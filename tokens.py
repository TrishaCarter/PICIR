
import errors

VARNUM = 0

class Token:
    """
    Holds state information to do with
    a single C token.
    """
    def __init__(self, token:str, filename:str, line_number:int):
        self.token = token
        self.filename = filename
        self.line_number = line_number
        self.undefined = False

    def __len__(self):
        return len(self.token)
    def __str__(self):
        return str(self.token)
    def __repr__(self):
        return repr(self.token)
    def __getitem__(self, index):
        return self.token[index]
    def __iter__(self):
        return iter(self.token)
    def __contains__(self, item):
        return item in self.token

    def __eq__(self, other):
        return self.token == str(other)
    def __ne__(self, other):
        return self.token != str(other)

    def __lt__(self, other):
        return self.token < str(other)
    def __le__(self, other):
        return self.token <= str(other)
    def __gt__(self, other):
        return self.token > str(other)
    def __ge__(self, other):
        return self.token >= str(other)

    def __hash__(self):
        return self.token.__hash__()


    def error(self, message:str):
        message = f"{message}: ({self.token})"
        result = errors.Error(message, self.filename, self.line_number)
        errors.ERROR_HANDLER.add_error(result, fatal=False)

    def fatal_error(self, message:str):
        message = f"{message}: ({self.token})"
        result = errors.Error(message, self.filename, self.line_number)
        errors.ERROR_HANDLER.add_error(result, fatal=True)


def string_to_token(string):
    if issubclass(type(string), Token):
        return string
    return Token(string, "", 0)


def strings_to_tokens(strings):
    return [string_to_token(x) for x in strings]


