import os
from psychopy import event, core, visual, data
from collections import defaultdict
from psychopytools import Buttons
import random


class RecButtons(Buttons):         #Change method for responding to box selection
    def method(self, stim, stimNum):
        if stim.Text.text == "Clear":
            for entry in self.stimList[:-3]:
                entry.Rect.setFillColor(self.win.color)
                entry.Text.text = "0"
                entry.Text.setAutoDraw(False)
            self.respNum = 1
        elif stim.Text.text == "Submit":
            self.done = True
        elif stim.Text.text == "Blank":
            self.respNum += 1
        elif stim.Text.text == "0":
            stim.Rect.setFillColor("red")
            stim.Text.setText(self.respNum)
            stim.Text.setAutoDraw(True)
            self.respNum += 1
            return stim, stimNum
        else: return None
        return stim, stim.Text.text


#Diff
def genSpatialGrid(gridWdth, gridHght, nRow, nCol,
                   optWdth = None, optHght = None, optDist = None,
                   recHght = None, recWdth = None, letters = None, gridPos = (0,0)):
    #wdths and hghts are not calculated using floating point
    if recWdth: indWdth = recWdth
    else: indWdth = gridWdth/nCol     #box width
    if recHght: indHght = recHght
    else: indHght = gridHght/nRow
    colSpace = (gridWdth - nCol * indWdth) / (nCol - 1) #0 if recWdth = None
    rowSpace = (gridHght - nRow * indHght) / (nRow - 1) #0 if recHght = None (no space between boxes)
    pos = []
    ltrPos = []
    for row in range(nRow):
        for col in range(nCol):
            pos.append((-gridWdth/2 + col*(indWdth + colSpace),       #Set no space between boxes
                         gridHght/2 - row*(indHght + rowSpace)))
            if letters:
                ltrPos.append([-gridWdth/2 + col*(indWdth + colSpace) + indWdth,
                               gridHght/2 - row*(indHght + rowSpace) - indHght/2])
    indWdth = [indWdth]* (nRow*nCol)#[gridWdth/nCol] * (nRow*nCol)      #list with wdth for each box
    indHght = [indHght]* (nRow*nCol)#gridHght/nRow] * (nRow*nCol)
    txt = ["0"] * (nRow*nCol)                    #boxes are empty
    #Add Clear, Submit, and Blank buttons
    if optWdth:
        indWdth.extend([optWdth]*3)
        indHght.extend([optHght]*3)
        pos.extend(
                    [( (-gridWdth)/2 - optWdth/2, -gridHght/2 - optDist),
                     ( ( gridWdth)/2 - optWdth/2, -gridHght/2 - optDist),
                     ( ( 0 - optWdth/2, -gridHght/2 - optDist/3))])
        txt.extend(["Clear", "Submit", "Blank"])
    if gridPos != (0,0):
        pos = [(indPos[0] + gridPos[0], indPos[1] + gridPos[1]) for indPos in pos]
        ltrPos =  [(indPos[0] + gridPos[0], indPos[1] + gridPos[1]) for indPos in ltrPos]
    if letters: return pos, indWdth, indHght, txt, ltrPos
    return pos, indWdth, indHght, txt



def genTrials(setSizes, repsPerSize, operations, blocks, randOps = True, randBlocks = True):
    if type(setSizes) == int: setSizes = [setSizes]
    setSizes = setSizes * repsPerSize
    random.shuffle(setSizes)
    most = max(setSizes)
    trialsList = []

    if randOps: new_ops = random.sample(operations, sum(setSizes))      #returns random keys
    else:
        operations.reverse()        #reverse so they're taken from front when pop()
        new_ops = operations
    for size in setSizes:
        d = defaultdict(list)
        d['trial.len.L'] = size

        new_blocks = random.sample(blocks, size)
        #OPERATIONS PER ROUND OF TRIAL
        for probnum in range(most):
            if probnum >= size:
                #Pad short trials
                d['op.W'].append("")       # processing stim
                d['ans.W'].append("")       # whether answer is True / False
                d['TBR.W'].append("")       # to-be-remembered item
                d['op.sol.W'].append("")
            else:
                #Fill trial entries
                op = new_ops.pop()             #assign last op
                d['op.W'].append(op[0])
                if hasattr(op[1], '__len__'):
                    d['ans.W'].append(op[1][1])           #correct answer
                    d['op.sol.W'].append(op[1][0])        #answer probe
                else:
                    d['ans.W'].append(op[1])
                    d['op.sol.W'].append("")
                d['TBR.W'].append(new_blocks.pop())        #assign last block
        #RESPONSES FOR EACH
        rtcells = ['op.RT.W', 'ans.RT.W', 'ans.Resp.W']
        for dataname in rtcells: d[dataname] = [""]*most
        trialsList.append(d)
    #CREATE TRIALHANDLER OBJECT
    Trials = data.TrialHandler(trialsList, nReps=1, method='sequential')
    emptycells = ['recall.L', 'recallRT.L', 'recall.filtered.L', 'recall.corr.L', 'ops.corr.L']
    for dataname in emptycells: Trials.data.addDataType(dataname)
    return Trials


