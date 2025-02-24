from decompiler import IRToCDecompiler

# based on this test case that was passed through the compiler. 
# struct TestStruct {
#     int a;
# };

# int main(int argc, char** argv){
#     struct TestStruct *test;
#     struct TestStruct test2;

#     int a = (unsigned int) -7;
#     return 0;
# }

# resulting token from compiler: 
# [$STRUCTURE_DEFINITION, ;, Function main -> void

# arguments:
# ['*i32:Constraint: []']

# Tokens: [#4, ;, #5, ;, #8, =, 0, -, 7, ;, #9, =, #8, ;, #6, =, #9, ;, #7, =, 0, ;, #10, access, 0, =, #7, ;, return, ;]
# ]




class Function:
    def __init__(self, name:str, input_variables:list[str], tokens:list[str]):
        self.name = name
        self.input_variables = input_variables
        self.tokens = tokens

# STRUCT TEST CASE # 
print("\nUNION/STRUCT TEST\n")


TEST_INCLUDED_LIBRARIES = ["#include <stdio.h>"]
TEST_EXTERNAL_VARIABLES = {"#3":"printf"}

TEST_STRUCT_TYPES = {
    "#4": "struct TestStruct*",  # Pointer to struct
    "#5": "struct TestStruct",   # Regular struct
    "#6": "u32",                 # Unsigned integer
    "#7": "i32",                 # Integer variable
    "#8": "i32",                 # Integer variable
    "#9": "u32",                 # Unsigned integer assignment
    "#10": "struct TestStruct"    # Struct variable access
}

TEST_NAME = "test_struct"
TEST_INPUT_VARIABLES = ["#1", "#2"]  # argc, argv 


TEST_STRUCT_TOKENS = [
    "#4", ";",   # struct TestStruct *test;
    "#5", ";",   # struct TestStruct test2;
    "#8", "=", "0", "-", "7", ";",  # int a = (unsigned int) -7;
    "#9", "=", "#8", ";",
    "#6", "=", "#9", ";",
    "#7", "=", "0", ";",
    "#10", "access", "0", "=", "#7", ";",
    "return", ";"
]


TEST_STRUCT_FUNCTION = Function(TEST_NAME, TEST_INPUT_VARIABLES, TEST_STRUCT_TOKENS)

COMPILED_STRUCT_CODE = IRToCDecompiler(TEST_STRUCT_FUNCTION, TEST_STRUCT_TYPES, TEST_INCLUDED_LIBRARIES, TEST_EXTERNAL_VARIABLES).generate_c_code()
print(COMPILED_STRUCT_CODE)