# This is the Internal Representation to C code "Decompiler"

# Made into a class in case we want to make more than C code in the future
# It would probably be better to make this a class anyway for organization anyway. 

# TODO: call and access are being ignored for now

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
        input_vars = [f"{self.types[var]} var{var[1:]}" for var in self.function.input_variables]
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
            if token == "if":
                if_block = self.handle_if_else(token_iter)
                for line in if_block:
                    c_code.append(line)
            elif token == "return":
                c_code.append("return;")
            else:
                c_code.append(self.handle_operations(token, token_iter))

        return c_code

    def handle_if_else(self, token_iter):
        block = ["if " + next(token_iter)]
        condition = next(token_iter)  # This is assuming a single variable/literal (item)
        condition_var, _ = self.handle_variables(condition)
        block.append(condition_var + next(token_iter) + next(token_iter))

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
        left_var, _ = self.handle_variables(first_token)
        operator = next(token_iter)

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

            return f"{left_var} = {' '.join(right_tokens)};"

        return ""  # TODO: Handle other cases  

    # Map an IR variable (e.g., #1) to a C variable name and type
    def handle_variables(self, var):
        var_name = f"var{var[1:]}"
        var_type = self.types.get(var, "int")  # Default to int if type is unknown
        return var_name, var_type
