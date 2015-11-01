import maya.cmds as cmds


class fileBrowser(object):
	"""
	A class whcih creates a file browser box, parented under a given 
	window section
	"""
	def __init__(self, parent, filter):
		"""
		Creating the file browser widget

		self:		Instance being initialised
		parent: 	The parent ui element
		filter: 	the file filter to be used in the search
		"""
		self.path = ""
		self.parent = parent
		self.file_path = cmds.textField(
								tx = "/path/to/file",
								p = parent)
		cmds.button(
				l = "open file browser",
				c = self.openBrowser,
				p = parent)

	def openBrowser(self, *kwargs):
		"""
		function run when the file browser button is clicked

		self:		Class instance
		*kwargs:	arguments passed by the cmds button command
		"""
		default_path = cmds.workspace(
									q = True,
									rd = True)
		try:
			self.path = cmds.fileDialog2(
									ds = 2, 
									dir = default_path, 
									fm = 1, 
									ff = "*.wav")[0]
			print self.path
		except TypeError:
			print "TypeError"
			self.path = "/path/to/file"
		#updating the text in the text field
		cmds.textField(self.file_path, e = True, tx = self.path)
