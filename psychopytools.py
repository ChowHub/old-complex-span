from psychopy import visual


def genMathOps(multDig1, multDig2, divDig1, divDig2, add, sub):
    """Return tuple with all strings of them form A */ B +- C, with constraints:
        A != B
        If division, A / B is whole number
        Answer is >= 0

    """
    multDivList = ["%s*%s"%(ii,jj) for ii in multDig1 for jj in multDig2 if ii != jj]           #multiplication
    multDivList.extend(["%s/%s"%(ii,jj) for ii in divDig1 for jj in divDig2 if (ii%jj == 0)])   #division
    arith = [" + %s"%ii for ii in add]                                                          #addition
    arith.extend([" - %s"%ii for ii in sub])                                                    #subtraction
    finalOps = [(muldiv + adsub) for muldiv in multDivList for adsub in arith
                    if eval(muldiv + adsub) >= 0]
    return finalOps


class WordBox:
    '''Convenience class, combining visual.ShapeStim and visual.TextStim'''
    def __init__(self, win, wdth, hght, TextStim = None, moveText=True, cntrRec = False, **kwargs):
        self.Rect = visual.ShapeStim(win,
                                     vertices = [( 0      , -hght),
                                                 ( wdth   , -hght),
                                                 ( wdth   , 0,),
                                                 ( 0      , 0)],
                                     **kwargs
                                     )
        if cntrRec: self.Rect.setPos((self.Rect.pos[0] - wdth/2., self.Rect.pos[1] + hght/2.))
        if TextStim:
            if moveText: TextStim.setPos((self.Rect.pos[0] + wdth/2., self.Rect.pos[1] - hght/2.))
        self.Text = TextStim
        self.wdth = wdth
        self.hght = hght
        self.win = win
        self.pos = self.Rect.pos
    def setAutoDraw(self, drawRect = True, drawText = True):
        if drawRect != None: self.Rect.setAutoDraw(drawRect)
        if self.Text!= None: self.Text.setAutoDraw(drawText)
    def setPos(self, pos):
        self.Rect.pos = pos
        if self.Text: self.Text.pos = (pos[0] + self.wdth, pos[1] + self.hght)
    def draw(self, drawRect = True, drawText = True):
        if drawRect: self.Rect.draw()
        if drawText: self.Text.draw()


class Buttons:
    """Generic class for selecting and interacting with rectangular objects.

    Draws N boxes with pos as top-left position, using WordBox class. Can check for mouse click within box, and respond with the
    function method().  All objects are stored as a list.


    """
    def __init__(self, win, pos, wdth, hght, txt, kwargsList = None, txtKwargs = None, **kwargs):
        try:                                    #Ensure pos,wdth,hght,txt are iterable
            pos[0][0]
            self.pos = pos
        except: self.pos = [pos]
        self.wdth, self.hght, self.txt = [],[],[]
        try:
            self.wdth.extend(wdth)
        except TypeError: self.wdth = [wdth]
        try:
            self.hght.extend(hght)
        except TypeError: self.hght = [hght]
        if type(txt) == str: self.txt = [txt]
        else: self.txt = [entry for entry in txt]
        if kwargsList: self.kwargs = kwargsList                 #kwargs are specefied for each button, or
        else: self.kwargs = [kwargs.copy() for entry in self.pos]#shallow copy kwargs dict for each button
        if not txtKwargs: self.txtKwargs = [{} for entry in self.pos]
        elif type(txtKwargs) == list or type(txtKwargs) == tuple: self.txtKwargs = txtKwargs
        else: self.txtKwargs = [txtKwargs.copy() for entry in self.pos]
        self.win = win
        self.done = False
        self.stimList = []
        self.respNum = 1
        self.genStims()

    def genStims(self):
        self.stimList = []
        for pos, wdth, hght, txt, txtKwargs, kwargs in zip(self.pos, self.wdth, self.hght, self.txt, self.txtKwargs, self.kwargs):
            oneTxt = visual.TextStim(self.win, txt, **txtKwargs)
            oneStim = WordBox(self.win, wdth, hght, TextStim = oneTxt, pos = pos, **kwargs)
            self.stimList.append(oneStim)

    def reset(self):
        self.done = False
        self.respNum = 1
        self.setAutoDraw(False, False)
        self.genStims()

    def method(self, stim, stimNum):
        '''Default method for responding to button presses.  Can / should be overloaded.'''
        self.done = True
        return stim.Text.text

    def selButtons(self, x,y):
        #for pos, wdth, hght, stimNum in zip(self.pos, self.wdth, self.hght, range(len(self.pos))):
        for stim, stimNum in zip(self.stimList, range(len(self.stimList))):
            if (x > stim.pos[0] and x < (stim.pos[0] + stim.wdth) and y < stim.pos[1] and y > (stim.pos[1]-stim.hght)):
                return self.method(stim, stimNum)

    def draw(self, drawRect = True, drawText = True):
        for button in self.stimList:
            button.draw(drawRect, drawText)

    def setAutoDraw(self, drawRect = True, drawText = True):
        for button in self.stimList:
            button.setAutoDraw(drawRect, drawText)

    def erase(self):
        for button in self.stimList:
            button.setAutoDraw(False)

    def setFillColor(self, stimList = None, color = "black"):
        '''Sets fill color for a list or single stimulus from stimList.
        Sets all black by default.
        '''
        if not stimList:
            stimList = self.stimList
        if hasattr(stimList, "__len__"):
            for stim in range(len(stimList)):
                if type(color) == str: stimList[stim].Rect.setFillColor(color)
                else: stimList[stim].Rect.setFillColor(color[stim], 'rgb')
        else: stimList.Rect.setFillColor(color)
