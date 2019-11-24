from idxParse import QueryParse
import re

#Reading the input query and creating a list of tokens
def lexer(query):
    tmp = list(filter(None, re.split(r" |(^[<>=]{2}$)|(^[:<>]{1}$)|(^output=[\w]+$)|([a-zA-Z0-9_\-]+)", query)))
    tokens = []
    [tokens.append(x) for x in tmp if not str(x).strip() == ""]
    return tokens

def main():
    input_query = input("Enter your query: ")
    tokens = lexer(input_query)
    parser = QueryParse(tokens)
    parser.execute()
    [db, cursor] = parser.__cursor__("idx/re.idx", "hash")
    recordResult = []
    for ID in parser.idResult:
        record = cursor.first()
        while record != None:
            if ID == record[0].decode("utf-8"):
                recordResult.append(record[1].decode("utf-8"))
            record = cursor.next()
    print (recordResult)

if __name__ == "__main__":
    main()