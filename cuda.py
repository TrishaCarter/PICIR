
import lexer
import normalizer


"""
Cuda process:
0. Accept C source file
1. Find Main Function
2. Look for 'for' loop and get contents
    * loop cannot modify the condition variables
    * no continues, breaks, or jumps allowed
    * check for data dependencies
3. Get a list of everything that needs to be allocated for the gpu
4. Replace the for loop with allocation, copying, invocation, copying, and deallocation
5. Create device function
"""




if __name__ == '__main__':
    lex = lexer.Lexer("testing.c")
    tokens = lex.tokens
    the_normalizer = normalizer.Normalizer(tokens)
    tokens = the_normalizer.tokens

    print(tokens)

    contents = []

    # find the main function
    i = 0
    n = len(tokens)
    while i < n:
        if tokens[i] == "main":
            print("Found main function")

            while i < n:
                if tokens[i] == "{":
                    break
                i += 1

            braces = 0
            while i < n:
                contents.append(tokens[i])
                if tokens[i] == "{":
                    braces += 1
                elif tokens[i] == "}":
                    braces -= 1
                    if braces == 0:
                        break
                i += 1

            break
        i += 1

    print("Main function contents")
    print(contents)


    # find eligible for loops
            

