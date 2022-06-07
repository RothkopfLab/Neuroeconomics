from psychopy import visual, core, event, gui
import random
import numpy as np
import pandas as pd
import string
import time
from datetime import datetime
import pylab as plt
from matplotlib.ticker import MaxNLocator


# Mouse | Tobii | SMI
GAZE = "Mouse"
# None or SMI
EYE = "None"

shallRecord = False
maxDelay = 30
minDelay = 0
testCircle = True
#### fill out this before experiment 
partName = "CEM-CDC-Test"

screen_width = 1920
screen_height = 1080

if EYE == "None":
    def gaze():
        return mouse.getPos()
elif EYE == "SMI":
    from iViewXAPI import  *
    res = iViewXAPI.iV_SetLogger(c_int(1), c_char_p("iViewXSDK_Python_GazeContingent_Demo.txt"))
    res = iViewXAPI.iV_Connect(c_char_p('127.0.0.1'), c_int(4444), c_char_p('127.0.0.1'), c_int(5555))

    res = iViewXAPI.iV_GetSystemInfo(byref(systemData))
    print "iV_GetSystemInfo: " + str(res)
    print "Samplerate: " + str(systemData.samplerate)
    print "iViewX Verion: " + str(systemData.iV_MajorVersion) + "." + str(systemData.iV_MinorVersion) + "." + str(systemData.iV_Buildnumber)
    print "iViewX API Verion: " + str(systemData.API_MajorVersion) + "." + str(systemData.API_MinorVersion) + "." + str(systemData.API_Buildnumber)

    def gaze():
        res = iViewXAPI.iV_GetSample(byref(sampleData))
        gazeX = 0
        gazeY=0
        if res == 1:
            gazeX = sampleData.leftEye.gazeX - screen_width/2
            gazeY = -1 * (sampleData.leftEye.gazeY - screen_height/2)
        return (gazeX, gazeY)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Generate random file ids"""
    return ''.join(random.choice(chars) for _ in range(size))


class Dot:
    """ Stimulus in the experiment """
    def __init__(self, win, radius, fillColor ="#000000",fillColorActive =
                 "#ff0000", lineColor  ="#000000", radiusIn = 10):
        self.s = visual.Circle(win = win , radius = radius,
                               fillColor = fillColor,
                               lineColor = lineColor)
        self.sin = visual.Circle(win = win , radius = radiusIn,
                               fillColor = "gray",
                               lineColor = "#000000")

        self.fillColor = fillColor
        self.fillColorActive = fillColorActive
        self.radius = radius

    def draw(self):
        self.s.draw()
        self.sin.draw()

    def setPos(self, pos):
        self.s.setPos(pos)
        self.sin.setPos(pos)

    def reset(self):
        self.s.setRadius(self.radius)

    def setRadius(self, perc):
        self.s.setRadius(int(self.radius - perc))


class Controller:

    def __init__(self, dots, timeThresActive, timeThresPassive, radiusDecay,
            distanceThres, minDelay=0, maxDelay=30):
        self.timeThres = timeThresActive
        self.timeThresActive = timeThresActive
        self.timeThresPassive = timeThresPassive
        self.dots = dots
        self.s = [np.array([0.0,0.0]) for i in range(len(dots))]
        self.gazePos = np.array([0,0])
        self.counter = [0 for i in range(len(dots))]
        self.distanceThres = distanceThres
        self.blank = True
        self.stepCounter = -1
        self.minDelay =  minDelay
        self.maxDelay = maxDelay

    def getClosest(self):
        dists = [np.linalg.norm(self.gazePos - a) for a in self.s]
        return (np.argmin(dists), np.min(dists))

    def setRandom(self):
        # +-12 deg
        self.s = [np.random.uniform(- 412, 412, 2) for i in range(len(self.s))]
        while (np.min([np.linalg.norm(a) for a in self.s]) < self.distanceThres)\
                or (np.max([np.linalg.norm(a) for a in self.s]) > 412):
            self.s = [np.random.uniform(- 412, 412, 2) for i in range(len(self.s))]
        self.blank = True

    def startTrial(self):
        self.stepCounter = 0

    def setInit(self):
        self.s = [np.random.uniform(5000, 6000, 2) for i in range(len(self.s))]
        self.s[0] = np.array([0,0])
        self.blank = False
        self.stepCounter += 1

    def update(self, gazePos):
        self.gazePos = gazePos
        n, d = self.getClosest()

        if self.s[0][0] == 0:
            self.timeThres = self.timeThresActive
        else:
            self.timeThres = self.timeThresPassive

        change = 0
        if d < self.distanceThres:
            if self.counter[n] == 0:
                self.counter = [0 for i in range(len(self.dots))]
            self.counter[n] += 1
#            for i in range(len(self.dots)):
#                self.dots[i].setRadius(self.counter[i])

        if np.max(self.counter) > self.timeThres:
            change = 1
            if self.s[0][0] == 0:
                self.timeThresActive = random.randint(self.minDelay, self.maxDelay)
            [self.dots[i].reset() for i in range(len(self.dots))]
            if self.blank:
                self.setInit()
            else:
                self.setRandom()
            self.counter = [0 for i in range(len(self.dots))]

        for dot,pos in zip(self.dots, self.s):
            dot.setPos(tuple(pos))

        return change, self.timeThresActive

def getMouse():
    return mouse.getPos()

# the window everything is put in
WIN_WIDTH = 500
WIN_HEIGHT = 500
# deactivate fullscreen on experiment laptop
win = visual.Window(size=(WIN_WIDTH, WIN_HEIGHT), units='pix', fullscr=True)

mouse = event.Mouse(visible=True)

# 24 -> 0.7 deg, 10 -> 0.3 deg
s1 = Dot(win, radius=24, fillColor="#000000", lineColor="#000000", radiusIn=3)
s2 = Dot(win, radius=24, fillColor="#000000", lineColor="#000000", radiusIn=3)

message = visual.TextStim(win, text='Block 0 \n \nStarten mit beliebiger Taste')
message.pos = (0, -200)
point = visual.Circle(win, radius = 15, fillColor = "#ff0000")
timeThresActive = random.randint(minDelay, maxDelay)
timeThresPassive = 20
cont = Controller([s1, s2], timeThresActive = timeThresActive,
                  timeThresPassive = timeThresPassive, radiusDecay = 2,
                  distanceThres = 100, minDelay=minDelay, maxDelay=maxDelay)

if EYE == "SMI":
    from Eyetracking import *
    
blocknr = 0
points = []
testCircle = visual.Circle(win, pos=(0,0), lineColor='#ff0000', radius=412)
while True:
    message.draw()
    win.flip()
    keys = event.waitKeys()
    if 'escape' in keys:
        break

    # start conditions
    data = []
    counter = 0
    trial = 0
    cont.setInit()
    cont.startTrial()
    partFile = partName + id_generator()

    if EYE == "SMI":
        startTrial(partFile)

    gazePos = gaze()
    mousePos = getMouse()
    change = 0
    stimCoords = cont.s
    stimCounts = cont.counter
    dat = {}
    dat["change"] = change # one if new location is chosen, zero otherwise
    dat["time"] = time.clock() * 1000 # current time
    dat["trial"] = trial # trial number, increases with every change
    dat["s1x"] = stimCoords[0][0] # location of stim1
    dat["s1y"] = stimCoords[0][1]
    dat["s2x"] = stimCoords[1][0] # location of stim2
    dat["s2y"] = stimCoords[1][1]
    dat["s1Count"] = stimCounts[0] # number of timesteps spent at s1
    dat["s2Count"] = stimCounts[1] # number of timesteps spent at s2
    dat["gazeX"] =  gazePos[0] # current gaze x
    dat["gazeY"] =  gazePos[1] # current gaze y 
    dat["mouseX"] =  mousePos[0] # current gaze x
    dat["mouseY"] =  mousePos[1] # current gaze y 

    dat["method"] = GAZE # method of input
    dat["partName"] = partName # name of participant
    dat["partFile"] = partFile # name of file
    dat["timeThresActive"] = timeThresActive # name of file
    dat["timeThresPassive"] = timeThresPassive # name of file
    dat["stepCounter"] = cont.stepCounter # number of decision
    dat["expdate"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data.append(dat)

    while counter < 3600:
        counter += 1
        keys =  event.getKeys()

        gazePos = gaze()
        mousePos = getMouse()

        if GAZE == "SMI":
            point.setPos(gazePos)
            change, timeThresActive = cont.update(gazePos)
        elif GAZE == "Mouse":
            point.setPos(mousePos)
            change, timeThresActive = cont.update(mousePos)

        if testCircle:
            testCircle.draw()

        #point.draw()
        # check if center is fixated
        if GAZE == "Mouse" and EYE == "SMI":
           if np.linalg.norm(gazePos) > 200:
                win.color = "#550000"
                win.flip()
                win.flip()
                keys = event.waitKeys()
        win.color = "#555555"

        s1.draw()
        s2.draw()
        if 'escape' in keys:
            break

        stimCoords = cont.s
        stimCounts = cont.counter

        trial = trial + change
        dat = {}
        dat["change"] = change # one if new location is chosen, zero otherwise
        dat["time"] = time.clock() * 1000 # current time
        dat["trial"] = trial # trial number, increases with every change
        dat["s1x"] = stimCoords[0][0] # location of stim1
        dat["s1y"] = stimCoords[0][1]
        dat["s2x"] = stimCoords[1][0] # location of stim2
        dat["s2y"] = stimCoords[1][1]
        dat["s1Count"] = stimCounts[0] # number of timesteps spent at s1
        dat["s2Count"] = stimCounts[1] # number of timesteps spent at s2
        dat["gazeX"] =  gazePos[0] # current gaze x
        dat["gazeY"] =  gazePos[1] # current gaze y 
        dat["mouseX"] =  mousePos[0] # current gaze x
        dat["mouseY"] =  mousePos[1] # current gaze y 

        dat["method"] = GAZE # method of input
        dat["partName"] = partName # name of participant
        dat["partFile"] = partFile # name of file
        dat["timeThresActive"] = timeThresActive # name of file
        dat["timeThresPassive"] = timeThresPassive # name of file
        dat["stepCounter"] = cont.stepCounter # number of decision
        dat["expdate"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data.append(dat)

        win.flip()
        if counter % 4 == 0 and shallRecord:
            win.getMovieFrame()

    blocknr += 1
    points.append(trial)
    message.setText(str(trial) + " Punkte \n \n" + "Block: " + str(blocknr) + "\n\n" +
            "Starten mit beliebiger Taste")
    plt.plot(range(1, len(points)), points[:-1], '-x', color='black')
    plt.plot(len(points), points[-1], '-x', color='white')
    axes = plt.gca()
    axes.set_ylim([min(points)-3, max(points)+3])
    axes.set_xlim(0.5, len(points)+0.5)
    axes.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xlabel('Trial')
    plt.ylabel('Gesammelte Targets')
    plt.savefig('points.png', transparent=True)
    plotStim = visual.ImageStim(win, 'points.png')
    plotStim.pos = (0, 200)
    plotStim.draw()
    
    if EYE == "SMI":
        saveTrial()
    df =  pd.DataFrame(data)
    df.to_csv(partFile +  ".csv")
    if shallRecord:
        win.saveMovieFrames(partFile + ".mov")
win.close()
