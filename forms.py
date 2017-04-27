class Form (object) :
	def __init__(self, fields=[], title="", action="", submit=""):
		if not submit:
			submit=title
		self.fields=fields
		self.title=title
		self.action=action
		self.submit=submit


