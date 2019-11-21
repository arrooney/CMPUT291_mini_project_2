# alphanumeric    ::= [0-9a-zA-Z_-]
# numeric		::= [0-9]
# date            ::= numeric numeric numeric numeric '/' numeric numeric '/' numeric numeric
# datePrefix      ::= 'date' whitespace* (':' | '>' | '<' | '>=' | '<=')
# dateQuery       ::= datePrefix whitespace* date
# emailterm	::= alphanumeric+ | alphanumeric+ '.' emailterm
# email		::= emailterm '@' emailterm
# emailPrefix	::= (from | to | cc | bcc) whitespace* ':'
# emailQuery	::= emailPrefix whitespace* email
# term            ::= alphanumeric+
# termPrefix	::= (subj | body) whitespace* ':'
# termSuffix      ::= '%'
# termQuery       ::= termPrefix? whitespace* term termSuffix?
#
# expression      ::= dateQuery | emailQuery | termQuery
# query           ::= expression (whitespace expression)*
#
# modeChange	::= 'output=full' | 'output=brief'
#
# command		::= query | modeChange

import re
from bsddb3 import db

class QueryParse(object):
        def __init__(self, tokens):
            self.tokens = tokens # list of tokens from the user
            self.current = 0
            self.mode = "brief" # brief by default
            self.idResult = set()
            # mydb.open("idx/da.idx", None, db.DB_BTREE, db.DB_RDONLY)
            # cursor = mydb.cursor()
            # mydb.close()

        def __cursor__(self, path, treeType):
            tmp = db.DB()
            data = db.DB_BTREE if treeType == "btree" else db.DB_HASH
            tmp.open(path, None, data, db.DB_RDONLY)
            return [tmp, tmp.cursor()]

        def __closeConn__(self, db):
            db.close()

        def __rewind__(self):
            self.current -= 1

        def __currentToken__(self):
            return self.tokens[self.current]

        def __match__(self, pattern):
            if re.search(pattern, self.__currentToken__()):
                self.current += 1
                return True
            return False

        def execute(self):
            return self.__command__()

        def __command__(self):
            print(self.__currentToken__())

            if (self.__match__("^output=[\w]+$")):
                self.__rewind__()
                return self.__modeChange__()
            else:
                return self.__query__()

        def __modeChange__(self):
            mode = re.findall("^output=([\w]+)$", self.__currentToken__())
            if mode != []:
                mode = mode[0]
            if not (mode == 'full' or mode == 'brief'):
                return "Failed"
            else:
                self.mode = mode
                return "Success"

        def __query__(self):
            while self.current < len(self.tokens):
                self.__expression__()

        def __expression__(self):
            if self.__match__("^date$"):
                self.__dateQuery__()

            elif self.__match__("^cc$|^bcc$|^from$|^to$"):
                self.__rewind__()
                self.__emailQuery__()

            else:
                self.__rewind__()
                self.__termQuery__()
            return True

        def __dateQuery__(self):
            [db, cursor] = self.__cursor__("idx/da.idx", "btree")

            if self.__match__("^:$"):
                dateString = ""
                if re.search("^[0-9]{4}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()

                result = cursor.set(dateString.encode("utf-8"))
                self.idResult.add(result)

            elif self.__match__("^>=$"):
                dateString = ""
                if re.search("^[0-9]{4}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()

                result = cursor.set_range(dateString.encode("utf-8"))
                while (result != None):
                    result = cursor.next()
                    self.idResult.add(result)

            elif self.__match__("^<=$"):
                if re.search("^[0-9]{4}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                    
                result = cursor.set_range(dateString.encode("utf-8"))
                while (result != None):
                    result = cursor.prev()
                    self.idResult.add(result)

            elif self.__match__("^>$"):
                if re.search("^[0-9]{4}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()

                result = cursor.set_range(dateString.encode("utf-8"))
                while (result != None):
                    if self.__currentToken__() != result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        result = cursor.next()
                        self.idResult.add(result)
                        
            elif self.__match__("^<$"):
                if re.search("^[0-9]{4}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()
                if self.__match__('/'):
                    dateString+=self.__consumeToken__()
                if re.search("^[0-9]{2}$", self.__currentToken__()):
                    dateString+=self.__consumeToken__()

                result = cursor.set_range(dateString.encode("utf-8"))
                while (result != None):
                    if self.__currentToken__() != result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        result = cursor.prev()
                        self.idResult.add(result)

            self.__closeConn__(db)
            return
        
        def __emailQuery__(self):
            [db, cursor] = self.__cursor__("idx/em.idx", "btree")

            emailString = ""
            emailString += self.__currentToken__()
            self.__current__+=2 #do this because we need to set the second part of the string to the mail, so we need to skip over the delimiter
            emailString += self.__currentToken__()

            #iterate through every single entry in the query
                #Check and return all emails that have a key that matches emailString
            self.__closeConn__(db)
            return
       
        def __termQuery__(self):
            [db, cursor] = self.__cursor__("idx/re.idx", "hash")

            if self.__match__("^subj$"):
                self.__current__+=1 #do this because the term after subj is the delimiter,

            elif self.__match__("^body$"):
                self.__current__+=1 #do this because the term after body is the delimiter

            else: return #this will be the condition where term prefix is 0
                #do something
            self.__closeConn__(db)
            return
        def __consumeToken__(self):
            temp = self.__currentToken__()
            self.__current__+=1
            return temp


def lexer(query):
    tmp = list(filter(None, re.split(r" |([a-zA-Z0-9_\-]+)|([:<>]{1})|(^output=[\w]+$)|(^[<>=]{2}$)", query)))
    tokens = []
    [tokens.append(x) for x in tmp if not str(x).strip() == ""]
    return tokens



def main():
    query = input("enter query:\n")
    tokens = lexer(query)
    print(tokens)
    parser = QueryParse(tokens)
    print(parser.execute())


if __name__ == "__main__":
    main()
