
from debug import *
from token import *

class Lexer:

    def __init__(self, filename:str):
        self.filename = filename

        # open the file and get its data as a string
        self.file_data: str = self.open_file(self.filename)

        # break the string into Tokens
        self.tokens = self.tokenize(self.file_data)

        # combine postfix and prefix operators while there are still spaces
        self.tokens = self.combine_prefix_and_postfix(self.tokens)



    def open_file(self, filename:str) -> str:
        dbg(f"Opening file {filename}...")
        try:
            f = open(filename, 'r')
        except:
            panic(f"Unable to open file ({filename})")

        dbg(f"File read successfully!")
        return f.read()


    def tokenize(self, file_data:str) -> list[Token]:
        i = 0
        n = len(file_data)

        # characters that cause a token break
        breakChars = {"~", "!", "#", "%", "^", "&", "*", "(", ")", "-", "+", "=", "{", "}", "[", "]", "|", '\\', "'", '"', ';', ":", "/", "?", ".", ",", "<", ">", '\n', '\t', ' '}

        result = []
        line_number = 1
        current_token = ""

        while i < n:

            if file_data[i] in breakChars:
                if file_data[i] == "\n":
                    line_number += 1

                if len(current_token) > 0:
                    result.append(Token(current_token, line_number, ""))

                result.append(Token(file_data[i], line_number, ""))

                current_token = ""
            else:
                current_token += file_data[i]

            i += 1


        for token in result:
            token.filename = self.filename

        return result


    def combine_prefix_and_postfix(self, tokens):
        """
        Combine ++ and -- into single tokens while spaces are still here
        """

        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i].token not in ["+", "-"]:
                i += 1
                continue

            if i + 1 >= n:
                break

            if tokens[i].token != tokens[i+1].token:
                i += 1
                continue

            tokens[i].token += tokens[i+1].token
            del tokens[i+1]
            n -= 1
            i += 1

        return tokens





