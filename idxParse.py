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
            self.multipleQuery = False

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
            if self.current < len(self.tokens):
                return self.tokens[self.current]
            return ""

        def __match__(self, pattern):
            if re.search(pattern, self.__currentToken__()):
                self.current += 1
                return True
            return False

        def execute(self):
            return self.__command__()

        def getResult(self):
            return list(self.idResult)

        def __command__(self):
            # print("fuc")
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
                self.__termQuery__()
            return True

        def __dateQuery__(self):
            [db, cursor] = self.__cursor__("idx/da.idx", "btree")
            dateSet = set()
            if self.__match__("^:$"):
                dateString = self.__createDate__()
                if dateString != None:
                    result = cursor.set_range(dateString.encode("utf-8"))
                else:
                    print ("BAD QUERY FORMAT")
                    return

                while (result != None):
                    if dateString == result[0].decode("utf-8"):
                        dateSet.add(result[1].decode("utf-8"))
                    cursor.next()

                if result != None:
                    dateSet.add(result[1].decode("utf-8"))

            elif self.__match__("^>=$"):
                dateString = self.__createDate__()
                if dateString != None:
                    result = cursor.set_range(dateString.encode("utf-8"))
                else:
                    print ("BAD QUERY FORMAT")
                    return
                
                while (result != None):
                    # print (result)
                    if result != None:
                        dateSet.add(result[1].decode("utf-8"))
                    result = cursor.next()

            elif self.__match__("^<=$"):
                dateString = self.__createDate__()
                if dateString != None:
                    result = cursor.set_range(dateString.encode("utf-8"))
                else:
                    print ("BAD QUERY FORMAT")
                    return
                
                while (result != None):
                    if result != None and dateString >= result[0].decode("utf-8"):
                        dateSet.add(result[1].decode("utf-8"))
                    result = cursor.prev()

            elif self.__match__("^>$"):
                dateString = self.__createDate__()
                if dateString != None:
                    result = cursor.set_range(dateString.encode("utf-8"))
                else:
                    print ("BAD QUERY FORMAT")
                    return
                
                while (result != None):
                    if dateString != result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        if result != None:
                            dateSet.add(result[1].decode("utf-8"))
                    result = cursor.next()
                        
            elif self.__match__("^<$"):
                dateString = self.__createDate__()
                if dateString != None:
                    result = cursor.set_range(dateString.encode("utf-8"))
                else:
                    print ("BAD QUERY FORMAT")

                while (result != None):
                    if dateString != result[0].decode("utf-8") and dateString > result[0].decode("utf-8"): #excludes the current token since this is exclusive
                        if result != None:
                            dateSet.add(result[1].decode("utf-8"))
                    result = cursor.prev()

            if self.multipleQuery == True:
                self.idResult.intersection(dateSet)
            else:
                self.idResult = dateSet
            self.__closeConn__(db)
            return
        
        def __emailQuery__(self):
            [db, cursor] = self.__cursor__("idx/em.idx", "btree")
            emailSet = set()
            #creating an empty string and adding the first token to it
            emailSearch = ""
            emailTerm = ""
            emailSearch += self.__consumeToken__()  + "-" # add the "to-, from-, bcc-, or cc-"
            if self.__currentToken__() == ":":
                self.__consumeToken__() # discard the colon
            else:
                print ("Enter a valid query")
            emailSearch += self.__emailTerm__(emailTerm)
            if (self.__match__("^@$")):
                emailterm = ""
                emailSearch += "@" + self.__emailTerm__(emailTerm)
            
            #iterate through every single entry in the query
            #Check and return all emails that have a key that matches emailSearch
            result = cursor.first()
            while (result != None):
                if result[0].decode("utf-8") == emailSearch:
                    # print (result[1].decode("utf-8"))
                    emailSet.add(result[1].decode("utf-8"))
                result = cursor.next()
            if self.multipleQuery == True:
                self.idResult.intersection(emailSet)
            else:
                self.idResult = emailSet
            
            self.__closeConn__(db)

            return
       
        def __termQuery__(self):
            [db, cursor] = self.__cursor__("idx/re.idx", "hash")
            if self.__match__("^subj$"):
                # seach in the subject field
                
                if not self.__match__("^:$"): print("ERROR") # consume the colon
                
                wildCard = False
                searchTerm = "s-" + self.__consumeToken__()
                if self.__match__("^%$"):
                    wildCard = True
                self.__findTerm__(wildCard, searchTerm)

            elif self.__match__("^body$"):

                if not self.__match__("^:$"): print("ERROR") # consume the colon

                # seach in the body field
                wildCard = False
                searchTerm = "b-" + self.__consumeToken__()
                if self.__match__("^%$"):
                    wildCard = True
                
                self.__findTerm__(wildCard, searchTerm)

            else: 
                #this will be the condition where term prefix is 0
                # search BOTH in the body, and the subject
                wildCard = False
                term = self.__consumeToken__()
                if self.__match__("^%$"):
                    wildCard = True
                searchTerm = "b-" + term
                self.__findTerm__(wildCard, searchTerm)
                searchTerm = "s-" + term
                self.__findTerm__(wildCard, searchTerm)
            return

        def __findTerm__(self, wildCard, term):
            [db, cursor] = self.__cursor__("idx/te.idx", "btree")
            termSet = set()
            if wildCard:
                # search for all occurances in alphabetical order
                result = cursor.set(term.encode("utf-8"))
                while (result != None and result[0].decode("utf-8").startswith(term)):
                    termSet.add(result[1].decode("utf-8"))
                    result = cursor.next()
            else:
                result = cursor.set(term.encode("utf-8"))
                if result != None:
                    print(result)
                    termSet.add(result[1].decode("utf-8"))
            if self.multipleQuery == True:
                self.idResult.intersection(termSet)
            else:
                self.idResult = termSet
            
            self.__closeConn__(db)
            return

        def __emailTerm__(self, email):
            # recursively construct the email term production
            if(re.search("^[0-9a-zA-Z_-]+$", self.__currentToken__())):
                email += self.__consumeToken__()
                if(re.search("^\.$", self.__currentToken__())):
                    tmp = ""
                    email += self.__consumeToken__()
                    email += self.__emailTerm__(tmp)
                return email
            else:
                print("BAD EMAIL FORMAT")

        def __consumeToken__(self):
            temp = self.__currentToken__()
            self.current += 1
            return temp            

        def __createDate__(self):
            dateString = ""
            if re.search("^[0-9]{4}$", self.__currentToken__()):
                dateString += self.__consumeToken__()
            else:
                return None

            if re.search("^/$", self.__currentToken__()):
                dateString += self.__consumeToken__()
            else:
                return None
                
            if re.search("^[0-9]{2}$", self.__currentToken__()):
                dateString += self.__consumeToken__()
            else:
                return None
                
            if re.search("^/$", self.__currentToken__()):
                dateString += self.__consumeToken__()
            else:
                return None
                
            if re.search("^[0-9]{2}$", self.__currentToken__()):
                dateString += self.__consumeToken__()
            else:
                return None
            #do while python equavilent?
            return dateString

