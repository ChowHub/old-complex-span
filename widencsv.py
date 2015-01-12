import csv

def widen(trialsList, colnames, sep, fromcsv=True):
    """Expands each column containing lists into seperate columns.

    E.g. if the column "resp" has a list of 3 responses per row, it is expanded to..
    resp1 resp2 resp3

    """
    for trial in trialsList:
        for col in colnames:
            if fromcsv: trial[col] = eval(trial[col])
            for ii, item in enumerate(trial[col]):
                trial["%s%s%i"%(col,sep,ii)] = item

#Read
d = csv.DictReader(open('testout.tsv'), dialect=csv.get_dialect('excel-tab'))
trials = [row for row in d]
cols2expand = [name for name in d.fieldnames if name.endswith('.W')]

#Expand
widen(trials, cols2expand, sep='.', fromcsv=True)

#Get all fieldvalues
s = set()
for row in trials: s.update(row.keys())

#Write
out = csv.DictWriter(open('testout2.csv', 'w'), s)
out.writeheader()
out.writerows(trials)
