# This is the Internal Representation to C code "Decompiler"

# Made into a class in case we want to make more than C code in the future 
import itertools

class IRToCDecompiler:
    def __init__(self, function, types, libraries, external_vars):
        self.function = function
        self.types = types
        self.libraries = libraries

        # These libraries are needed for platform independent code
        self.libraries.append("#include <stdint.h>")
        self.libraries.append("#include <stddef.h>")

        self.external_vars = external_vars


    # generate the full C code
    def generate_c_code(self):

        # Add libraries
        c_code = [lib for lib in self.libraries]

        # Start of Function, arguments, name
        # TODO: handle argument types
        input_vars = [f"{self.types[var]} var{var[1:]}" for var in self.function.input_variables]
        # split each input var by space, use handle_variables on the first part of the split and keep the second part the same

        input_vars = self.handle_input_vars(input_vars)

        c_code.append(f"void {self.function.name}({', '.join(input_vars)}) {{")

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
        #     print()

        for token in token_iter:
            if token == "if":
                if_block = self.handle_if_else(token_iter)
                for line in if_block:
                    c_code.append(line)
            elif token == "else":
                else_block = self.handle_if_else(token_iter, check_if=False)
                for line in else_block:
                    c_code.append(line)
            elif token == "return":
                # this doesn't seem right
                c_code.append("return;")
            else:
                c_code.append(self.handle_operations(token, token_iter))

        return c_code

    # Trying to handle more for if-else cases
    def handle_if_else(self, token_iter, check_if=True):
        def parse_block():
            block = []
            while True:
                token = next(token_iter, None)
                if token is None:
                    break

                if token == "}":
                    block.append(token)
                    break
                
                elif token == "if":
                    block.append(self.handle_if_else(token_iter))  
                elif token == "else":
                    block.append(token + next(token_iter))
                    block.append(parse_block())
                elif token == "return":
                    block.append(token + next(token_iter))
                else:
                    block.append(self.handle_operations(token, token_iter))

            for i in range(len(block)):
                if isinstance(block[i], list):
                    block[i] = ' '.join(block[i])
            return block

        # collect list of next tokens from  "(" to ")"
        if check_if:
            condition_list = []
            while True:
                token = next(token_iter, None)
                if token == ")":
                    condition_list.append(token)
                    break
                condition_list.append(token)

            if len(condition_list) > 3:
                condition = self.handle_operations(condition_list[0], iter(condition_list))
            else:
                condition = ' '.join(condition_list)
            # condition_var, _ = self.handle_variables(condition)
            if_block = ["if " + condition + next(token_iter)]

        if not check_if:
            if_block = ["else" + next(token_iter)]
        
        # for each in block, append new line to if_block as string
        parse_block = parse_block()
        string_block = ""
        for line in parse_block:
            string_block += f"\t{line}\n"
        if_block.append(string_block)
        
        return if_block

    def handle_operations(self, first_token, token_iter):

        left_var, left_var_type = self.handle_variables(first_token)
        operator = next(token_iter, None)
        # , - put together function arguments
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
                elif token == "access":
                    # var_name, _ = self.handle_operations(next(token_iter))
                    index = next(token_iter)
                    right_tokens.append(f"[{index}]")
                    
                else:
                    right_tokens.append(token)

            # if any right tokens contain "\n", replace with r"\n" (raw string literal)
            for i in range(len(right_tokens)):
                if "\n" in right_tokens[i]:
                    right_tokens[i] = right_tokens[i].replace("\n", r"\n")
                if "\t" in right_tokens[i]:
                    right_tokens[i] = right_tokens[i].replace("\t", r"\t")
            
            if left_var_type == "":
                return f"{left_var} = {' '.join(right_tokens)};"
            return f"{left_var_type} {left_var} = {''.join(right_tokens)};"
        
        elif operator == "+" or operator == "-" or operator == "%" or operator == "^" or operator == "&" or operator == "|" or operator == "*" or operator == "/" or operator == ">>" or operator == "<<":
            right_var = next(token_iter)
            right_var_name, _ = self.handle_variables(right_var)
            return f"{left_var} {operator}= {right_var_name};"
        
        elif operator == "<" or operator == ">" or operator == "==" or operator == "!=" or operator == "<=" or operator == ">=":
            right_var = next(token_iter)
            right_var_name, _ = self.handle_variables(right_var)

            return f"{left_var} = {left_var} {operator} {right_var_name};"

        elif operator == "access":
            index = next(token_iter)
            statement = f"{left_var}[{index}]"
            operator = next(token_iter)
            # append correctly handled tokens to statement
            while operator != ";":
                if operator == "access":
                    index = next(token_iter)
                    statement += f"[{index}]"
                elif operator == "=":
                    statement += " ="

                else:
                    assignment, _ = self.handle_variables(operator)
                    statement += f" {assignment}"
                
                operator = next(token_iter)

            statement += ";"

            return statement
            
        
        # ref & deref (pointers) -- will probably be more complex with testing
        elif operator == "ref":
            ref_var = next(token_iter)
            return f"{left_var} = &{ref_var};"
        
        elif operator == "deref":
            return f"{left_var} = *{next(token_iter)};"
        
        elif operator == "call":
            func_name, _ = self.handle_variables(next(token_iter))
            args = []
            while (arg := next(token_iter)) != ";":
                args.append(arg)
            return f"{left_var} = {func_name}({', '.join(args)});"

        
        # union/structs 
        # not sure how these will be structured for input
        elif operator == ".": 
            struct_var = next(token_iter)
            struct_var_name, _ = self.handle_variables(struct_var)
            return f"{left_var} = {struct_var_name}.{next(token_iter)};"

        # bitnot - bitwise not ~ (always has a 0 before it, where the 0 does not mean anything)
        elif operator == "bitnot":
            # remove the zero, I suppose. Also need to figure how how the bitnot will be structured
            return f"{left_var} = ~{next(token_iter)};"

        elif operator == "goto":
            return f"{operator} {next(token_iter)};"
        
        return ""  # TODO: Handle other cases  

    # Map an IR variable (e.g., #1) to a C variable name and type
    def handle_variables(self, var):
        var_name = f"var{var[1:]}"
        var_type = f"{self.types.get(var)}"
        # If var_type has i, f, or u, then it is an int, float, or unsigned
        if var_type.count("i") > 0:
            var_type = "int"
        elif var_type.count("f") > 0:
            var_type = "float"
        elif var_type.count("u") > 0:
            var_type = "unsigned int"
        else:
            var_type = ""

        return var_name, var_type

    # only some of the variable types
    def handle_input_vars(self, input_vars):
        converted_vars = []
        for var in input_vars:
            var_type = var.split(" ")[0]
            if var_type.count("i") > 0:
                var_type = "int"
            elif var_type.count("f") > 0:
                var_type = "float"
            elif var_type.count("u") > 0:
                var_type = "unsigned int"
            converted_vars.append(f"{var_type} {var.split(' ')[1]}")
            
        return converted_vars
