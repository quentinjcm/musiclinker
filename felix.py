import maya.cmds as cmds
import random

def UI():
	'''creates a UI for speaker system, containing a loading bar, followed by checkboxes
	for placing a curve, lights, sound bars, setting the particles and light to the same
	colour and a box to check for smoother colour transitions.
	it also contains sliders for particle emission strength and emission threshold, and
	a slider to change the amplitude threshold for changing the colour.
	'''
	windowName = "SpeakerSystem"
	#delete window if it already exists
	if cmds.window(windowName, exists=True):
		cmds.deleteUI(windowName)
	
	#create window
	cmds.window(windowName, s=False)
	cmds.columnLayout(adj=True)
	
	#create progress bar at top of window
	progressName = "progress"
	progressBar = cmds.progressBar("progress")
	
	#check box for curve
	curveOn = cmds.checkBox(label="curve", value=False)
	#check box for lights
	lightOn = cmds.checkBox(label="lights", value=True)
	#check box for bars
	barsOn = cmds.checkBox(label="bars", value=False)
	#check box for same colour particles and lights
	sameCol = cmds.checkBox(label="same colour lights and particles", value=True)
	#checl box for smooth colour change
	smoothCol = cmds.checkBox(label="smooth colour transitions", value=True)
	
	#slider for particle strength
	particleStr = cmds.intSliderGrp(label="particle strength", maxValue=15, minValue=0, value=7, field=True)
	
	#slider for particle threshold
	particleThres = cmds.floatSliderGrp(label="particle emission threshold", maxValue=1.0, minValue=0.0, value=0.4, field=True)
	
	#slider for colour threshold
	colorThres = cmds.floatSliderGrp(label="colour change threshold", maxValue=1.0, minValue=0.0, value=0.2, field=True)
	
	#text field for file path and button for user to find file
	fieldPath = cmds.textField("path")
	cmds.button(label="browse for audio source file...", command=fileBrowse)
	
	#create speaker system button
	cmds.button(label="create speaker system", command=lambda *args: main(windowName,
	                                                                      cmds.textField(fieldPath, query=True, text=True),
	                                                                      cmds.checkBox(curveOn, query=True, value=True),
	                                                                      cmds.checkBox(lightOn, query=True, value=True),
	                                                                      cmds.checkBox(barsOn, query=True, value=True),
	                                                                      cmds.checkBox(sameCol, query=True, value=True),
	                                                                      cmds.checkBox(smoothCol, query=True, value=True),
	                                                                      cmds.intSliderGrp(particleStr, query=True, value=True),
	                                                                      cmds.floatSliderGrp(particleThres, query=True, value=True),
	                                                                      cmds.floatSliderGrp(colorThres, query=True, value=True),
	                                                                      progressName
	                                                                      ))
	
	#show the window to the user
	cmds.showWindow(windowName)

def fileBrowse(*pArgs):
	'''finds a .wav file path by opening a file browsing window
	'''
	#open file browser to get desired file from user
	foundFilePath = cmds.fileDialog2(fileFilter="Wav Files (*.wav)", fileMode=1, okCaption="OK")
	try: 
		#put file path into text field in window
		cmds.textField("path", e=True, text=foundFilePath[0])
	#if user doesn't specify a file, leave text field blank
	except TypeError:
		cmds.textField("path", e=True, text="")

