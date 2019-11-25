"""
CMPUT 291 MiniProject 2
"""
from idxParse import QueryParse, Lexer, XMLlexer, XMLParse
from bsddb3 import db
import os, sys, time, re

# globals
clear = lambda: os.system('clear')
lexer = Lexer()
parser = QueryParse()
xmlLexer = XMLlexer()
xmlParser = XMLParse()

def displayResults(idList, verbosity):
	mydb = db.DB()
	mydb.open("idx/re.idx", None, db.DB_HASH, db.DB_RDONLY)
	cursor = mydb.cursor()
	for thisId in idList:
		result = cursor.set(thisId.encode("utf-8"))
		if (result == None):
			return
		tok = xmlLexer.execute(result[1].decode("ASCII"))
		xmlParser.execute(tok)
		email = xmlParser.result

		print("\nID:")
		print(email["row"])
		print("subj:")
		if ("subj" in email.keys()):
			print(email["subj"])
		else:
			print("(No subject)")
		if verbosity == "full":
			print("Date:")
			if ("date" in email.keys()):
				print(email["date"])
			print("From:")
			if ("from" in email.keys()):
				print(email["from"])
			print("To:")
			if ("to" in email.keys()):
				print(email["to"])
			print("CC:")
			if ("cc" in email.keys()):
				print(email["cc"])
			print("BCC:")
			if ("bcc" in email.keys()):
				print(email["bcc"])
			print("Body:")
			if ("body" in email.keys()):
				print(email["body"])
		print("")
	mydb.close()

def main():
	while True:
		prettyPrint("Enter your query:")
		query = input("> ")
		tokens = lexer.execute(query)
		parser.execute(tokens)
		idx = parser.getResult()
		if idx == []:
			# either empty, or mode change
			prettyPrint("No results", 0.5)
		else:
			displayResults(idx, parser.mode)
		input("Press enter to continue...")

def prettyPrint(output, timeout=0):
	# output a nice header, with an optional timeout parameter
	clear()
	print ("=====================================")
	print ("\t" + output)
	print ("=====================================")
	time.sleep(timeout)

if __name__ == "__main__":
	main()
