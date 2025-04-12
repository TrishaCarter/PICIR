# This is the Internal Representation to C code "Decompiler"

from tokens import *


def get_type(toks:list[Token]):
    result = []
    print(f"GETTYPE: {toks}")

    for tok in toks:
        if tok == "#TYPE":
            result += tok.value
        elif tok in ["#STRUCT", "#UNION", "#ENUM"]:
            result += get_type([tok.value])
        else:
            result.append(tok)

    return result



class IRToCDecompiler:
    def __init__(self):
        pass

    # generate the full C code
    def generate_c_code(self, tokens, libraries):
        c_code = ""
        for lib in libraries:
            c_code += f"#include \"{lib}\"\n"

        # handle structs, unions, and enums
        # handle the types of variables
        # convert names variables to real names
        used_already = set()

        new_tokens = []
        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i] in ["#STRUCT", "#UNION", "#ENUM"]:
                new_tokens += [str(tokens[i])[1:].lower()] 
                if tokens[i].name is not None:
                    new_tokens.append(tokens[i].name)
                for tok in tokens[i].original_value:
                    if tok in ["#STRUCT", "#UNION", "#ENUM", "#TYPE"]:
                        new_tokens += get_type([tok])
                    else:
                        new_tokens.append(tok)
                new_tokens.append("\n")
            elif tokens[i] == "#FUNC":
                # handle functions
                new_tokens += tokens[i].return_type.value
                new_tokens.append(tokens[i].name)
                for arg in tokens[i].args:
                    if arg == "#TYPE":
                        new_tokens += arg.value
                    elif TOKEN_VARIABLE() == arg:
                        used_already.add(arg)
                        new_tokens.append("var" + arg[1:])
                    else:
                        new_tokens.append(arg)
                continues = 0
                for j, tok in enumerate(tokens[i].value):
                    if continues:
                        continues -= 1
                        continue

                    # handle .
                    if tok == ".":
                        new_tokens[-1] += "."
                        new_tokens[-1] += tokens[i].value[j+1].original
                        continues = 1
                        continue
                    elif TOKEN_VARIABLE() == tok:
                        if tok not in used_already:
                            # TODO: fix this to use actual type
                            new_tokens.append("int")
                        used_already.add(tok)
                        new_tokens.append("var" + tok[1:])
                    elif tok == "access":
                        # handle access
                        new_tokens.append("[")
                        new_tokens.append("0")
                        new_tokens.append("]")
                        continues = 1
                        continue
                    else:
                        new_tokens.append(tok)
                        
                    # TODO: handle call
            i += 1

        print("New Tokens:")
        print(new_tokens)

        c_code += " ".join([str(x) for x in new_tokens])


        return c_code
    
    



