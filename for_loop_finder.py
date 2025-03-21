

# TODO: make sure the loop does not modify the condition variables and no continues, breaks, or goto allowed
# TODO: make it take in a list of tokens instead of a file path so that it can be used in cuda.py 

import re
import sys

# function to extract the content inside 'for' loops from the input file (c source file)
def extract_for_loops(file_path):
    with open(file_path, 'r') as file:
        code = file.read()
    
    for_loops = [] # list to store the extracted content inside 'for' loops 
    modified_code = code # copy of the original code to remove the 'for' loops 
    
    # regular expression to match 'for' loops
    for_loop_pattern = re.compile(r'for\s*(\(.*?\))\s*\{', re.DOTALL)
    
    matches = list(for_loop_pattern.finditer(code)) # find all 'for' loops in the code 
    
    print("Found for loops in the code:") # debug statement 
    
    for match in reversed(matches):  # process from last to first to avoid shifting indices
        loop_condition = match.group(1)  # capture condition part inside parentheses
        start_idx = match.end()  # start after 'for (...) {'
        brace_count = 1 # count of open braces 
        end_idx = start_idx # end index of the loop 
        
        # find the matching closing brace
        for i in range(start_idx, len(code)): 
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        loop_body = code[start_idx:end_idx] # extract the content inside the 'for' loop 
        full_loop_content = loop_condition + loop_body # full content inside the 'for' loop 
        tokenized_loop = re.findall(r'\w+|[^\w\s]', full_loop_content) # tokenize the content inside the 'for' loop 
        
        for_loops.append(tokenized_loop) # add the tokenized content to the list 
        print("For loop contents:")
        print(f"tokenized loop: {tokenized_loop}")  # debug statement
        print(f"loop_body: {loop_body}")  # debug statement
        print(f"loop_condition: {loop_condition}")  # debug statement
        
        # Remove the for loop from the original code
        modified_code = modified_code[:match.start()] + "/* Removed for-loop */" + modified_code[end_idx:]
    
    return for_loops, modified_code

# write the modified code to the output file specified by the user in the terminal 
def write_modified_code(output_path, modified_code):
    with open(output_path, 'w') as file:
        file.write(modified_code)

# main function to extract for loops from the input file and write the modified code to the output file
def main():
    if len(sys.argv) < 3:
        print("Usage: python for_loop_finder.py <input_file.c> <output_file.c>")
        sys.exit(1)
    
    input_file = sys.argv[1] # c source file 
    output_file = sys.argv[2] # output file to write the modified code to 
    
    for_loops, modified_code = extract_for_loops(input_file)
    
    print("Extracted for loops:")
    for loop in for_loops:
        print("For loop contents:")
        print(loop, "\n")
    
    write_modified_code(output_file, modified_code)
    print(f"Modified C file saved to {output_file}")

if __name__ == "__main__":
    main()
