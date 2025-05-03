# This is the Internal Representation to C code "Decompiler"

from tokens import *


def get_type(toks:list[Token]):
    result = []

    for tok in toks:
        if tok == "#TYPE":
            result += tok.value
        elif tok in ["#STRUCT", "#UNION", "#ENUM"]:
            result += [f"{tok[1:].lower()} {tok.name}"]
        else:
            result.append(tok)

    return result


def handle_multiple_set(tokens):
    # handle x = y = z => y = z; x = y
    print("Handling...")
    i = 0
    n = len(tokens)
    while i < n:
        if i + 4 < n and TOKEN_VARIABLE() == tokens[i] and TOKEN_VARIABLE() == tokens[i+2] and TOKEN_VARIABLE() == tokens[i+4] and tokens[i+1] == "=" and tokens[i+3] == "=":
            print("found")
            new_stuff = tokens[i:i+3]
            del tokens[i]
            del tokens[i]
            i += 3
            tokens.insert(i, string_to_token(";"))
            i += 1
            tokens.insert_all(i, new_stuff)
            n = len(tokens)
        elif tokens[i] == "#FUNC":
            tokens[i].value = handle_multiple_set(tokens[i].value)
        i += 1
    return tokens

class IRToCDecompiler:
    def __init__(self):
        pass


    # generate the full C code
    def generate_c_code(self, tokens, libraries):
        c_code = ""
        for lib in libraries:
            c_code += f"#include \"{lib}\"\n"

        tokens = handle_multiple_set(tokens)

        print("After multiple sets")
        print(tokens)


        # handle type casts and refs
        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i] == "#FUNC":
                func = tokens[i].value
                j = 0
                m = len(func)
                while j < m:

                    if func[j] == "#TYPE" and j + 1 < m and func[j+1] == "cast":
                        func.insert(j, string_to_token("("))
                        j += 1
                        m += 1
                        func[j+1] = string_to_token(")")
                        new_tokens = get_type([func[j]])
                        del func[j]
                        m -= 1
                        for x in reversed(new_tokens):
                            func.insert(j, x)
                        m = len(func)
                    elif func[j] == "ref":
                        del func[j-1]
                        m -= 1
                        func[j].token = "*"
                    elif func[j] == "access":
                        func[j].token = "["
                        if func[j+1] == "(":
                            func.insert(j+4, Token("]", "", 0))
                        else:
                            func.insert(j+2, Token("]", "", 0))
                        m += 1
                    j += 1
            i += 1


        # handle structs, unions, and enums
        # handle the types of variables
        # convert names variables to real names
        used_already = set()

        new_tokens = Tokens([])
        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i] in ["#STRUCT", "#UNION", "#ENUM"]:
                new_tokens.tokens += [str(tokens[i])[1:].lower()] 
                if tokens[i].name is not None:
                    new_tokens.append(tokens[i].name)
                for tok in tokens[i].original_value:
                    if tok in ["#STRUCT", "#UNION", "#ENUM", "#TYPE"]:
                        new_tokens.tokens += get_type([tok])
                    else:
                        new_tokens.append(tok)
                new_tokens.append(";")
                new_tokens.append("\n")
            elif tokens[i] == "#FUNC":
                # handle functions
                new_tokens.tokens += tokens[i].return_type.value
                new_tokens.append(tokens[i].name)
                for arg in tokens[i].args:
                    if arg == "#TYPE":
                        new_tokens.tokens += arg.value
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
                            if hasattr(tok, "type") and tok.type is not None and len(tok.type) != 0 and not (len(tok.type) == 1 and tok.type[0] == ""):
                                new_tokens.tokens += get_type([tok.type])
                            else: 
                                print("NO TYPE")
                                # new_tokens.append(string_to_token("long"))
                        used_already.add(tok)
                        new_tokens.append("var" + tok[1:])
                    elif tok == "#FUNCCALL":
                        # handle call
                        tok.value[0] = tok.value[0].original
                        for j in range(1, len(tok.value)):
                            if TOKEN_VARIABLE() == tok.value[j]:
                                tok.value[j] = "var" + tok.value[j][1:]
                        new_tokens.tokens += tok.value
                    elif len(tok) > 0 and tok[0] == "@":
                        # handle labels
                        new_tokens.append("label_" + tok[1:])
                    elif tok == ":":
                        new_tokens[-1] += ":"
                        new_tokens.append("\n")
                    else:
                        new_tokens.append(tok)
            else:
                # normal token in global scope
                if TOKEN_VARIABLE() == tokens[i]:
                    if hasattr(tokens[i], "type") and tokens[i].type is not None and len(tokens[i].type) != 0:
                        the_type = get_type([tokens[i].type])
                        print(the_type)
                        if not(len(the_type) == 1 and the_type[0] == ""):
                            new_tokens.tokens += the_type
                    new_tokens.append("var" + tokens[i].token[1:])
                else:
                    new_tokens.append(tokens[i])

                        
            i += 1

        print("After struct, union, type")
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

        print("After comma separated")
        print(new_tokens)

        # handle tokens that have no type
        subsitutions = {}
        seen_already = set()

        type_tokens = set(["*", "int", "short", "signed", "unsigned", "float", "double", "long", "size_t", "ssize_t", "clock_t", "void", "char"])

        i = 0
        n = len(new_tokens)
        while i < n:
            print(new_tokens[i])
            if new_tokens[i][0:3] == "var":
                the_var = new_tokens[i]

                if new_tokens[i] in seen_already:
                    if new_tokens[i] in subsitutions:
                        # replace with the subsitutions
                        del new_tokens[i]
                        n -= 1
                        new_tokens.insert_all(i, subsitutions[the_var])
                        n = len(new_tokens)
                    else:
                        i += 1
                    continue

                if i > 0 and new_tokens[i-1] in type_tokens:
                    seen_already.add(new_tokens[i])
                    i += 1
                    continue

                seen_already.add(new_tokens[i])

                del new_tokens[i]
                n -= 1

                if new_tokens[i] == "=":
                    endline = new_tokens.get_line_end(i)
                    sub = new_tokens[i+1:endline]
                    for j in range(i, endline):
                        del new_tokens[i]
                        n -= 1

                    subsitutions[the_var] = sub
                    print(f"Added substitution: {the_var} -> {sub}")

            i += 1


        print("New Tokens:")
        print(new_tokens)

        i = 0
        n = len(new_tokens)
        while i < n:
            if new_tokens[i] == ";":
                new_tokens.insert(i+1, "\n")
                n += 1
            i += 1

        c_code += " ".join([str(x) for x in new_tokens])


        return c_code
    
    



