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
            self.mydb = db.DB()
            self.idResult = set([]) # instantiate the database object
            # mydb.open("idx/da.idx", None, db.DB_BTREE, db.DB_RDONLY)
            # cursor = mydb.cursor()
            # mydb.close()

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
            if (self.__match__("^output=[\w]$")):
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

            elif self.__match__("^cc$ | ^bcc$ | ^from$ | ^to$"):
                self.__rewind__()
                self.__emailQuery__()

            else:
                self.__rewind__()
                self.__termQuery__()

            return True

        def __dateQuery__(self):
            mydb.open("idx/da.idx", None, db.DB_BTREE, db.DB_RDONLY)
            cursor = mydb.cursor()

            if self.__match__("^:$"):
                result = cursor.set(self.__currentToken__().encode("utf-8"))
                idResult.add(result)


            elif self.__match__("^>=$"):
                result = cursor.set_range(self.__currentToken__().encode("utf-8"))
                while (result != None):
                    result = cursor.next()
                    idResult.add(result)

            elif self.__match__("^<=$"):
                result = cursor.set_range(self.__currentToken__().encode("utf-8"))
                while (result != None):
                    result = cursor.prev()
                    idResult.add(result)

            elif self.__match__("^>$"):
                result = cursor.set_range(self.__currentToken__().encode("utf-8"))
                while (result != None):
                    if self.__currentToken__() != result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        result = cursor.next()
                        idResult.add(result)
                        
            elif self.__match__("^<$"):
                result = cursor.set_range(self.__currentToken__().encode("utf-8"))
                while (result != None):
                    if self.__currentToken__() != result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        result = cursor.prev()
                        idResult.add(result)
            mydb.close()
            return
        def __emailQuery__(self):
            mydb.open("idx/em.idx", None, db.DB_BTREE, db.DB_RDONLY)
            cursor = mydb.cursor()

            emailString = ""
            emailString += self.__currentToken__()
            self.__current__+=2 #do this because we need to set the second part of the string to the mail, so we need to skip over the delimiter
            emailString += self.__currentToken__()

            #iterate through every single entry in the query
                #Check and return all emails that have a key that matches emailString

            return
        def __termQuery__(self):
            mydb.open("idx/recs.idx", None, db.DB_BTREE, db.DB_RDONLY)
            cursor = mydb.cursor()

            if self.__match__("^subj$")
                self.__current__+=1 #do this because the term after subj is the delimiter,

            elif self.__match__("^body$")
                self.__current__+=1 #do this because the term after subj is the delimiter

            else #this will be the condition where term prefix is 0
                #do something
            return

def main():

    query = input("enter query")
    tokens = list(filter(None, re.split(r"([\w]+( )*:)", query)))
    parser = QueryParse(tokens)
    print(parser.execute())


if __name__ == "__main__":
    main()
