import re

# function to extract for-loop contents from tokenized input
def extract_for_loops(tokens):
    for_loops = []
    modified_tokens = tokens[:]  # create a copy of tokens to modify

    i = 0
    n = len(tokens)

    print("Scanning tokens for 'for' loops...")  # debug

    while i < n:
        if tokens[i] == "for":
            start_idx = i
            loop_condition = []

            # collect everything inside ( ... ) after 'for'
            i += 1
            if tokens[i] == "(":
                brace_count = 1
                loop_condition.append(tokens[i])
                i += 1
                while i < n and brace_count > 0:
                    loop_condition.append(tokens[i])
                    if tokens[i] == "(":
                        brace_count += 1
                    elif tokens[i] == ")":
                        brace_count -= 1
                    i += 1

            # collect loop body (inside `{ ... }`)
            if i < n and tokens[i] == "{":
                loop_body = []
                brace_count = 1
                loop_body.append(tokens[i])
                i += 1
                while i < n and brace_count > 0:
                    loop_body.append(tokens[i])
                    if tokens[i] == "{":
                        brace_count += 1
                    elif tokens[i] == "}":
                        brace_count -= 1
                    i += 1

                # store extracted loop (excluding 'for')
                full_loop_content = loop_condition + loop_body
                for_loops.append(full_loop_content)

                # debug output
                print(f"Extracted loop: {full_loop_content}")

                # replace the loop with a placeholder
                modified_tokens[start_idx:i] = ["/* Removed for-loop */"]

        else:
            i += 1

    return for_loops, modified_tokens  # return extracted loops and modified token list