def waitScreen(win, myMouse, maxViewingTime = 100000, lastTime = 0, onClick = True):
    '''Either waits for a mouse click or until maxViewingTime has elapsed'''
    done = False
    clock = core.Clock()
    myMouse.clickReset()
    while not done:
        click, time = myMouse.getPressed(getTime=True)
        if onClick and click[0] and time[0]:                #click
            done = True
            lastTime = time[0]
        now = clock.getTime()
        if now > maxViewingTime: return now                 #timeout
    return lastTime


def finalResps(resps):
    reverse = resps[:]
    reverse.reverse()
    if "Clear" in reverse:
        if "Submit" in reverse: finalResps = reverse[reverse.index("Submit") + 1:reverse.index("Clear")]
        else: finalResps = reverse[:reverse.index("Clear")]
        finalResps.reverse()
        return finalResps
    else:
        return resps[:]


def calcOpsDur(opsRTs_orig, trimNum = 2):
    '''Use winsorized mean and SD'''
    opsRTs = sorted(opsRTs_orig)
    N = len(opsRTs)
    trimmedRTs = opsRTs[trimNum:-trimNum]        #trim
    trimmedRTs.extend([trimmedRTs[0],trimmedRTs[-1]]*trimNum)     #replace with winsorized val
    meanTrimmed = sum(trimmedRTs) / N
    SSD = sum([(RT - meanTrimmed)**2 for RT in trimmedRTs])
    SDEV = (SSD / N)**(1./2)                                        #winsorized SD (for population)
    print opsRTs
    print trimmedRTs
    return meanTrimmed, meanTrimmed + 2.5*SDEV, SDEV


def dispInstructions(win, myMouse, Stims, lastTime = 0):
    if not hasattr(Stims, "__len__"): Stims = [Stims]
    stimNum = 0
    myMouse.clickReset()
    lastTime = myMouse.getPressed(True)[1][0]
    while stimNum !=  len(Stims):
        stim = Stims[stimNum]
        try: stim.draw()
        except:
            for entry in stim: entry.draw()
        win.flip()
        myMouse.clickReset()
        lastTime = myMouse.getPressed(True)[1][0]
        done = False
        while not done:
            time = myMouse.getPressed(True)[1][0]
            if "left" in event.getKeys() and stimNum > 0:
                stimNum -= 1
                done = True
            if lastTime != time:
                stimNum += 1
                done = True
            event.clearEvents()
    return lastTime


def instruct2stim(win, fname, pos = (0, 150)):
    print fname
    if os.path.splitext(fname)[1] == '.txt':
        return visual.TextStim(win, text=open(fname).read(), color='black', alignHoriz='center')
    else:
        return visual.SimpleImageStim(win, image=fname, pos = pos)

def genInstructions(win, dirname):
    fnames = [f for f in os.listdir(dirname) if not f.startswith('.')]
    screennum = map(lambda x: x.split('.')[0], fnames)
    full_paths = [os.path.join(dirname, fname) for fname in fnames]
    stims = [instruct2stim(win, name) for name in full_paths]
    d = defaultdict(list)
    for key, stim in zip(screennum, stims):
        d[key].append(stim)
    return [d[key] for key in sorted(d)]

