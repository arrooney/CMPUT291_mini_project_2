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
                print(self.__currentToken__())
                dateString = self.__createDate__()
                result = cursor.set(dateString.encode("utf-8"))

                if result != None:
                    self.idResult.add(result[0].decode("utf-8"))

            elif self.__match__("^>=$"):
                dateString = self.__createDate__()
                result = cursor.set_range(dateString.encode("utf-8"))
                while (result != None):
                    print (result)
                    result = cursor.next()
                    if result != None:
                        self.idResult.add(result[0].decode("utf-8"))

            elif self.__match__("^<=$"):
                dateString = self.__createDate__()
                    
                result = cursor.set_range(dateString.encode("utf-8"))
                while (result != None):
                    result = cursor.prev()
                    if result != None:
                        self.idResult.add(result[0].decode("utf-8"))

            elif self.__match__("^>$"):
                dateString = self.__createDate__()

                result = cursor.set_range(dateString.encode("utf-8"))
                
                while (result != None):
                    if self.__currentToken__() != result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        result = cursor.next()
                        if result != None:
                            self.idResult.add(result[0].decode("utf-8"))
                        
            elif self.__match__("^<$"):
                dateString = self.__createDate__()
                result = cursor.set_range(dateString.encode("utf-8"))
                while (result != None):
                    if self.__currentToken__() != result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        result = cursor.prev()
                        if result != None:
                            self.idResult.add(result[0].decode("utf-8"))

            self.__closeConn__(db)
            return
        
        def __emailQuery__(self):
            [db, cursor] = self.__cursor__("idx/em.idx", "btree")

            #creating an empty string and adding the first token to it
            emailString = ""
            emailString += self.__consumeToken__()

            self.__consumeToken__()
            #do this because we need to set the second part of the string to the mail
            #so we need to skip over the delimiter
            
            emailString += '-'
            emailString += self.__currentToken__()
            print (emailString)
            #iterate through every single entry in the query
            #Check and return all emails that have a key that matches emailString
            # email_result = cursor.set(emailString.encode("utf-8"))
            # print (email_result)
            # while (email_result != None):
            #     #excludes the current token since this is exclusive
            #     if self.__currentToken__() != email_result[0].decode("utf-8"):
            #         email_result = cursor.next()
            #         if len(email_result) != 0:
            #             self.idResult.add(email_result[0].decode("utf-8"))

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
            self.current += 1
            return temp
        
        def __createDate__(self):
            dateString = ""
            if re.search("^[0-9]{4}$", self.__currentToken__()):
                dateString += self.__consumeToken__()

            if re.search("^/$", self.__currentToken__()):
                dateString += self.__consumeToken__()
                
            if re.search("^[0-9]{2}$", self.__currentToken__()):
                dateString += self.__consumeToken__()
                
            if re.search("^/$", self.__currentToken__()):
                dateString += self.__consumeToken__()
                
            if re.search("^[0-9]{2}$", self.__currentToken__()):
                dateString += self.__consumeToken__()
            return dateString



def lexer(query):
    tmp = list(filter(None, re.split(r" |(^[<>=]{2}$)|(^[:<>]{1}$)|(^output=[\w]+$)|([a-zA-Z0-9_\-]+)", query)))
    tokens = []
    [tokens.append(x) for x in tmp if not str(x).strip() == ""]
    return tokens



def main():
    query = input("enter query:\n")
    tokens = lexer(query)
    parser = QueryParse(tokens)
    print(parser.execute())


if __name__ == "__main__":
    main()
