from psychopy import visual, event
import pickle
import sys
sys.path.append('..')
from psychopytools import Buttons
from ospanFuncs import extendMe, procRec, dispOp, dispTBR
from sharedFuncs import genSpatialGrid, calcOpsDur, RecButtons, genTrials, dispInstructions, task, genInstructions, procVer


##################
#Parameters
fname_stimDict = "ostims.pickle"
letters =  [["F", "H", "J"],
            ["K", "L", "N"],
            ["P", "Q", "R"],
            ["S", "T", "Y"]]


verPrompt = ""
recPrompt = "Select the letters in order.  Use the blank button to fill in forgotten letters."

##################


f1 = open(fname_stimDict, "r")
stimDict = pickle.load(f1)
f1.close()
letters_flat = extendMe(letters)

#INITIALIZE TRIALS
trialStims = genTrials([6,6],1, stimDict, letters_flat)
pracStims = genTrials([2], 2, stimDict, letters_flat)
pracOps = genTrials([1], 10, stimDict, letters_flat)
pracBoth = genTrials([2], 3, stimDict, letters_flat)
win = visual.Window((1600, 1200), fullscr = False, color = "white", units = 'pix')
myMouse = event.Mouse(win = win)
instruct_dir = ('instructions/pracTBR', 'instructions/pracOp', 'instructions/pracBoth', 'instructions/pracDone')
instructs = [genInstructions(win, fname) for fname in instruct_dir]
##
#GENERATE STIMULI
#Response Grid
nrow, ncol = 4,3
boxHght, boxWdth = 50, 50
textHght = boxHght - 15
Rpos, Rwdth, Rhght, Rtxt, ltrPos = genSpatialGrid(600,450,nrow,ncol, optWdth = 125, optHght = 50, optDist = 200,
                                                  recWdth = boxWdth, recHght = boxHght,
                                                  letters = True, gridPos = (0, 100))

RecScreen = RecButtons(win, Rpos, Rwdth, Rhght, Rtxt,
               txtKwargs = {"color": "black", "height": textHght},
               lineColor = "black", fillColor = win.color, interpolate = False)

Prompt = visual.TextStim(win, text =  recPrompt, pos = (0, 450), color = "black")

LetterStims = []
for row in range(nrow):
    for col in range(ncol):
        LetterStims.append(visual.TextStim(win, text = " " + letters[row][col],
                                           pos = ltrPos[ncol*row + col],
                                           alignHoriz = "left",
                                           height = textHght,
                                           color = "black"))

#CREATE PROCEDURES
#Processing task Stimulus
OpStim = visual.TextStim(win, color = "black", height = textHght)
dispOp = dispOp(win, OpStim)
#Verification Screen
VerText = visual.TextStim(win, text = verPrompt, color = "black", pos = (0, 150), height = textHght)
Vwdth, Vhght = 100, 50
VerScreen = Buttons(win,
                    [(-200 - Vwdth/2, 0), (200 - Vwdth/2, 0)],      #pos
                    [Vwdth]*2,                 #width
                    [Vhght]*2,                   #height
                    ["True", "False"],          #text
                    txtKwargs = {"color":"black", "height" : textHght},
                    lineColor = "black", lineWidth = 5, interpolate = False, fillColor = "white")
procVer = procVer(win, myMouse, TxtStim = VerText, VerScreen = VerScreen)
#TBR
TBRStim = visual.TextStim(win, color = "black", height = textHght)
dispTBR = dispTBR(win, TBRStim, letters, color = 'black')
#Recall
procRec = procRec(win, myMouse, RecScreen, Prompt, LetterStims, letters)

pars = dict(screenBlankInterval = .25,
            opsPracFeedbackTime = 1,
            TBRItemTime = .75,
            feedbackTime = 2,
            procRec = procRec,
            procVer = procVer,
            dispOp = dispOp,
            dispTBR = dispTBR)

#RUN TASK
#Introduction
#Practice TBR Item and Recall
#dispInstructions(win, myMouse, instructs[0])
#task(win, myMouse, pracStims, kwargs_dict, opsDur = 60, TBROnly = True, **pars)
#Practice Ops and calc ops duration
dispInstructions(win, myMouse, instructs[1])
task(win, myMouse, pracOps, opsDur = 60, opsOnly = True, opsFeedback = True, **pars)
RTs = [trial['op.RT.W'][0] for trial in pracOps.trialList]                   #get RTs for practice ops
print RTs
opsDur = calcOpsDur(RTs, trimNum = 2)
print opsDur
##Practice both
dispInstructions(win, myMouse, instructs[2])
task(win, myMouse, pracBoth, opsDur = opsDur, **pars)
##Actual Task
dispInstructions(win, myMouse, instructs[3])
task(win, myMouse, trialStims, opsDur = opsDur, **pars)
win.close()
#Save Data
trialStims.saveAsWideText('data/testout.tsv')
