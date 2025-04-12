# This is the Internal Representation to C code "Decompiler"

from tokens import *


def get_type(toks:list[Token]):
    result = []
    print(f"GETTYPE: {toks}")

    for tok in toks:
        if tok == "#TYPE":
            result += tok.value
        elif tok in ["#STRUCT", "#UNION", "#ENUM"]:
            result += [f"{tok[1:].lower()} {tok.name}"]
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
                new_tokens.append(";")
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
                            if hasattr(tok, "type"):
                                new_tokens += get_type([tok.type])
                        used_already.add(tok)
                        new_tokens.append("var" + tok[1:])
                    elif tok == "access":
                        # handle access
                        new_tokens.append("[")
                        new_tokens.append("0")
                        new_tokens.append("]")
                        continues = 1
                        continue
                    elif tok == "#FUNCCALL":
                        # handle call
                        tok.value[0] = tok.value[0].original
                        for j in range(1, len(tok.value)):
                            if TOKEN_VARIABLE() == tok.value[j]:
                                tok.value[j] = "var" + tok.value[j][1:]
                        new_tokens += tok.value
                    elif len(tok) > 0 and tok[0] == "@":
                        # handle labels
                        new_tokens.append("label_" + tok[1:])
                    elif tok == ":":
                        new_tokens[-1] += ":"
                        new_tokens.append("\n")
                    else:
                        new_tokens.append(tok)
                        
            i += 1

        print(new_tokens)

        # handle comma separated tokens
        i = len(new_tokens)-1
        while i-3 >= 0:
            if new_tokens[i] == "," and new_tokens[i-2] == "=":
                # replace all occurances of i-3 with i-1,i+1
                replacement = [new_tokens[i-1], ",", new_tokens[i+1]]
                search_term = new_tokens[i-3]

                del new_tokens[i-3]
                del new_tokens[i-3]
                del new_tokens[i-3]
                del new_tokens[i-3]
                del new_tokens[i-3]
                del new_tokens[i-3]
                i -= 3

                print(f"Search: {search_term}\tReplace: {replacement}")
                j = i
                while j < len(new_tokens):
                    if new_tokens[j] == search_term:
                        del new_tokens[j]
                        for x in reversed(replacement):
                            new_tokens.insert(j, x)
                    j += 1

                continue
            i -= 1

        print("New Tokens:")
        print(new_tokens)

        c_code += " ".join([str(x) for x in new_tokens])


        return c_code
    
    



