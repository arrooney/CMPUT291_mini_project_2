import sys, re


class parseMail(object):

	# CONSTRUCTOR:
	def __init__(self):
		self.thisEmail = {}
		self.current = 0
		self.thisToken = None

	## PUBLIC METHODS: ##

	def execute(self):
		# public entry point to the parser
		self.__mail__()

	## PRIVATE METHODS: ##

	def __mail__(self):
		while(self.__match__("^\s*(<mail>)|(<emails type=[\w\"\']*>)\s*$")):
			self.thisEmail.clear()
			self.__emailInfo__()

	def __emailInfo__(self):
		while(not self.__match__("^\s*</mail>\s*$")):
			if re.search("^\s*<([\w]+)>([\s\w/!@#$%^&*\.:\-,\?\(\)\"\'\+=\\/\[\]\{\}]+)</[\w]+>\s*$", self.__tokenPeek__()):
				# this line contains 
				tagVal = re.findall("^\s*<([\w]+)>([\s\w/!@#$%^&*\.:\-,\?\(\)\"\'\+=\\/\[\]\{\}]+)</[\w]+>\s*$", self.__consume__())
				self.thisEmail[tagVal[0][0]] = tagVal[0][1]
			if re.search("^\s*<([a-zA-z]+)>\s*$", self.__tokenPeek__()):
				# open tag with contents as next token
				tagname = re.findall("^\s*<([a-zA-z]+)>\s*$", self.__consume__())
				self.thisEmail[tagname[0]] = self.__consume__()
			elif re.search("^\s*<([a-zA-z]+)/>\s*$", self.__tokenPeek__()):
				# empty tag
				# give email an empty tagname
				tagname = re.findall("^\s*<([a-zA-z]+)/>\s*$", self.__consume__())
				self.thisEmail[tagname[0]] = ""
			elif re.search("^\s*</([a-zA-z]+)>\s*$", self.__tokenPeek__()):
				# end of valid open tag
				tag = re.findall("^\s*</([a-zA-z]+)>\s*$", self.__consume__())
				if tag[0] == "mail":
					break
		print(self.thisEmail)

	## HELPER METHODS: ##

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
	parser = parseMail()
	parser.execute()


if __name__ == "__main__":
	main()
