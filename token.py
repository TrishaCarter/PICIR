


class Token:

    def __init__(self, token:str, line_number:int, filename:str):
        self.token = token
        self.line_number = line_number
        self.filename = filename

    def __eq__(self, other:str):
        return self.token == other

    def __len__(self):
        return len(self.token)

    def __str__(self) -> str:
        return self.token

    def __repr__(self) ->str:
        return self.__str__()


