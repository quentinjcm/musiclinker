import maya.cmds as cmds
import fileBrowser as fb


class mlUI(object):
	"""
	A user interface class for the music linker for reading audio files, 
	separating usefual parts of the audio and attaching them to attributes
	of objects in maya (lights, geo etc)
	"""
	def __init__(self):
		"""
		Thie initialising function sets the widgets dictionary and runs the
		main ui function to build and show the ui.

		self:		Class instance being initialised
		"""
		self.widgets = {}
		self.win_name = "music_linker"
		self.win_w = 400
		self.win_h = 700
		self.buildUI()

	def buildUI(self):
		"""
		This is the main ui building function that runs the functions for
		building each of the seperate parts of the ui.

		self: 		Current class instance
		"""
		#checking for previous instances of the window and deleting them
		if cmds.window(self.win_name, ex = True):
			cmds.deleteUI(self.win_name)
		#setting attributes for the main window
		self.widgets["main_win"] = cmds.window(
										self.win_name,
										t = "Music Linker",
										w = self.win_w, 
										h = self.win_h,
										mnb = False,
										mxb = False)
		self.widgets["main_lay"] = cmds. columnLayout(
										w = self.win_w,
										h = self.win_h,
										p = self.widgets["main_win"])
		#place section building functions here
		self.buildWavBrowser()

		#displaying the window
		cmds.showWindow(self.widgets["main_win"])

	def buildWavBrowser(self):
		"""
		builds a wav browser field for selecting and importing a wav file.

		self:		Current class instance
		"""
		self.widgets["browser_lay"] = cmds.frameLayout(
													l = ".wav file browser",
                                                    p = self.widgets["main_lay"],
                                                    fn = "boldLabelFont",
                                                    mw = 20, mh = 5, w = 400)
		self.widgets["wav_browser"] = fb.fileBrowser(
													self.widgets["browser_lay"],
													".wav")
		cmds.button(l = "Import .wav file to timeline",
					p = self.widgets["browser_lay"],
					c = self.importWav)

	def importWav(self, *args):
		"""
		function that is run when the 'import .wav file' button is pressed
		""" 

		print self.widgets["wav_browser"].path
		try:
			self.widgets["audio"] = cmds.sound(f = self.widgets["wav_browser"].path, o = 1)
		except IndexError:
			cmds.confirmDialog(
							t = "No audio selected",
							m = "Please open the file browser and select a .wav file")
		except RuntimeError:
			cmds.confirmDialog(
							t = "No audio selected",
							m = "Please select a valid .wav file")



def run():
	return mlUI()
