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




# # write the modified code to the output file specified by the user in the terminal 
# def write_modified_code(output_path, modified_code):
#     with open(output_path, 'w') as file:
#         file.write(modified_code)

# # main function to extract for loops from the input file and write the modified code to the output file
# def main():
#     if len(sys.argv) < 3:
#         print("Usage: python for_loop_finder.py <input_file.c> <output_file.c>")
#         sys.exit(1)
    
#     input_file = sys.argv[1] # c source file 
#     output_file = sys.argv[2] # output file to write the modified code to 
    
#     for_loops, modified_code = extract_for_loops(input_file)
    
#     print("Extracted for loops:")
#     for loop in for_loops:
#         print("For loop contents:")
#         print(loop, "\n")
    
#     write_modified_code(output_file, modified_code)
#     print(f"Modified C file saved to {output_file}")

# if __name__ == "__main__":
#     main()
