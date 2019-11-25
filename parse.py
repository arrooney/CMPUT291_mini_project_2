"""
CMPUT 291 MiniProject 2
"""

import sys, re, os

class ParseMail(object):

	# CONSTRUCTOR:
	def __init__(self):
		self.thisEmail = {}
		self.current = 0
		self.thisToken = None
		self.term = None

	## PUBLIC METHODS: ##

	def execute(self):
		# public entry point to the parser
		self.__mail__()

	## PRIVATE METHODS: ##

	def __mail__(self):
		self.__openFiles__()
		self.thisEmail = {}
		self.thisEmail["xml"] = ""
		while(self.__match__("^\s*(<mail>)|(<emails type=[\w\"\']*>)\s*$")):
			self.__emailInfo__()
			self.thisEmail.clear()
			self.thisEmail["xml"] = ""
		self.__closeFiles__()

	def __emailInfo__(self):
		while(not self.__match__("^\s*</mail>\s*$", appendXml=False)):
			if re.search("^\s*<([\w]+)>([\s\w/!@#$%^&*\.:\-,\?\(\)\"\'\+=\\/\[\]\{\}]+)?</[\w]+>\s*$", self.__tokenPeek__()):
				# <tag>data</tag>
				# this line contains
				tagVal = re.findall("^\s*<([\w]+)>([\s\w/!@#$%^&*\.:\-,\?\(\)\"\'\+=\\/\[\]\{\}]+)?</[\w]+>\s*$", self.__consume__())
				self.thisEmail[tagVal[0][0]] = tagVal[0][1]

			if re.search("^\s*<([a-zA-z]+)>\s*$", self.__tokenPeek__()):
				# <tag>
				# next token is data
				# open tag with contents as next token
				tagname = re.findall("^\s*<([a-zA-z]+)>\s*$", self.__tokenPeek__())
				if (tagname[0] != "mail"):
					self.__consume__()
					self.thisEmail[tagname[0]] = self.__consume__()
				else:
					self.__consume__(appendXml=False)

			if re.search("^\s*<([a-zA-z]+)/>\s*$", self.__tokenPeek__()):
				# <emptyTag/>
				# empty tag
				# give email an empty tagname
				tagname = re.findall("^\s*<([a-zA-z]+)/>\s*$", self.__consume__())
				self.thisEmail[tagname[0]] = ""

			if re.search("^\s*</([a-zA-z]+)>\s*$", self.__tokenPeek__()):
				# </endTag>
				# end of valid open tag
				tag = re.findall("^\s*</([a-zA-z]+)>\s*$", self.__tokenPeek__())
				if tag[0] == "mail":
					self.__consume__(appendXml=False)
					break
				else:
					self.__consume__()

		self.__createTerm__()
		self.__createEmails__()
		self.__createDates__()
		self.__createRecs__()

	def __createTerm__(self):
		if self.thisEmail != {}:
			# sanitize output and write to term.txt
			id = self.thisEmail["row"]
			# subject line
			for term in re.split(" |[^a-zA-Z0-9\-_]*|&#[\d]+", self.thisEmail["subj"]):
				if len(term) > 2:
					self.term.write("s-" + term.lower() + ":" + id + "\n")
			# body
			for term in re.split(" |[^a-zA-Z0-9\-_]*|&#[\d]+", self.thisEmail["body"]):
				if len(term) > 2:
					self.term.write("b-" + term.lower() + ":" + id + "\n")

	def __createEmails__(self):
		if self.thisEmail != {}:
			id = self.thisEmail["row"]
			if id == "107":
				print(self.thisEmail["to"])
			if self.thisEmail["from"] != "":
				self.emails.write("from-" + self.thisEmail["from"] + ":" + id + "\n")
			if self.thisEmail["to"] != "":
				for emails in self.thisEmail["to"].strip().split(","):
					self.emails.write("to-" + emails + ":" + id + "\n")
			if self.thisEmail["cc"] != "":
				for emails in self.thisEmail["cc"].strip().split(","):
					self.emails.write("cc-" + emails + ":" + id + "\n")
			if self.thisEmail["bcc"] != "":
				for emails in self.thisEmail["bcc"].strip().split(","):
					self.emails.write("bcc-" + emails + ":" + id + "\n")

	def __createDates__(self):
		if self.thisEmail != {}:
			id = self.thisEmail["row"]
			if self.thisEmail["date"] != []:
				self.dates.write(self.thisEmail["date"] + ":" + id + "\n")

	def __createRecs__(self):
		if self.thisEmail != {}:
			if re.search("^<mail>", self.thisEmail["xml"]):
				sep = ":"
			else:
				sep = ":<mail>"
			self.recs.write(self.thisEmail["row"] + sep + self.thisEmail["xml"] + "\n")

	def __sortFiles__(self):
		os.system("sort terms.txt -u -o terms_sorted.txt")
		os.system("sort emails.txt -u -o emails_sorted.txt")
		os.system("sort dates.txt -u -o dates_sorted.txt")
		os.system("sort recs.txt -u -n -o recs_sorted.txt")


	## HELPER METHODS: ##

	def __openFiles__(self):
		self.term = open("terms.txt", mode = "w", encoding = "utf-8")
		self.emails = open("emails.txt", mode = "w", encoding = "utf-8")
		self.dates = open("dates.txt", mode = "w", encoding = "utf-8")
		self.recs = open("recs.txt", mode = "w", encoding = "utf-8")

	def __closeFiles__(self):
		self.term.close()

		self.emails.close()
		self.dates.close()
		self.recs.close()

	def __match__(self, pattern, appendXml=True):
		# check if the current token matches the pattern, increment current if so
		if not self.thisToken:
			self.thisToken = sys.stdin.readline()
			self.thisEmail["xml"] += self.thisToken.strip()
		if re.search(pattern, self.thisToken):
			self.thisToken = sys.stdin.readline()
			if appendXml:
				self.thisEmail["xml"] += self.thisToken.strip()
			return True
		return False

	def __tokenPeek__(self):
		return self.thisToken

	def __consume__(self, appendXml=True):
		tmp = self.thisToken
		self.thisToken = sys.stdin.readline()
		if appendXml:
			self.thisEmail["xml"] += self.thisToken.strip()
		return tmp


def main():
	parser = ParseMail()
	parser.execute()


if __name__ == "__main__":
	main()