def main(windowName, filePath, curveOn, lightOn, barsOn, sameCol, smoothCol, particleStr, particleThres, colorThres, progressName):
	'''creates the components specified by the user, on top of a speaker system that scales relative to the amplitude of the audio.
	
	windowName    : the name of the window used as UI
	filePath      : the location of the audio file to be used
	curveOn       : boolean specifying whether the user has requested a curve
	lightOn       : boolean specifying whether the user has requested lights
	barsOn        : boolean specifying whether the user requested bars
	sameCol       : boolean specifying whether the particles and the light should be the same colours
	smoothCol     : boolean specifying whether the user desires colour changes to be smoother or sudden
	particleStr   : rate and speed of the particle emission, can be set to 0 to turn particles off
	particleThres : amplitude threshold for particle emission
	colorThres    : amplitude threshold for color emission
	progressName  : name of the progress bar to update
	'''
	#if a file path is given
	if filePath:
		
		#empty list used for grouping everything at end
		componentList = []
		colorItemList = []
		
		#calculate progress bar size needed
		maxProgress = curveOn + lightOn + 100 * barsOn + sameCol + bool(particleStr) + 3
		#change max value of progress bar
		cmds.progressBar(progressName, edit=True, minValue=0, maxValue=maxProgress)
		
		######increment progress bar######
		cmds.progressBar(progressName, edit=True, step=1)
		
		#delete all objects in scene
		cmds.select(all=True)
		cmds.delete()
		#find name of audio file used
		fileName = findFileName(filePath)
		#import sound and get length
		audioNode = importSound(filePath)
		if(audioNode):
			audioLength = int(cmds.getAttr(fileName + ".duration"))
			
			######increment progress bar######
			cmds.progressBar(progressName, edit=True, step=1)
			
			#create list of amplitude at each frame
			ampList = createAverageAmpList(audioNode, audioLength)
			
			#create speaker
			speakerShapeGroup, position = createSpeakerGroup(ampList, audioLength)
			
			######increment progress bar######
			cmds.progressBar(progressName, edit=True, step=1)
			
			componentList.append(speakerShapeGroup)
			
			#sound curve
			if curveOn:
				curve = createCurve(position, ampList, audioLength)
				######increment progress bar######
				cmds.progressBar(progressName, edit=True, step=1)
				
				componentList.append(curve)
			
			#speaker light
			if lightOn:
				speakerLight = createLight(position, ampList, audioLength)
				if sameCol == False:
					randomiseColor([speakerLight], ampList, audioLength, smoothCol, colorThres)
				else:
					colorItemList.append(speakerLight)
				######increment progress bar######
				cmds.progressBar(progressName, edit=True, step=1)
				
				componentList.append(speakerLight)
			
			#particles
			if particleStr:
				particleEmitter, particles, particleShader = createParticles(position, ampList, audioLength, particleStr, particleThres)
				colorItemList.append(particleShader)
				if sameCol == False:
					randomiseColor([particleShader], ampList, audioLength, smoothCol, colorThres)
				else:
					colorItemList.append(particleShader)
				######increment progress bar######
				cmds.progressBar(progressName, edit=True, step=1)
				
				componentList.append(particleEmitter)
				componentList.append(particles)
			
			#randomise itemList colours
			if sameCol == True:
				randomiseColor(colorItemList, ampList, audioLength, smoothCol, colorThres)
				######increment progress bar######
				cmds.progressBar(progressName, edit=True, step=1)
			
			#audio bars
			if barsOn:
				barGroup = createBars(audioNode, audioLength, 10, 10, progressName)
				#if lights are on, create one to illuminate the bars
				if lightOn:
					barLight = cmds.duplicate(speakerLight, un=True)
					cmds.move(0,47,0, barLight, r=True)
					componentList.append(barLight[0])
				componentList.append(barGroup)
			
			cmds.group(componentList, name="speakerSystem")
			#set playback to length of audio
			cmds.playbackOptions(min=1, max=audioLength)
			
			#print cmds.modelEditor( cmds.getPanel(wf=True), q=True, rnm=True )
			#cmds.modelEditor(cmds.getPanel(wf=True), rnm="hwRender_OpenGL_Renderer")
			cmds.deleteUI(windowName)
		else:
			cmds.confirmDialog(title="No File Found!",button="ok", message="Can't find file!")
	else:
		cmds.confirmDialog(title="No File Found!",button="ok", message="Please specify a file!")

def findFileName(filePath):
	'''the name of the audio file is required for the program to work. however it is difficult to acquire this
	as it is returned by a MEL command called in the importing of the audio node. so i created a function to
	read the file path and extract the name of the audio file.
	
	filePath : the desired file, including path and extension
	
	return   : the name of the file without the path or extension
	'''
	
	i=len(filePath)
	#create an empty string
	fileNameReverse = ""
	#iterate backwards through the string
	while i > 0:
		i-=1
		#once it finds the '.' then that's the extension point
		if filePath[i] == '.':
			i-=1
			#take all characters between the '.' and the first '/' found and add them to the string
			while filePath[i] != '/':
				fileNameReverse+=filePath[i]
				i-=1
	#reverse the string found
	fileName = fileNameReverse[::-1]
	return fileName

