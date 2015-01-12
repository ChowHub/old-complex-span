import random
import pickle

def genMathOps(multDig1, multDig2, divDig1, divDig2, add, sub):
    multDivList = ["%s * %s"%(ii,jj) for ii in multDig1 for jj in multDig2 if ii != jj]       #diff multipliers
    multDivList.extend(["%s / %s"%(ii,jj) for ii in divDig1 for jj in divDig2 if (ii%jj == 0)]) #must divide evenly
    arith = [" + %s"%ii for ii in add]
    arith.extend([" - %s"%ii for ii in sub])
    Ops = [(muldiv + adsub) for muldiv in multDivList for adsub in arith       #keep those that >= 0
                    if eval(muldiv + adsub) >= 0]
    opsList = []
    for op in Ops:
        #Solutions
        corr = random.randint(0,1)
        adjust = random.randint(1, 5)*(-1**random.randint(0,1))     #to add or subtract to ans
        ans = eval(op) +  (not corr) * adjust                   #if correct don't adjust
        while ans < 0:
            adjust = random.randint(1, 5)                           #re-adjust (there will likely be more additions than subtractions as a result)
            ans = eval(op) + adjust
        opsList.append([op, (ans, bool(corr))])                          


    
    return opsList

ranges = [range(1,10)]*6
stimDict = genMathOps(*ranges) #1 through 9 for each


fname_storage = "ostims.pickle"
f1 = open(fname_storage, "w")
pickle.dump(stimDict, f1)
f1.close()