class Tokens:
    """
    Holds a list of tokens.
    Makes operations on lists of tokens easier.
    """
    def __init__(self, tokens:list[Token]=[]):
        self.tokens = tokens
        self.varnum = 0
        self.label_num = 0

    def valid_next(self, search:str, valid_tokens:set):
        """
        Throw a syntax error if a token not in valid tokens
        is after the search token
        None = End of file
        """
        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] == search:
                # this is the last token
                if i + 1 >= n:
                    # throw error if this is not allowed to be the last token
                    if None not in valid_tokens:
                        error_message = f"Expected one of '{list(valid_tokens)}' after '{search}'. Found EOF."
                        self.tokens[i].error(error_message)
                else:
                    if self.tokens[i+1] not in valid_tokens:
                        error_message = f"Expected one of '{list(valid_tokens)}' after '{search}'. Found '{self.tokens[i+1]}'."
                        self.tokens[i].error(error_message)

            i += 1


    def valid_last(self, search:str, valid_tokens:set):
        """
        Throw a syntax error if a token not in valid tokens
        is before the search token
        None = Beginning of file
        """
        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] == search:
                # this is the last token
                if i == 0:
                    # throw error if this is not allowed to be the last token
                    if None not in valid_tokens:
                        error_message = f"Expected one of '{list(valid_tokens)}' before '{search}'. Found BOF."
                        self.tokens[i].error(error_message)
                else:
                    if self.tokens[i-1] not in valid_tokens:
                        error_message = f"Expected one of '{list(valid_tokens)}' before '{search}'. Found '{self.tokens[i-1]}'."
                        self.tokens[i].error(error_message)

            i += 1


    def check_valid(self, valid_tokens:set):
        """
        Check if all tokens are present in the set of valid tokens,
        else throw a fatal error
        """
        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] not in valid_tokens:
                self.tokens[i].fatal_error(f"Token '{self.tokens[i]}' is invalid...\n\tvalid tokens: {list(valid_tokens)}")
            i += 1


    def remove_all(self, search:str):
        """
        Remove all occurrences of a token.
        """
        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] == search:
                del self.tokens[i]
                i -= 1
                n -= 1
            i += 1

    def replace_all_single(self, search:Token, replace:Token):
        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] == search:
                self.tokens[i] = replace
            i += 1
    

    def replace_all(self, search:list[str], replace:list[str]):
        """
        Replace all occurances of some tokens with some other tokens
        """
        i = 0
        n = len(self.tokens)
        while i < n:
            j = 0
            for j in range(len(search)):
                if search[j] != self.tokens[i+j]:
                    j = 0
                    break
            if j != 0:
                for j in range(len(search)):
                    del self.tokens[i]
                    n -= 1

                for tok in reversed(replace):
                    self.tokens.insert(i, Token(tok, self.tokens[i].filename, self.tokens[i].line_number))
                    n += 1

                i -= 1

            i += 1


    def error_all(self, search:str, error_message:str, fatal:bool=True):
        """
        Throw an error at all occurances of some tokens
        """
        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] == search:
                if fatal:
                    self.tokens[i].fatal_error(error_message)
                else:
                    self.tokens[i].error(error_message)
            i += 1

    def combine_all(self, search:list[str]):
        """
        For any occurance of all items in search in order,
        combine all of the values
        """
        m = len(search)
        if m == 0:
            return

        i = 0
        n = len(self.tokens)
        while i < n:
            j = 0
            for j in range(m):
                if self.tokens[i+j] != search[j]:
                    j = 0
                    break
            if j != 0:
                for j in range(m-1):
                    self.tokens[i].token += self.tokens[i+1].token
                    del self.tokens[i+1]
                    n -= 1
            i += 1


    def combine(self, index):
        self.tokens[index].token += self.tokens[index+1].token
        del self.tokens[index+1]


    def index(self, value):
        return self.tokens.index(value)


    def splice_until(self, index, end):
        """
        Remove tokens from index until (and including) the ending token
        """
        result = []
        while True:
            if index >= len(self.tokens):
                self.tokens[-1].fatal_error(f"Expected {end} before EOF")

            result.append(self.tokens[index])

            if self.tokens[index] == end:
                del self.tokens[index]
                break

            del self.tokens[index]

        return result


    def split_at(self, delimiter):
        result = []
        current = Tokens([])

        openers = ["(", "{", "["]
        closers = [")", "}", "]"]

        stack = []

        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] in openers:
                stack.append(self.tokens[i].token)
            elif self.tokens[i] in closers:
                if len(stack) == 0:
                    self.tokens[i].fatal_error(f"Unmatched {self.tokens[i]}")
                if closers.index(self.tokens[i]) != openers.index(stack[-1]):
                    self.tokens[i].fatal_error(f"Unmatched {self.tokens[i]}")
                stack.pop()

            if delimiter == self.tokens[i] and len(stack) == 0:
                result.append(current)
                current = Tokens([])
            else:
                current.append(self.tokens[i])
            i += 1

        result.append(current)
        return result


    def get_line_start(self, index):
        """
        get the index of the first token of this line
        { } ; :
        """
        result = index
        while result >= 0:
            if self.tokens[result] in ["{", "}", ";", ":"]:
                return result + 1
            result -= 1
        return result + 1

    
    def find_next(self, index, closer):
        """
        find the next closer starting from index
        """
        while index < len(self.tokens):
            if closer == self.tokens[index]:
                return index
            index += 1
        # Return None if it does not exist
        return None


    def get_match_end(self, index, closer:str):
        """
        Find the index of the closing token
        using a stack that opens at each occurance of index
        """
        opener = self.tokens[index]
        i = index
        n = len(self.tokens)
        opened = 0
        while i < n:
            if self.tokens[i] == opener:
                opened += 1
            elif self.tokens[i] == closer:
                opened -= 1
                if opened == 0:
                    return i
            i += 1

        # if never closed
        return None


    def get_match_content(self, index, closer:str):
        """
        Return the inner content of the closing token
        """
        end = self.get_match_end(index, closer)
        # if never closed
        if end is None:
            return None

        contents = self.tokens[index:end+1]
        self.tokens = self.tokens[:index] + self.tokens[end+1:]

        return contents


    def get_match_content_replace(self, index, closer:str):
        """
        Return the inner content of the closing token
        """
        end = self.get_match_end(index, closer)
        # if never closed
        if end is None:
            return None

        contents = self.tokens[index:end+1]
        return contents

    def insert_all(self, index:int, toks:list[Token]):
        for tok in reversed(toks):
            self.tokens.insert(index, tok)

    def __str__(self):
        return str(self.tokens)
    def __repr__(self):
        return repr(self.tokens)
    def __getitem__(self, index):
        return self.tokens[index]
    def __setitem__(self, index, value):
        self.tokens[index] = value
    def __delitem__(self, index):
        del self.tokens[index]
    def __iter__(self):
        return iter(self.tokens)
    def __len__(self):
        return len(self.tokens)
    def __contains__(self, item):
        return item in self.tokens
    def append(self, item):
        self.tokens.append(item)
    def extend(self, iterable):
        self.tokens.extend(iterable)
    def insert(self, index, item):
        self.tokens.insert(index, item)
    def remove(self, item):
        self.tokens.remove(item)
    def pop(self, index=-1):
        self.tokens.pop(index)
    def clear(self):
        self.tokens.clear()