def importSound(filePath):
	'''imports sound file, creates an audio node, connects it to time and returns it.
	
	filePath : the location of the audio file to import
	
	return   : the created audio node
	'''
	try:
		#place sound file on the time slider, to play while the speaker moves
		cmds.file(filePath, i=True)
	#if the file can't be opened, return False
	except RuntimeError:
		return False
	
	#create the audio node
	audioNode = cmds.createNode("audioWave")
	#connect the audio node to the source file
	cmds.setAttr(audioNode + ".audio", filePath, type="string")
	cmds.setAttr(audioNode + ".sampleSize", 20)
	
	#connect the audio node to the time slider
	cmds.connectAttr("time1.outTime", audioNode+".input")
	return audioNode

def createAverageAmpList(audioNode, audioLength):
	'''create a list of amplitudes, averaged over each frame, to use as drivers for various values.
	
	audioNode   : the audio node to read
	audioLength : number of frames the node covers
	
	return      : list of float amplitudes
	'''
	#create empty list
	ampList = []
	#find average amplitude of each frame
	for i in range(audioLength):
		totalAmp = 0
		for j in range(10):
			#find the amplitude at 10 steps through the frame
			trueAmplitude = cmds.getAttr(audioNode + ".output", time=i+1)
			#convert the amplitude to 'heard' amplitude
			amplitude = abs(0.5-trueAmplitude)
			totalAmp += amplitude
		finalAmp = 1.5 * (totalAmp / 10)
		#add average amplitude to list
		ampList.append(finalAmp)
	return ampList

def createCurve(position, ampList, audioLength):
	'''create an audio curve based on a list of amplitudes, which will represent the value
	of the audio across time, and will move through the position at that time.
	
	position    : starting position of curve end
	ampList     : list of amplitudes to drive the height of the points of the curve
	audioLength : length of the audio, in frames
	'''
	#empty list to store points
	pointList = []
	#for each frame in the audio
	for i in range(audioLength):
		#calulate position of point on curve based on start positon given and amplitude of audio
		point = (position[0]+i, position[1]+ampList[i]*20-2, position[2])
		#add point to list
		pointList.append(point)
	#create curve from list of points
	audioCurve = cmds.curve(p=pointList)
	#key frame the curve to move through the given position over the time it takes for the audio to play
	cmds.setKeyframe(audioCurve, attribute="translateX", value=0, time=1, outTangentType="linear")
	cmds.setKeyframe(audioCurve, attribute="translateX", value=-audioLength, time=audioLength, inTangentType="linear")
	return audioCurve

def createSpeakerGroup(ampList, audioLength):
	'''create a speaker driven by the list given, made up of a box and a cylinder.
	
	ampList     : list of floats to drive scale of speaker
	audioLength : length of amplitude list
	
	return      : group created and position of the cylinder
	'''
	#create the speaker box
	box = createBox()
	#create the speaker itself
	speaker = createSpeaker()
	#drive speaker based on sound
	soundToScale(speaker, ampList, audioLength)
	#group two objects then rotate the group
	speakerShapeGroup = cmds.group(box, speaker, name="speakerShapeGroup")
	cmds.xform(speakerShapeGroup, rotation=(0,0,90))
	#drive group by sound, by only a small degree. this makes the entire box and speaker bounce with the music
	soundToScale(speakerShapeGroup, ampList, audioLength, 20)
	#find position of speaker cone
	position = cmds.xform(speaker, q=True, translation=True, ws=True)
	return speakerShapeGroup, position

def createBox():
	'''create a box of the correct size and move it the correct position.
	
	return : the name of the created box
	'''
	#create box
	box = cmds.polyCube(w=2.4, d=1.5, h=1.5)
	#move to position
	cmds.xform(box, translation=(0.2,-0.75,0))
	return box

