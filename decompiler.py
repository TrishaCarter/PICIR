# This is the Internal Representation to C code "Decompiler"

# Made into a class in case we want to make more than C code in the future 
 
# TODO: Pointer Arithmetic?
# TODO: implementing unions & structs - maybe depending on cuda

IS_MAIN = False

class IRToCDecompiler:
    def __init__(self, function, types, libraries, external_vars):
        self.function = function
        self.types = types
        self.libraries = libraries
        self.external_vars = external_vars

        # These libraries are needed for platform independent code
        self.libraries.append("#include <stdint.h>")
        # self.libraries.append("#include <stddef.h>")
        # self.libraries.append("#include <stdbool.h>")
        # self.libraries.append("#include <float.h>")

    # generate the full C code
    def generate_c_code(self):

        # Add libraries
        c_code = [lib for lib in self.libraries]
        c_code.append("")

        # Start of function, arguments, name, and return type
        input_vars = [var for var in self.function.input_variables]
        converted_vars = []
        for var in input_vars:
            if var.count("arg") > 0:
                if var.count("argc")> 0:
                    converted_vars.append("int argc")
                    input_vars.remove(var)
                elif var.count("argv") > 0:
                    converted_vars.append("char **argv")
                    input_vars.remove(var)
                continue

            var_name, var_type = self.handle_variables(var)
            converted_vars.append(f"{var_type} {var_name}")

        function_name = f'{self.function.name}'

        if function_name == "main":
            IS_MAIN = True
            c_code.append(f"int {function_name}({', '.join(converted_vars)}) {{")

        else:
            c_code.append(f"void {self.function.name}({', '.join(converted_vars)}) {{")

        # Translate tokens to C statements
        body_code = self.handle_tokens()
        c_code.extend(f"    {line}" for line in body_code) # Indent the body code

        # Close function
        c_code.append("}")

        c_code = "\n".join(c_code)

        # for handling print statements and anything else post translation
        c_code = self.handle_post_translation(c_code)

        return c_code
    
    def handle_tokens(self):
        c_code = []
        
        token_iter = iter(self.function.tokens)

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
                return_statement = "return"

                # until token ";" is found, append to return statement 
                while True:
                    return_token = next(token_iter, None)
                    if return_token == ";":
                        return_statement += f"{return_token}"
                        break
                    return_statement += f" {return_token}"
                c_code.append(return_statement)
            
            else:
                c_code.append(self.handle_operations(token, token_iter))
                

        return c_code

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
                    return_tokens = "return"
                    while True:
                        next_token = next(token_iter, None)
                        if next_token == ";":
                            return_tokens += f"{next_token}"
                            break
                        else:
                            return_tokens += f" {next_token}"
                    block.append(return_tokens)
                else:
                    block.append(self.handle_operations(token, token_iter))

            for i in range(len(block)):            
                if isinstance(block[i], list):
                    block[i] = ' '.join(block[i])
            return block

        # collect list of next tokens from  "(" to ")"
        if check_if:
            condition = self.handle_variables(next(token_iter, None))[0]
            # There are not parantheses now?
            # condition_list = []
            # while True:
            #     token = next(token_iter, None)
            #     if token == ")":
            #         condition_list.append(token)
            #         break
            #     condition_list.append(token)

            # if len(condition_list) > 3:
            #     condition = self.handle_operations(condition_list[0], iter(condition_list))
            # else:
            #     variable = condition_list[1]
            #     condition_list[1] = self.handle_variables(variable)[0]
            #     condition = ' '.join(condition_list)
            
            if_block = ["if (" + condition  + ")"  + next(token_iter)]

        if not check_if:
            # string_block = "else"
            if_block = ["else" + next(token_iter)]
            # if next(token_iter) == "}":
            #     if_block  = []
            # else:
            #     if_block.append(next(token_iter))
            # print("if_block "+str(if_block))
        
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
        
        # labels
        elif operator == ":":
        
            return f"{left_var}{operator}" + " {}"
        
        elif operator == ";":
            return f"{left_var_type} {left_var}{operator}"
        
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
                if operator == "=":
                    statement += " ="

                else:
                    # handle if right side has access or just variable
                    if operator.startswith("#"):
                        var_name, _ = self.handle_variables(operator)
                        statement += f" {var_name}"    
                
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
            func_name = self.external_vars.get(first_token)
            args = []
            while (arg := next(token_iter)) != ";":
                arg_name, _ = self.handle_variables(arg)
                args.append(arg_name)
            return f"{func_name}({', '.join(args)});"
        
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
        
        # elif operator.count("@") > 0:
        #     label, _ = self.handle_variables(operator)
        #     return f"{label}:"

        elif first_token == "goto":
            label, _ = self.handle_variables(operator)
            return f"{first_token} {label}{next(token_iter)}"
        
        else:
            return ""

    # Map an IR variable (e.g., #1) to a C variable name and type
    def handle_variables(self, var):
        var_name = f"var{var[1:]}"
        # print(var)
        var_type = f"{self.types.get(var)}"
        return_var_type = ""

        # Parse Data Types
        if var_type.count("i") > 0:
            return_var_type += "int"
            if var_type.count("*") > 0:
                return_var_type += "ptr"
            else:
                if var_type.count("8") > 0:
                    return_var_type += "8"
                elif var_type.count("16") > 0:
                    return_var_type += "16"
                elif var_type.count("32") > 0:
                    return_var_type += "32"
                else:
                    return_var_type += "64"

            return_var_type+= "_t"

        elif var_type.count("f") > 0:
            var_type = "float"
            if var_type.count("32") > 0:
                return_var_type += "32"
            else:
                return_var_type += "64"

            return_var_type+= "_t"

        elif var_type.count("u") > 0:
            return_var_type += "uint"
            if var_type.count("*") > 0:
                return_var_type += "ptr"
            else:
                if var_type.count("8") > 0:
                    return_var_type += "8"
                elif var_type.count("16") > 0:
                    return_var_type += "16"
                elif var_type.count("32") > 0:
                    return_var_type += "32"
                else:
                    return_var_type += "64"

            return_var_type+= "_t"

        else:
            return_var_type = ""

        
        if return_var_type.count("ptr") > 0:
            # add * after _t
            return_var_type = return_var_type[:return_var_type.index("_t")+2] + "*" + return_var_type[return_var_type.index("_t")+2:]
        return var_name, return_var_type
    
    def handle_post_translation(self, code):
    # go through the code to replace function calls with their respective function names
        code = code.split("\n")


        for i in range(len(code)-5):
            # store names of variables assigned strings and replace any calls of that name with printf
            if code[i].count('else{') > 0 and code[i+1].count('}') > 0:

                # remove this and next two indexes
                code.pop(i+2)
                code.pop(i+1)
                code.pop(i)
            
            if '"' in code[i]:
                # dont come for me for this please, if I think of a better way I will change it
                # remove leading whitespace, but also store the whitespace to add back later
                white_space = code[i][:code[i].index(code[i].lstrip())]
                line = code[i].lstrip()

                # name of variable is in between first space and next space
                if "=" in line:
                    name = f"{line[line.index(' '):line.index(' ', line.index('=')-1)]}".strip()
                    # replace 'line' up to first space with const char*
                    code[i] = white_space + 'const char*' + line[line.index(' '):]
                
        # put it back together
        return "\n".join(code)