class TOKEN_ANY(Token):
    """
    Special Token that is equal to any str
    """
    def __init__(self):
        pass



class TOKEN_VARIABLE(Token):
    """
    Special Token that is equal to any str in the form
    #{int}
    """
    def __init__(self):
        Token.__init__(self, "", "", 0)

    def __eq__(self, other):
        if len(other) == 0 or other[0] != "#":
            return False

        after = other[1:]
        try:
            int_rep = int(after)
            return str(int_rep) == after
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class TOKEN_INTEGER(Token):
    """
    Special Token that is equal to any str that is an int
    """
    def __init__(self):
        Token.__init__(self, "", "", 0)

    def __eq__(self, other):
        try:
            int_rep = int(other.token)
            return str(int_rep) == other
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)



class TOKEN_FLOAT(Token):
    """
    Special Token that is equal to any str that is a float
    """
    def __init__(self):
        pass



class TOKEN_FROM_LIST(Token):
    """
    Special Token that is equal to any str from given list
    """
    def __init__(self):
        """
        Special Token that is equal to any literal token
        """
        pass


class TOKEN_LITERAL(Token):
    def __init__(self):
        Token.__init__(self, "", "", 0)

    def __eq__(self, other):
        try:
            int_rep = int(other.token)
            return True
        except:
            pass
        return len(other) > 0 and other[0] in ["'", '"']

    def __ne__(self, other):
        return not self.__eq__(other)


class TypeToken(Token):
    """
    Special Token that is a replacement for multiple type tokens
    """
    def __init__(self, token, filename, line_number, value:list[Token]=[]):
        Token.__init__(self, token, filename, line_number)
        self.value = value


    def __repr__(self):
        return f"{self.token}({self.value})"


class VariableToken(Token):
    """
    Special Token that is a replacement for an identifier
    """
    def __init__(self, token, filename, line_number, original:Token, the_type:Token):
        Token.__init__(self, token, filename, line_number)
        self.original = original
        self.type = the_type


class EnumToken(Token):
    """
    Special Token that is a replacement for an enum
    """
    def __init__(self, token, filename, line_number, name=None, value=[]):
        Token.__init__(self, token, filename, line_number)
        self.name = name
        self.value = value
        self.mappings = {}

    def __repr__(self):
        return f"{self.token}({self.name})"


class StructToken(Token):
    """
    Special Token that is a replacement for an enum
    """
    def __init__(self, token, filename, line_number, name=None, value=[]):
        Token.__init__(self, token, filename, line_number)
        self.name = name
        self.value = value
        self.mappings = {}

    def __repr__(self):
        return f"{self.token}({self.name})"


class UnionToken(Token):
    """
    Special Token that is a replacement for an enum
    """
    def __init__(self, token, filename, line_number, name=None, value=[]):
        Token.__init__(self, token, filename, line_number)
        self.name = name
        self.value = value
        self.mappings = {}

    def __repr__(self):
        return f"{self.token}({self.name})"


class TypedefToken(Token):
    """
    Special Token that is a replacement for an enum
    """
    def __init__(self, token, filename, line_number, original_value:Token, new_value:Token):
        Token.__init__(self, token, filename, line_number)
        self.original_value = original_value
        self.new_value = new_value

    def __repr__(self):
        return f"{self.token}({self.original_value} -> {self.new_value})"


class FuncToken(Token):
    """
    Special Token that is a replacement for a function
    """
    def __init__(self, token, name_value, filename, line_number, name:str, return_type:str, args:list[Token], value:list[Token]):
        Token.__init__(self, token, filename, line_number)
        self.name = name
        self.name_value = name_value
        self.return_type = return_type
        self.args = args
        self.value = value

    def __repr__(self):
        return f"{self.token} - {self.name_value}({self.name}) -> {self.return_type} ({self.args}) => {self.value}"



class FunctionCall(Token):
    """
    Special Token that is a replacement for a function call
    """
    def __init__(self, value): 
        Token.__init__(self, "#FUNCCALL", "", 0)
        self.value = value


