from psychopy import core

class procRec:
    def __init__(self, win, myMouse, RecScreen, Prompt):
        self.win, self.myMouse, self.RecScreen, self.Prompt = win, myMouse, RecScreen, Prompt
    def __call__(self):
        return self.proc(**self.__dict__)
        
    def proc(self, win, myMouse, RecScreen, Prompt, lastTime = 0):
        """TODO: bug fix--hold down mouse click over the blank button"""
        RecScreen.setAutoDraw(drawText=False)
        for stim in RecScreen.stimList[-3:]:
            stim.Text.setAutoDraw(True)
        Prompt.setAutoDraw(True)
        win.flip()
        myMouse.clickReset()
        resps = []
        respsRT = []
        while not RecScreen.done:
            click, time = myMouse.getPressed(getTime=True)
            if click[0] and time[0]:
                x,y = myMouse.getPos()
                sel = RecScreen.selButtons(x,y)
                if sel:
                    stim, stimLab = sel
                    resps.append(stimLab)
                    if stim.Text.text in ("Submit", "Clear", "Blank"):
                        origRCol, origTCol = stim.Rect.fillColor, stim.Text.color
                        stim.Rect.setFillColor("black")
                        stim.Text.setColor("white")
                        win.flip()
                        core.wait(.05)
                        stim.Rect.setFillColor(origRCol)
                        stim.Text.setColor(origTCol)
                respsRT.append(time[0])
                RecScreen.draw(drawRect = True, drawText = None)
                win.flip()
                myMouse.clickReset()
        for stim in RecScreen.stimList[-3:]:
            stim.Text.setAutoDraw(False)
        Prompt.setAutoDraw(False)
        RecScreen.reset()
        return resps, respsRT
from random import randint
class dispOp:
    def __init__(self, win, Grid, stimDict): 
        self.win, self.Grid, self.stimDict = win, Grid, stimDict
    def __call__(self, color_key):
        print self.__dict__
        self.proc(color_key = color_key,  **self.__dict__)

    def proc(self, win, color_key, Grid, stimDict):
        Grid.setFillColor(color = stimDict[color_key])
        Grid.draw(drawText = False)
        win.flip()

class dispTBR:
    def __init__(self, win, Grid, color):
        self.win, self.Grid, self.color = win, Grid, color
    def __call__(self, toFill):
        self.proc(self.win, toFill, self.Grid, self.color)

    def proc(self, win, toFill, Grid, color):
        Grid.setFillColor(Grid.stimList[toFill], color)
        for entry in Grid.stimList[:-3]:
            entry.draw(drawRect = True, drawText = False)
        win.flip()
        Grid.reset()

