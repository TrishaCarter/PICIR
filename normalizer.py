
from debug import *
from token import *


class Normalizer:
    def __init__(self, tokens:list[Token]):
        self.tokens = tokens

        # remove comments and multi-line comments that are not in string
        self.tokens = self.remove_comments(self.tokens)
        
        # check compiler directive syntax
        self.tokens = self.check_directive_syntax(self.tokens)

        # combine strings into single tokens and remove whitespace
        self.tokens = self.combine_strings(self.tokens)

        # combine floats into single tokens
        self.tokens = self.combine_floats(self.tokens)

        # remove auto and register keywords
        self.tokens = self.remove_auto_and_register(self.tokens)


    def remove_auto_and_register(self, tokens):
        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i] == "auto" or tokens[i] == "register" or tokens[i] == "volatile":
                del tokens[i]
                n -= 1
                i -= 1
            i += 1
        return tokens

        
    def remove_comments(self, tokens:list[Token]) -> list[Token]:
        dbg("Removing Comments From The Tokens...")

        result = []

        comment = False
        multi_line = False
        quotes = False
        char_quote = False

        i = 0
        n = len(tokens)
        while i < n:

            if tokens[i] == '/':
                if comment and multi_line:
                    if i and tokens[i-1] == "*":
                        comment = False
                        multi_line = False
                        i += 1
                        continue

                if i + 1 < n:
                    if not comment and not quotes:
                        if tokens[i+1] == '/':
                            comment = True
                            multi_line = False
                        elif tokens[i+1] == '*':
                            comment = True
                            multi_line = True

            elif tokens[i] == '"':
                if not quotes and not char_quote:
                    quotes = True
                elif quotes and not char_quote:
                    backslashes = self.get_backslashes_before(tokens, i)
                    if backslashes % 2 == 0:
                        quotes = False
            elif tokens[i] == "'":
                if not quotes and not char_quote:
                    char_quote = True
                elif not quotes and char_quote:
                    backslashes = self.get_backslashes_before(tokens, i)
                    if backslashes % 2 == 0:
                        char_quote = False

            # keeping track of newlines
            elif tokens[i] == '\n':
                if comment and not multi_line:
                    comment = False
                if quotes and i:
                    if tokens[i-1] == "\\":
                        fatal_error(tokens[i-1], "Syntax error. Unmatched \"")

            if not comment:
                result.append(tokens[i])

            i += 1

        dbg("Finished Removing Comments From The Tokens!")
        return result


    def get_backslashes_before(self, tokens, index):
        result = 0

        for i in range(index-1, -1, -1):
            if tokens[i] != "\\":
                return result
            result += 1

        return result


    def check_directive_syntax(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i] == "#END_DIRECTIVE":
                fatal_error(tokens[i], "Invalid token")
            elif tokens[i] == "#":
                definition = False
                # put #END_DIRECTIVE in place of the newline
                while i < n:
                    if tokens[i] == "define":
                        definition = True
                    elif tokens[i] == " " and definition:
                        tokens[i].token = "DEFINE_SPACE"
                    elif tokens[i] == "\n":
                        tokens.insert(i, Token("#END_DIRECTIVE", tokens[i].line_number, tokens[i].filename))
                        break;
                    i += 1

            i += 1

        return tokens

    
    def combine_strings(self, tokens:list[Token]) -> list[Token]:
        dbg("Combining string and char literals to single tokens...")

        i = 0
        n = len(tokens)

        result = []

        quotes = False
        char_quotes = False

        while i < n:
            if tokens[i] == "\"":
                if not char_quotes and not quotes:
                    quotes = 1
                    result.append(tokens[i])
                    i += 1
                    continue
                elif not char_quotes and quotes:
                    backslashes = self.get_backslashes_before(tokens, i)
                    if backslashes % 2 == 0:
                        quotes = False
                        result[-1].token += tokens[i].token
                        i += 1
                        continue
            elif tokens[i] == "'":
                if not char_quotes and not quotes:
                    char_quotes = True
                    result.append(tokens[i])
                    i += 1
                    continue
                elif char_quotes and not quotes:
                    backslashes = self.get_backslashes_before(tokens, i)
                    if backslashes % 2 == 0:
                        char_quotes = False
                        result[-1].token += tokens[i].token
                        i += 1
                        continue
            elif tokens[i] == "\\":
                if i + 1 < n:
                    if tokens[i+1] == '\n':
                        i += 2
                        continue

            if quotes or char_quotes:
                result[-1].token += tokens[i].token
            else:
                if tokens[i].token not in {" ", "\n", "\t"}:
                    result.append(tokens[i])

            i += 1

        dbg("Finished combining string and char literals to single tokens...")
        return result


    def combine_floats(self, tokens):
        i = 0
        n = len(tokens)

        result = []

        while i < n:
            try:
                int(tokens[i].token)
                int(tokens[i+2].token)
                if tokens[i+1] == ".":
                    tokens[i].token += tokens[i+1].token + tokens[i+2].token
                    result.append(tokens[i])
                    i += 3
                    continue
            except:
                pass
            result.append(tokens[i])
            i += 1

        return result 
        
        