class procVer:
    def __init__(self, win, myMouse, TxtStim, VerScreen):
        self.win, self.myMouse, self.TxtStim, self.VerScreen = win, myMouse, TxtStim, VerScreen

    def __call__(self, ans_probe):
        return self.proc(self.win, self.myMouse, ans_probe, self.TxtStim, self.VerScreen)

    def proc(self, win, myMouse, ans_probe, TxtStim, VerScreen):
        TxtStim.setText(ans_probe)
        TxtStim.draw()
        VerScreen.draw()
        win.flip()
        myMouse.clickReset()                                        #TODO: replace with waitscreen
        lastTime = myMouse.getPressed(getTime = True)[1][0]
        ans = None
        while not VerScreen.done:
            click, time = myMouse.getPressed(getTime=True)
            if click[0] and time[0] != lastTime:
                x,y = myMouse.getPos()
                ans = VerScreen.selButtons(x,y)
                lastTime = time[0]
        VerScreen.reset()
        if ans == "True": return True, lastTime
        else: return False, lastTime


def task(win, myMouse, Trials, 
         opsDur, screenBlankInterval, opsPracFeedbackTime, TBRItemTime, feedbackTime,
         dispOp, procVer, dispTBR, procRec,
         opsOnly = False, opsFeedback = False, TBROnly = False):

    #Rec and Ops feedback stims
    TextPrompt = visual.TextStim(win, pos = (0, -50), color = "black")
    OpsFeedback = visual.TextStim(win, pos = (0,-75), color = "black")
    OpsTtlCorr = visual.TextStim(win, pos = (200, 200), color = "black")
    RecFeedback = visual.TextStim(win, color = "black")

    ttlTrials, ttlCorr = 0., 0.
    for trialStims in Trials:
        for cycle in range(len(trialStims['TBR.W'])):
            if cycle < trialStims['trial.len.L']:
                if not TBROnly:
                    #VIEW PROCESSING OPERATION
                    dispOp(trialStims['op.W'][cycle])
                    vt = waitScreen(win, myMouse, opsDur)
                    trialStims['op.RT.W'][cycle] = vt
                    win.flip()
                    waitScreen(win, myMouse, screenBlankInterval, onClick = False)  #Blank Screen
                    #ANSWER
                    ans_probe = trialStims['op.sol.W'][cycle]
                    ans, rt = procVer(ans_probe)
                    trialStims['ans.RT.W'][cycle] = rt
                    trialStims['ans.Resp.W'][cycle] = ans
                    if opsFeedback:
                        if ans == trialStims['ans.W'][cycle]: TextPrompt.setText("Correct")
                        else: TextPrompt.setText("Incorrect")
                        TextPrompt.draw()
                        win.flip()
                        waitScreen(win, myMouse, opsPracFeedbackTime, onClick = False)
                    win.flip()
                    waitScreen(win, myMouse, screenBlankInterval, onClick = False)  #Blank Screen
                if not opsOnly:
                    #TBR-ITEM PRESENTATION (FOR LATER RECALL)
                    dispTBR(trialStims['TBR.W'][cycle])
                    vt = waitScreen(win, myMouse, TBRItemTime, onClick = False)
                    win.flip()
                    waitScreen(win, myMouse, screenBlankInterval, onClick = False)
        if opsOnly: continue
        #RECALL
        resps, respsRT = procRec()
        win.flip()
        finalAns = finalResps(resps)
        Trials.data.add('recall.L', resps)
        Trials.data.add('recall.filtered.L', finalAns)
        Trials.data.add('recallRT.L', respsRT)
        #scored responses
        ans_seen = zip(finalAns, trialStims['TBR.W'])
        recCorr = sum([ans == seen and ans != "" for ans, seen in ans_seen])  #count correct responses
        Trials.data.add('recall.corr.L', recCorr)
        #FEEDBACK FOR RECALL AND OPS
        #proportion of ops correct
        ans_seen = zip(trialStims['ans.Resp.W'],trialStims['ans.W'])
        opsCorr = sum([ans == seen and ans != "" for ans, seen in ans_seen])
        ttlCorr += opsCorr
        ttlTrials += trialStims['trial.len.L']
        Trials.data.add('ops.corr.L', opsCorr)                        #record ops correct for trial
        #give feedback
        if not TBROnly:
            OpsTtlCorr.setText("%s%%"%(int(100 * ttlCorr / ttlTrials)))
            OpsFeedback.setText("You made %s symmetry error(s)"%(trialStims['trial.len.L'] - opsCorr))
            OpsTtlCorr.draw()
            OpsFeedback.draw()
        RecFeedback.setText("%s of %s locations recalled correctly"%(recCorr, trialStims['trial.len.L']))
        RecFeedback.draw()
        win.flip()
        waitScreen(win, myMouse, feedbackTime, onClick = False)