class Lexer(object):

    def __init__(self):
        return

    def execute(self, query):
        tmp = list(filter(None, re.split(r" |(^[<>=]{2}$)|(^[:<>]{1}$)|(^output=[\w]+$)|([a-zA-Z0-9_\-]+)", query)))
        tokens = []
        [tokens.append(x) for x in tmp if not str(x).strip() == ""]
        return tokens

class XMLlexer(object):
    def __init__(self):
        return

    def execute(self, xml):
        tmp = re.split("(<[\w\/]+>)", xml)
        tokens = []
        [tokens.append(x) for x in tmp if not str(x).strip() == ""]
        return tokens

class XMLParse(object):
    """docstring for XMLParse"""
    def __init__(self):
        self.result = {}

    def execute(self, tokens):
        i = 0
        self.result = {}
        while(i < len(tokens)):
            if (re.search("<([a-zA-Z]+)>", tokens[i])):
                tmp = re.findall("<([a-zA-Z]+)>", tokens[i])[0]
                i += 1
                val = tokens[i]
                if not re.search("^<[\w\/]+>$", val):
                    # not another tag of any sort
                    self.result[tmp] = val
                else:
                    self.result[tmp] = ""
                    i -= 1
            i += 1

        

def main():
    query = input("enter query:\n")
    lex = Lexer()
    tokens = lex.execute(query)
    parser = QueryParse(tokens)
    parser.execute()
    print (parser.idResult)


if __name__ == "__main__":
    main()
