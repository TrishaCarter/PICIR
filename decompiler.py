# This is the Internal Representation to C code "Decompiler"

# Made into a class in case we want to make more than C code in the future
# It would probably be better to make this a class anyway for organization anyway. 

# TODO: call and access
# TODO: variable initialization

class IRToCDecompiler:
    def __init__(self, function, types, libraries, external_vars):
        self.function = function
        self.types = types
        self.libraries = libraries
        self.external_vars = external_vars

    # generate the full C code
    # TODO: see if it would be better to return a file instead of console output
    # more than likely should, but I will see what is easier for debugging, demonstration, etc.
    def generate_c_code(self):
        # Add libraries
        c_code = [lib for lib in self.libraries]

        # Start of Function, arguments, name
        # TODO: handle argument types
        input_vars = [f"{self.types[var]} var{var[1:]}" for var in self.function.input_variables]
        # split each input var by space, use handle_variables on the first part of the split and keep the second part the same
        for var in input_vars:
            var.split(" ")
            _, var_type = self.handle_variables(var[0])
            var = f"{var_type} {var[1]}"

        c_code.append(f"void {self.function.name}({','.join(input_vars)}) {{")

        # Translate tokens to C statements
        body_code = self.handle_tokens()
        c_code.extend(f"    {line}" for line in body_code) # Indent the body code

        # Close function
        c_code.append("}")

        return "\n".join(c_code)
    
    def handle_tokens(self):
        c_code = []
        token_iter = iter(self.function.tokens)
        # for token in token_iter:
        #     print(token)

        for token in token_iter:
            # TODO: "\n" and "\t" are not handlesd correctly
            if token == "if":
                if_block = self.handle_if_else(token_iter)
                for line in if_block:
                    c_code.append(line)
            
            elif token == "return":
                # this doesn't seem right
                c_code.append("return;")
            else:
                c_code.append(self.handle_operations(token, token_iter))

        return c_code

    def handle_if_else(self, token_iter):
        block = ["if " + next(token_iter)]
        condition = next(token_iter)  # This is assuming a single variable/literal (item)
        condition_var, _ = self.handle_variables(condition)
        block[0] += condition_var + next(token_iter) + next(token_iter)

        while True:

            token = next(token_iter, None)
            if token is None:
                break
            if token == "else":
                block.append(token + next(token_iter))
                #TODO: Handle anything actually in the else block
            elif token == "}":
                block.append(token)
                break
            else:
                block.append(self.handle_operations(token, token_iter))

        return block
    
    def handle_operations(self, first_token, token_iter):
        left_var, left_var_type = self.handle_variables(first_token)
        operator = next(token_iter)

        # bitnot - bitwise not ~ (always has a 0 before it, where the 0 does not mean anything)
        # ref - reference of & (always has a 0 before it, where the 0 does not mean anything)
        # . - structure/union access - probably wait for this one (will be difficult)
        # call - make function call (variable before is the function's identifier. 
        #                             variable after is all of the arguments that have been put together using the , operator)
        # access - array access - ( #2 access 3  =>  #2[3] )

        # , - put together function arguments
        # goto - jump to label
        # @x followed by : - define a label

        # = - set equal to
        if operator == "=":
            right_tokens = []
            while True:
                token = next(token_iter)
                if token == ";":
                    break
                elif token.startswith("#"):
                    var_name, _ = self.handle_variables(token)
                    right_tokens.append(var_name)
                else:
                    right_tokens.append(token)
            if left_var_type == "":
                return f"{left_var} = {' '.join(right_tokens)};"
            return f"{left_var_type} {left_var} = {' '.join(right_tokens)};"
        
        elif operator == "+" or operator == "-" or operator == "%" or operator == "^" or operator == "&" or operator == "|" or operator == "*" or operator == "/" or operator == ">>" or operator == "<<":
            right_var = next(token_iter)
            right_var_name, _ = self.handle_variables(right_var)
            return f"{left_var} {operator}= {right_var_name};"
        
        elif operator == "<" or operator == ">" or operator == "==" or operator == "!=" or operator == "<=" or operator == ">=":
            right_var = next(token_iter)
            right_var_name, _ = self.handle_variables(right_var)

            return f"{left_var} = {left_var} {operator} {right_var_name};"
        
        return ""  # TODO: Handle other cases  

    # Map an IR variable (e.g., #1) to a C variable name and type
    def handle_variables(self, var):
        var_name = f"var{var[1:]}"
        var_type = f"{self.types.get(var)}"
        # If var_type has i, f, or u, then it is an int, float, or unsigne
        if var_type.count("i") > 0:
            var_type = "int"
        elif var_type.count("f") > 0:
            var_type = "float"
        elif var_type.count("u") > 0:
            var_type = "unsigned int"
        else:
            var_type = ""

        return var_name, var_type
