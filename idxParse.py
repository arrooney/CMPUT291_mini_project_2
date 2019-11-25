"""
CMPUT 291 MiniProject 2
"""

import re
from bsddb3 import db

class QueryParse(object):
    """

    Recursive descent-style parser to implement the query language as specified by the grammar on eclass.

    + execute(tokens) executes the parser on the given tokens
    + getResult() returns the set of ID's matching the executed query

    """

    """ CONSTRUCTOR """
    def __init__(self):
        self.mode = "brief" # brief by default

    """ Public API methods """

    def execute(self, tokens):
        # run the parser on the given tokens
        self.tokens = tokens # list of tokens from the user
        self.current = 0
        self.idResult = set()
        self.multipleQuery = False

        return self.__command__()

    def getResult(self):
        # get the set of ID's as a list
        return list(self.idResult)

    """ Private methods """

    def __cursor__(self, path, treeType):
        # get a new cursor to a berkeley db index file of the given type
        tmp = db.DB()
        data = db.DB_BTREE if treeType == "btree" else db.DB_HASH
        tmp.open(path, None, data, db.DB_RDONLY)

        return [tmp, tmp.cursor()]

    def __closeConn__(self, db):
        # close a db file
        db.close()

    def __rewind__(self):
        # decrement the token pointer
        self.current -= 1

    def __currentToken__(self):
        # return the current token
        if self.current < len(self.tokens):
            return self.tokens[self.current]

        return ""

    def __match__(self, pattern):
        # check if the current token matches the given pattern
        # consume the token if true
        if re.search(pattern, self.__currentToken__()):
            self.current += 1
            return True

        return False

    def __command__(self):
        # entry point to parser, either change mode, or another type of query
        # command ::= query | modeChange
        if (self.__match__("^output=[\w]+$")):
            self.__rewind__()
            return self.__modeChange__()
        else:
            return self.__query__()

    def __modeChange__(self):
        # change the output verbosity of the query
        mode = re.findall("^output=([\w]+)$", self.__currentToken__())

        if mode != []:
            mode = mode[0]

        if not (mode == 'full' or mode == 'brief'):
            return "Failed"
        else:
            self.mode = mode
            return "Success"

    def __query__(self):
        # parse tokens until they have all been consumed
        while self.current < len(self.tokens):
            self.__expression__()

    def __expression__(self):
        # implement expression production
        # expression      ::= dateQuery | emailQuery | termQuery
        if self.__match__("^date$"):
            self.__dateQuery__()
            self.multipleQuery = True
        elif self.__match__("^cc$|^bcc$|^from$|^to$"):
            self.__rewind__()
            self.__emailQuery__()
            self.multipleQuery = True
        else:
            self.__termQuery__()
            self.multipleQuery = True

        return True

    def __dateQuery__(self):
        # implement date query production
        # dateQuery       ::= datePrefix whitespace* date
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
                result = cursor.next()

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

        if self.idResult != set():
            self.idResult = self.idResult.intersection(dateSet)
        else:
            self.idResult = dateSet
        self.__closeConn__(db)

        return

    def __emailQuery__(self):
        # implement emailQuery production
        # emailQuery    ::= emailPrefix whitespace* email
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
        emailSearch = emailSearch.lower()
        #iterate through every single entry in the query
        #Check and return all emails that have a key that matches emailSearch
        result = cursor.first()
        while (result != None):

            if result[0].decode("utf-8").lower() == emailSearch:
                emailSet.add(result[1].decode("utf-8"))
            result = cursor.next()

        if self.idResult != set():
            self.idResult = self.idResult.intersection(emailSet)
        else:
            self.idResult = emailSet

        self.__closeConn__(db)

        return

    def __termQuery__(self):
        # implement termQuery production
        # termQuery       ::= termPrefix? whitespace* term termSuffix?
        [db, cursor] = self.__cursor__("idx/re.idx", "hash")

        if self.__match__("^subj$") or self.__match__("^subject$"):
            # seach in the subject field
            if not self.__match__("^:$"): print("ERROR") # consume the colon

            wildCard = False
            searchTerm = "s-" + self.__consumeToken__()
            searchTerm = searchTerm.lower()

            if self.__match__("^%$"):
                wildCard = True
            self.__findTerm__(wildCard, searchTerm)

        elif self.__match__("^body$"):

            if not self.__match__("^:$"): print("ERROR") # consume the colon

            # seach in the body field
            wildCard = False
            searchTerm = "b-" + self.__consumeToken__()
            searchTerm = searchTerm.lower()

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
            term = term.lower()
            searchTerm = "b-" + term
            self.__findTerm__(wildCard, searchTerm)
            searchTerm = "s-" + term
            self.__findTerm__(wildCard, searchTerm, generalTerm=True)
        return


    def __findTerm__(self, wildCard, term, generalTerm=False):
        # Get the given term from the term file
        [db, cursor] = self.__cursor__("idx/te.idx", "btree")
        termSet = set()

        if wildCard:
            # search for all occurances in alphabetical order
            result = cursor.set_range(term.encode("utf-8"))

            while (result != None and result[0].decode("utf-8").startswith(term)):
                termSet.add(result[1].decode("utf-8"))
                result = cursor.next()
        else:
            result = cursor.set(term.encode("utf-8"))
            while (result != None and result[0].decode("utf-8") == term):
                termSet.add(result[1].decode("utf-8"))
                result = cursor.next()

        if self.idResult == set():
            self.idResult = termSet
        elif not generalTerm:
            self.idResult = self.idResult.intersection(termSet)
        else:
            # when you're looking for subject OR body
            self.idResult = self.idResult.union(termSet)

        self.__closeConn__(db)

        return


    def __emailTerm__(self, email):
        # recursively construct the email term production
        # emailterm ::= alphanumeric+ | alphanumeric+ '.' emailterm
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
        # return the current token, and increment pointer
        temp = self.__currentToken__()
        self.current += 1
        return temp


    def __createDate__(self):
        # implement the date production from the grammar
        # date            ::= numeric numeric numeric numeric '/' numeric numeric '/' numeric numeric
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
        return dateString


class Lexer(object):
    """
    Tokenize a given query to prepare for parsing
    """
    def __init__(self):
        return

    def execute(self, query):
        tmp = list(filter(None, re.split(r" |(^[<>=]{2}$)|(^[:<>]{1}$)|(^output=[\w]+$)|([a-zA-Z0-9_\-]+)", query)))
        tokens = []
        [tokens.append(x.lower()) for x in tmp if not str(x).strip() == ""]
        return tokens


class XMLlexer(object):
    """
    Tokenize the given XML and return tokens based on <tags>and_data</tags>
    """
    def __init__(self):
        return

    def execute(self, xml):
        tmp = re.split("(<[\w\/]+>)", xml)
        tokens = []
        [tokens.append(x) for x in tmp if not str(x).strip() == ""]
        return tokens


class XMLParse(object):
    """
    Parse XML tokens and reuturn a pyhton dictionary with key-value pairs from
    the found tags
    """
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
    # main for testing purposes
    query = input("enter query:\n")
    lex = Lexer()
    tokens = lex.execute(query)
    parser = QueryParse(tokens)
    parser.execute()
    print (parser.idResult)


if __name__ == "__main__":
    main()