def createSpeaker():
	'''create a speaker shape to be used as a sound visualiser.
	
	return : name of the cylinder created
	'''
	#create cylinder
	speaker = cmds.polyCylinder(h=0.025, r=0.5)
	#extrude to create 'speaker' shape
	cmds.polyExtrudeFacet(speaker[0]+".f[21]", scale=(0.8,0.8,0.8))
	cmds.polyExtrudeFacet(speaker[0]+".f[21]", scale=(0.5,0.5,0.5), translate=(0,-0.2,0))
	cmds.polyExtrudeFacet(speaker[0]+".f[21]", translate=(0,0.1,0))
	return speaker

def soundToScale(shape, ampList, audioLength, damping=1):
	'''takes an object or similar, and keyframes its scale to match up with the values in ampList.
	
	shape       : the item to scale
	ampList     : the list of float values with which to scale the shape
	audioLength : number of frames to go through
	weight      : a value used to limit the variation in scaling, although it will increase the average scale
	'''
	#for each frame in the audio
	for i in range(audioLength):
		#calculate a scale factor
		sf = damping + ampList[i]*2
		#scale the shape
		cmds.xform(shape, scale=(sf, sf, sf))
		#keyframe the shape's scale
		cmds.setKeyframe(shape, attribute="scale", time=i)

def createBars(audioNode, audioLength, numOfBarsX, numOfBarsZ, progressName):
	'''creates a grid of bars where each row contains a reading of the audioNode across the frame.
	
	audioNode    : audio to read
	audioLength  : number of frames the node covers
	numOfBarsX   : number of bars desired in X direction
	numOfBarsZ   : number of bars desired in Z direction
	progressName : name of the progress bar to be updated
	
	return      : a group containing the created bars
	'''
	#set default bar height
	barHeight = 20
	#empty list to add bars to
	barList = []
	#row of bars for each frame
	for i in range(numOfBarsZ):
		#across the row, each bar reads from a section of audio in that frame
		for j in range(numOfBarsX):
			#create a cube
			bar = cmds.polyCube(w=3, h=barHeight, d=3)
			#move it based on the iteration, to get a grid of bars
			cmds.move(j*3,barHeight/2.0,i*3, bar)
			#set the bar height at time:0 to 0
			cmds.xform(bar, scalePivot=(0,0,0), ws=True)
			cmds.setKeyframe(bar, attribute="scaleY", value=0, time=0)
			#for each frame, find the audio amplitude at the frame + an offset determined by iteration
			for k in range(j,audioLength):
				#get amplitude and convert it to more readable form
				trueAmplitude = cmds.getAttr(audioNode + ".output", time=k-j+float(i)/numOfBarsZ)
				amplitude  = abs(0.5-trueAmplitude)
				#set scale factor to amplitude squared to exaggerate the scale factor
				sf = amplitude*2
				#keyframe the scale at the appropriate frame
				cmds.setKeyframe(bar, attribute="scaleY", value=sf, time=k)
			#once the bar is keyframed, add it to the list
			barList.append(bar[0])
			######increment progress bar######
			cmds.progressBar(progressName, edit=True, step=1)
	
	#group the created bars
	barGroup = cmds.group(barList, name='barGroup')
	#move the group to the position above the speaker
	cmds.move(-13.174997772,23,-13.5, barGroup)
	return barGroup

def createParticles(position, ampList, audioLength, particleStr, threshold):
	'''create a basic particle system with an emitter and particles, where the colour, emission rate
	and emission speed depends on the amplitude list and particle strength.
	
	position    : the position to place the particles
	ampList     : list of amplitudes to control particle speed and emission
	audioLength : the length of the audio, in frames
	particleStr : value to weight the emission rate of particles
	threshold   : minimum value required for particle emission
	'''
	cmds.select(d=True)
	#create emitter
	particleEmitter = cmds.emitter(type="direction", r=100, sro=0, dx=-1, dy=0, dz=0, sp=1, cye="Frame", cyi=25)
	#move emitter to position
	cmds.xform(particleEmitter, translation=position)
	#create particles
	particles = cmds.particle(p=position, conserve=0.99)
	#connect particles and emitter
	cmds.connectDynamic(particles, em=particleEmitter)
	
	#set particles' lifespan to random
	cmds.setAttr(particles[1]+".lifespanMode", 2)
	#change weight of random lifespans
	cmds.setAttr(particles[1]+".lifespanRandom", 2)
	#render particles as multistreaks
	cmds.setAttr(particles[1]+".particleRenderType", 1)
	
	#set particle emission rate and speed
	setParticleEmission(particleEmitter, ampList, audioLength, particleStr, threshold)
	
	#give particles a material
	particleShader = colorObject(particles)
	return particleEmitter[0], particles[1], particleShader

