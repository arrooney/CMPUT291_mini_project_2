import sys, re


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
		while(self.__match__("^\s*(<mail>)|(<emails type=[\w\"\']*>)\s*$")):
			self.thisEmail.clear()
			self.__emailInfo__()
		self.__closeFiles__()

	def __emailInfo__(self):
		while(not self.__match__("^\s*</mail>\s*$")):
			if re.search("^\s*<([\w]+)>([\s\w/!@#$%^&*\.:\-,\?\(\)\"\'\+=\\/\[\]\{\}]+)?</[\w]+>\s*$", self.__tokenPeek__()):
				# <tag>data</tag>
				# this line contains 
				tagVal = re.findall("^\s*<([\w]+)>([\s\w/!@#$%^&*\.:\-,\?\(\)\"\'\+=\\/\[\]\{\}]+)?</[\w]+>\s*$", self.__consume__())
				self.thisEmail[tagVal[0][0]] = tagVal[0][1]

			if re.search("^\s*<([a-zA-z]+)>\s*$", self.__tokenPeek__()):
				# <tag>
				# next token is data
				# open tag with contents as next token
				tagname = re.findall("^\s*<([a-zA-z]+)>\s*$", self.__consume__())
				if (tagname[0] != "mail"):
					self.thisEmail[tagname[0]] = self.__consume__()

			if re.search("^\s*<([a-zA-z]+)/>\s*$", self.__tokenPeek__()):
				# <emptyTag/>
				# empty tag
				# give email an empty tagname
				tagname = re.findall("^\s*<([a-zA-z]+)/>\s*$", self.__consume__())
				self.thisEmail[tagname[0]] = ""

			if re.search("^\s*</([a-zA-z]+)>\s*$", self.__tokenPeek__()):
				# </endTag>
				# end of valid open tag
				tag = re.findall("^\s*</([a-zA-z]+)>\s*$", self.__consume__())
				if tag[0] == "mail":
					break
		self.__createTerm__()

	def __createTerm__(self):
		if self.thisEmail != {}:
			# sanitize output and write to term.txt
			id = self.thisEmail["row"]
			# subject line
			for term in self.thisEmail["subj"].split(" "):
				term = re.sub("[^a-zA-Z0-9\-_]*|&#[\d]+", "", term)
				if len(term) > 2:
					self.term.write("s-" + term.lower() + ":" + id + "\n")
			# body
			for term in self.thisEmail["body"].split(" "):
				term = re.sub("[^a-zA-Z\-_]*|&#[\d]+", "", term)
				if len(term) > 2:
					self.term.write("b-" + term.lower() + ":" + id + "\n")


	## HELPER METHODS: ##

	def __openFiles__(self):
		self.term = open("term.txt", mode = 'w', encoding = 'utf-8')

	def __closeFiles__(self):
		self.term.close()

	def __match__(self, pattern):
		# check if the current token matches the pattern, increment current if so
		if not self.thisToken:
			self.thisToken = sys.stdin.readline()
		if re.search(pattern, self.thisToken):
			self.thisToken = sys.stdin.readline()
			return True
		return False

	def __tokenPeek__(self):
		return self.thisToken

	def __consume__(self):
		tmp = self.thisToken
		self.thisToken = sys.stdin.readline()
		return tmp


def main():
	parser = ParseMail()
	parser.execute()


if __name__ == "__main__":
	main()
