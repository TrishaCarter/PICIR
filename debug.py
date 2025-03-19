
from token import *

DEBUG = 1
ERRORS = []

def dbg(message:str):
    if DEBUG:
        print(message)

def panic(message:str):
    print(message)
    exit(1)

def error(token:Token, message:str):
    result = f"Error: {token.filename}:{token.line_number} at token {token.token}\n\t{message}"
    ERRORS.append(result)

def print_errors():
    dbg(f"{len(ERRORS)} NON-FATAL ERRORS ENCOUNTERED")
    [print(err) for err in ERRORS]

def fatal_error(token:Token, message:str):
    print_errors()

    print(f"Fatal Error: {token.filename}:{token.line_number} at token {token.token}")
    print(f"\t{message}")

    print("Encountered fatal error... exiting!")
    exit(1)