def setParticleEmission(particleEmitter, ampList, audioLength, particleStr, threshold):
	'''set and keyframe the emission rate of an emitter, varying depending on a list of amplitudes.
	
	particleEmitter : emitter to keyframe
	ampList         : list of amplitudes to drive the emission
	audioLength     : length of audio, in frames
	particleStr     : weight fot the emission rate
	threshold       : minimum value required for particle emission
	'''
	#for each frame in the audio
	for i in range(audioLength):
		#if the amplitude is too low, set emission to 0
		if ampList[i] < threshold:
			emitRate = 0
			emitSpeed = 0
		#otherwise set emission rate and speed to a value based on the amplitude list
		else:
			emitRate = (30 * ampList[i] * particleStr)**2
			emitSpeed = 550 * ampList[i]**2
		#keyframe the emission rate and speed
		cmds.setKeyframe(particleEmitter, attribute="speed", value=emitSpeed, time=i)
		cmds.setKeyframe(particleEmitter, attribute="rate", value=emitRate, time=i)

###########################
def colorObject(objName, materialName="lambert", materialColor=(0,0,0)):
	'''source from Xiaosong Yang's source.
	takes an object and creates and assigns a material to that object with the specified colour.
	
	objName       : name of object to assign shader to
	materialName  : type of material to create
	materialColor : color of the material
	
	return        : name of the shader created
	'''
	setName = cmds.sets(name='_MaterialGroup_', renderable=True, empty=True)
	# create a new shading node
	shaderName = cmds.shadingNode(materialName, asShader=True)
	# add to the list of surface shaders
	cmds.surfaceShaderList(shaderName, add=setName)
	# assign the material to the object
	cmds.sets(objName, edit=True, forceElement=setName)
	return shaderName

def createLight(position, ampList, audioLength):
	'''create a light at the position given, which changes colour based on the list of amplitudes given.
	
	position    : position to place the light
	ampList     : list of values to influence colour of light
	audioLength : length of the audio, in frames
	'''
	#create point light at position
	light = cmds.pointLight(position = (position[0]- 1.5, position[1], position[2]))
	#change the decay rate to quadratic
	cmds.setAttr(light+".decayRate", 2)
	#increase the intensity of the light
	cmds.setAttr(light+".intensity", 1500)
	return light

def randomiseColor(itemList, ampList, audioLength, smoothCol, threshold):
	'''keyframe the 'color' attribute of the given item to change at each frame that the corresponding
	value in ampList is higher than a threshold
	
	itemName    : item with a 'color' attribute to be keyframed
	ampList     : list of audio values to control the colour
	audioLength : length of audio, in frames
	threshold   : minimum value required for colour change
	'''
	#for each frame the audio covers
	for i in range(audioLength):
		#if the amplitude is above threshold
		if ampList[i] > threshold:
			#generate random rgb values
			red = random.random()
			green = random.random()
			blue = random.random()
			for item in itemList:
				#keyframe the colour to change to the rgb values at keyframes
				#depends on smooth colour option
				if smoothCol == True:
					cmds.setAttr(item+".color", red, green, blue, type="double3")
					cmds.setKeyframe(item, attribute="color", time=i, inTangentType="linear", outTangentType="linear")
				else:
					cmds.setKeyframe(item, attribute="color", time=i-1, inTangentType="flat", outTangentType="linear")
					cmds.setAttr(item+".color", red, green, blue, type="double3")
					cmds.setKeyframe(item, attribute="color", time=i, inTangentType="linear", outTangentType="flat")

if __name__ == "__main__":
	UI()
