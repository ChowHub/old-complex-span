from PIL import Image
import os
import pickle

def findCorner(img, pixVal):
    '''find top-left coords, then bottom-right coords.  
    Returns as a 4 item list: [x1, y1, x2, y2] (in PIL fashion)'''
    newImg = img.load()
    coords = []
    done = False
    x,y = 0, 0
    for ii in range(img.size[1]):
        if done: break
        for jj in range(img.size[0]):
            if done: break
            if newImg[x,y] == pixVal:
                coords.extend((x,y))
                done = True
            x += 1
        y += 1
        x = 0
    x, y = img.size
    done = False
    for ii in range(img.size[1]):
        y -= 1
        if done: break
        for jj in range(img.size[0]):
            x -= 1
            if done: break
            if newImg[x,y] == pixVal:
                coords.extend((x,y))
                done = True
        x = img.size[0]
    return coords

    
def bmp2grid(img, box, rows, cols, retFlat = True):
    '''Finds the color of the middle-most pixel for each bin in a rows x cols grid,
    and returns either a list[row][col] or a flat list with [entry11, entry12, etc..]
    '''
    x1, x2 = box[0], box[2]
    y1, y2 = box[1], box[3]
    binWdth = abs(x1 - x2) / cols       #int / int (just keep that in mind)
    binHght= abs(y1 - y2) / rows       #distance per bin
    pixMat = []
    pixFlat = []
    crntRowPix = []
    for row in range(rows):
        for col in range(cols):
            #PIL starts in top-left (whereas pyglet used in Psychopy starts bottom-left)
            crntRowPix.append(img.getpixel((x1 + binWdth/2 + binWdth*col,
                                            y1 + binHght/2 + binHght*row)))
        pixMat.append(crntRowPix)
        pixFlat.extend(crntRowPix)
        crntRowPix = []
    sym = True
    for row in pixMat:
        for col in range(cols/2):
            if row[col] != row[-(col+1)]: sym = False   #Symmetry judgement
    
    if not retFlat: return pixMat, sym
    return pixFlat, sym


fname_storage = "stims.pickle"
f1 = open(fname_storage, "wb")
box = (122, 80, 275, 215)
os.chdir("spatial stims")
stimDict = {}

keys_corr = []
for fname in os.listdir(os.getcwd()):
    try: 
        img = Image.open(fname)
        box = findCorner(img, 0)
        img = img.convert("RGB")
        img.convert("RGB")
        stimFill, isSym = bmp2grid(img, box, 8, 8)
        for ii in range(len(stimFill)):                   #convert from 0:255 to psychopy's -255:255 range
            stimFill[ii] = [-255 + entry*2 for entry in stimFill[ii]]
        if "prac" not in fname: 
            keys_corr.append( (fname[:-4], isSym) )            #keyname, correct or not    (for randomly generating trials)
            stimDict[fname[:-4]] = stimFill
    except:
        print fname, " didn't convert to stim (OK if it is a hidden or non-stim file..)"


pickle.dump((stimDict, keys_corr), f1)
f1.close()
    
