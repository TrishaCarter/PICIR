from decompiler import IRToCDecompiler
"""
You will be given a function object that needs to be converted to C.
By giving this program every function in the representation, it should be able to rebuild the program.

You may assume at this point:
    All types are correct
    All accesses are valid (they are done on a pointer with enough space for the access)
    All External Libraries and External Variables are real and have the given type
    Every statement will end with a ; (except for starting if/else statements)
    Every statement will have at most 1 operation (not including the equal sign)
        Although the operation may be to the left of the equal sign
        There is not guarantee that a line has an equal sign
    There will be exactly one term inside of if statements (can be a variable or literal)
    Every if statement will have an else clause (even if it will be empty)
    Any token whose first character is ' is a character literal
    Any token whose first character is " is a string literal
    int and float literals are just numbers (floats have decimals) without # in front of them
    #x represents a variable where x is its number (used to index the TEST_TYPES dictionary
    The function should return void, meaning the return keyword should never return a value
    All functions, variables, and identifiers have been turned into variables


Remaining Tokens:
    bitnot, ref, %, ^, &, |, -, +, <, >, *, /, ==, ., call, access, >>, <<, =, ,,
    {, }, ;
    if, else
    return
    goto, @x, #x, :
    <char, int, float, and string literals>


bitnot - bitwise not ~ (always has a 0 before it, where the 0 does not mean anything)
ref - reference of & (always has a 0 before it, where the 0 does not mean anything)
% - modulus
^ - xor
& - bitwise and
| - bitwise or
- - subtraction
+ - addition
< - less than
> - greater than
* - multiplication
/ - division
== - equality operator
. - structure/union access - probably wait for this one (will be difficult)
call - make function call (variable before is the function's identifier. 
                            variable after is all of the arguments that have been put together using the , operator)
access - array access - ( #2 access 3  =>  #2[3] )
>> - right shift
<< - left shift
= - set equal to
, - put together function arguments
goto - jump to label
@x followed by : - define a label


"""

class Function:
    def __init__(self, name:str, input_variables:list[str], tokens:list[str]):
        self.name = name
        self.input_variables = input_variables
        self.tokens = tokens

# external functions will be identified
TEST_INCLUDED_LIBRARIES = ["#include <stdio.h>"]
TEST_EXTERNAL_VARIABLES = {"#3":"printf"}

# * can come after types to show that it is a pointer
TEST_TYPES = {
        "#1":"i32",
        "#2":"u8**", # there can be any number of *'s
        "#3":"i32", # external function types are shown as their return type
        "#4":"i32",
        "#5":"i32",
        "#6":"i32",
        "#7":"i32",
        "#8":"i32",
        "#9":"i32",
        "#10":"u8*",
        "#11":"i32",
        "#12":"i32",
        "#13":"i32*",
    }
"""
u - represents unsigned integer
i - represents signed integer
f - represents float
number after - represents number of bits

Possible (primitive) types:
    u8
    u16
    u32
    u64

    i8
    i16
    i32
    i64

    f32
    f64

    along with any number of * after them
    can deal with structures and unions later

"""

TEST_NAME = "main"
TEST_INPUT_VARIABLES = ["#13", "#1", "#2"]
TEST_TOKENS = [
        "#7", "=", "#1", "<", "2", ";", 
        "if", "(", "#7", ")", "{", 
            "#10", "=", '"HELLO, WORLD!\n"', ";", 
            "#3", "call", "#10", ";", 
            "#11", "=", "10", "*", "3", ";", 
            "#12", "=", "#11", "-", "2", ";", 
            "#8", "=", "#12", ";", 
            "#13", "access", "1", "=", "#8", "access", "0", ";", 
            "return", ";",
        "}", "else", "{", "}", 
        "#4", "=", "2", ";", 
        "#5", "=", "3", ";", 
        "#6", "=", "#4", "<<", "#5", ";", 
        "#9", "=", "#6", ";", 
        "#13", "access", "0", "=", "#9", ";",
        "return", ";"
    ]


TEST_FUNCTION = Function(TEST_NAME, TEST_INPUT_VARIABLES, TEST_TOKENS)
# make new line after ; and { when printing test_tokens
for token in TEST_TOKENS:
    print(token, end=" ")
    if token == ";" or token == "{":
        print()
    

COMPILED_CODE = IRToCDecompiler(TEST_FUNCTION, TEST_TYPES, TEST_INCLUDED_LIBRARIES, TEST_EXTERNAL_VARIABLES).generate_c_code()
print(COMPILED_CODE)