from psychopy import visual, event
import pickle
import sys
sys.path.append('..')
from psychopytools import Buttons
from spatialFuncs import procRec, dispOp, dispTBR
from sharedFuncs import RecButtons, genSpatialGrid, genTrials, calcOpsDur, dispInstructions, task, genInstructions, procVer


##################
#Parameters
letters = None
LetterStims = None
setSizes = [6, 6]
repsPerSize = 1

verPrompt = "Is this symmetrical?"
recPrompt = "Select the blocks in order.  Use the blank button to skip forgotten blocks."
##################

fname_stimDict = "stims.pickle"
f1 = open(fname_stimDict, "rb")
stimDict, keys_corr = pickle.load(f1)
f1.close()
win = visual.Window(fullscr = False, color = "white", units = 'pix')
myMouse = event.Mouse(win = win)
instruct_dir = ('instructions/pracTBR', 'instructions/pracOp', 'instructions/pracBoth', 'instructions/pracDone')
instructs = [genInstructions(win, fname) for fname in instruct_dir]

#INITIALIZE TRIALS
trialStims = genTrials(setSizes,repsPerSize, keys_corr, range(16))        #f([setsizes], repetitions per size, ops, TBR-options)
pracStims = genTrials([2], 2, keys_corr, range(16))
pracOps = genTrials([1], 10, keys_corr, range(16))
pracBoth = genTrials([2], 3, keys_corr, range(16))

##
#GENERATE SCREENS
#Response Grid
Rpos, Rwdth, Rhght, Rtxt = genSpatialGrid(400,400,4,4, optWdth = 100, optHght = 50, optDist = 50)
RecScreen = RecButtons(win, Rpos, Rwdth, Rhght, Rtxt,
               txtKwargs = {"color": "black"},
               lineColor = "black", fillColor = win.color, interpolate = False)

Prompt = visual.TextStim(win, text =  recPrompt, pos = (0, 250), color = "black")
procRec = procRec(win, myMouse, RecScreen, Prompt)

#Processing task Stimulus
Spos, Swdth, Shght, Stxt = genSpatialGrid(400*1.15,400,8,8)                  #Create grid without options buttons
OpGrid = Buttons(win, Spos, Swdth, Shght, Stxt,
                   lineColor = "black", interpolate = False)
dispOp = dispOp(win, OpGrid, stimDict)
#Verification Screen
VerText = visual.TextStim(win, text = verPrompt, color = "black", pos = (0, 150))
Vwdth, Vhght = 100, 50
VerScreen = Buttons(win,
                    [(-200 - Vwdth/2, 0), (200 - Vwdth/2, 0)],      #pos
                    [Vwdth]*2,                 #width
                    [Vhght]*2,                   #height
                    ["True", "False"],          #text
                    txtKwargs = {"color":"black"},
                    lineColor = "black", lineWidth = 3, interpolate = False)
procVer = procVer(win, myMouse, VerText, VerScreen)
#To Be Remembered Item
dispTBR = dispTBR(win, RecScreen, 'red')
#PARAMS
pars = dict(opsDur = 20,
            opsPracFeedbackTime = 1,
            screenBlankInterval = .25,
            TBRItemTime = .75,
            feedbackTime = 2,
            procRec = procRec,
            procVer = procVer,
            dispOp = dispOp,
            dispTBR = dispTBR)

#RUN TASK
dispInstructions(win, myMouse, instructs[0])                                            #Practice TBR Item and Recall 
task(win, myMouse, pracStims, TBROnly = True, **pars)
dispInstructions(win, myMouse, instructs[1])                                            #Practice Ops and calc ops duration
task(win, myMouse, pracOps, opsOnly = True, opsFeedback = True, **pars)

RTs = [trial['op.RT.W'][0] for trial in pracOps.trialList]                              #get RTs for practice ops
print RTs
opsDur = calcOpsDur(RTs, trimNum = 2)
print opsDur
opsDur = opsDur[1]

dispInstructions(win, myMouse, instructs[2])                                            #Practice both
task(win, myMouse, pracBoth, opsDur = opsDur, **pars)
dispInstructions(win, myMouse, instructs[3])                                             #Actual Task
task(win, myMouse, trialStims, opsDur = opsDur, **pars)
win.close()

#Output data
trialStims.saveAsWideText('data/testout.tsv')
