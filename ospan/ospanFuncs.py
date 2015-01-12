from psychopy import visual, core
from sharedFuncs import waitScreen, finalResps


def extendMe(letters):
    letters = [row[:] for row in letters]
    for n in range(1,len(letters)):
        letters[0].extend(letters[n])
    return letters[0]


def num2ltr(num, letters):
    return letters[num / len(letters[0])][num % len(letters[0])]

class procRec:
    def __init__(self, win, myMouse, RecScreen, Prompt, LetterStims, letters):
        self.win, self.myMouse = win, myMouse
        self.RecScreen, self.Prompt, self.LetterStims = RecScreen, Prompt, LetterStims
        self.letters = letters

    def __call__(self):
        return self.procRec(**self.__dict__)

    def procRec(self, win, myMouse, RecScreen, Prompt, LetterStims, letters, lastTime = 0):
        LettersChosen = visual.TextStim(win, text = "", pos = (0,RecScreen.stimList[-1].Rect.pos[1] - 100), height = RecScreen.txtKwargs[0]["height"], color = "black")
        RecScreen.setAutoDraw(drawText=False)
        for stim in RecScreen.stimList[-3:]: stim.Text.setAutoDraw(True)
        for stim in LetterStims: stim.setAutoDraw(True)
        Prompt.setAutoDraw(True)
        LettersChosen.setAutoDraw(True)
        win.flip()
        myMouse.clickReset()
        resps = []
        while not RecScreen.done:
            click, time = myMouse.getPressed(getTime=True)
            if click[0] and time[0]:
                x,y = myMouse.getPos()
                sel = RecScreen.selButtons(x,y)
                if sel:
                    stim, stimLab = sel
                    if stim.Text.text in ("Submit", "Clear", "Blank"):
                        origRCol, origTCol = stim.Rect.fillColor, stim.Text.color
                        stim.Rect.setFillColor("black")
                        stim.Text.setColor("white")
                        win.flip()
                        core.wait(.1)
                        stim.Rect.setFillColor(origRCol)
                        stim.Text.setColor(origTCol)
                        resps.append(stimLab)
                    else:
                        stim.Rect.setFillColor("white")
                        resps.append(num2ltr(stimLab, letters))
                    crnt = " ".join([str(ii) for ii in finalResps(resps)])
                    crnt = crnt.replace("Blank", "_").replace("Submit", "")
                    LettersChosen.setText(crnt)
                myMouse.clickReset()
                lastTime = time[0]
                RecScreen.draw(drawRect = True, drawText = None)
                win.flip()
        RecScreen.reset()
        for stim in LetterStims: stim.setAutoDraw(False)
        Prompt.setAutoDraw(False)
        LettersChosen.setAutoDraw(False)
        return resps, lastTime

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


class dispOp:
    def __init__(self, win, OpStim):
        self.win = win
        self.OpStim = OpStim

    def __call__(self, opVal):
        self.proc(self.win, opVal, self.OpStim)

    def proc(self, win, opVal, OpStim):
        OpStim.setText(opVal)
        OpStim.draw()
        win.flip()

class dispTBR:
    def __init__(self, win, TxtStim, letters, color):
        self.win, self.TxtStim, self.letters, self.color = win, TxtStim, letters, color

    def __call__(self, toDisp):
        self.proc(self.win, toDisp, self.TxtStim, self.letters, self.color)

    def proc(self, win, toDisp, TxtStim, letters, color):
        if type(toDisp) == int: toDisp = num2ltr(toDisp, letters)
        TxtStim.setText(toDisp)
        TxtStim.setColor(color)
        TxtStim.draw()
        win.flip()


def dispInstructions(win, myMouse, Stims, lastTime = 0):
    if not hasattr(Stims, "__len__"): Stims = [Stims]
    for stim in Stims:
        try: stim.draw()
        except:
            for entry in stim: entry.draw()
        win.flip()
        dur, lastTime = waitScreen(win, myMouse, lastTime = lastTime)
    return lastTime
