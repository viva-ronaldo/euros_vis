import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr,linregress
import re,sys

years = [1996,2000,2004,2008,2012]
#years = [2000]

allDates = []
totalGoals = []
for year in years:

    #group stages require separate pages
    for g in ['A','B','C','D']:
        hits = 0
        with open('data/UEFA_Euro_%i_Group_%s' % (year,g)) as myfile:
            for row in myfile:
                if re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row) != None:
                    date = re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row).groups()[0]
                    print date
                    date = date.split(' ')
                    allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+date[0]))
                elif re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row) != None:
                    date = re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row).groups()[0]
                    print date.replace('&#160;',' ')
                    date = date.split('&#160;')
                    allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+date[0]))

                if re.search('width:22%;.*>',row) != None:
                    scores = re.search('width:22%;.*center">([0-9])[^0-9]*([0-9])',row).groups()
                    totalGoals.append(int(scores[0])+int(scores[1]))
                    print totalGoals[-1]
                    hits += 1
                if hits == 6:
                    break


    foundKnockouts = 0
    hits = 0
    with open('data/UEFA_Euro_%i' % year) as myfile:
        for row in myfile:
            if 'id="Quarter-finals"' in row:
                foundKnockouts = 1
            if foundKnockouts and re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row) != None:
                date = re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row).groups()[0]
                print date
                date = date.split(' ')
                allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+date[0]))
            elif foundKnockouts and re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row) != None:
                date = re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row).groups()[0]
                print date.replace('&#160;',' ')
                date = date.split('&#160;')
                allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+date[0]))

            if foundKnockouts and re.search('title="UEFA Euro %i knockout [a-z]*">[0-9]' % year,row) != None:
                #print row
                scores = re.search('title="UEFA Euro %i knockout [a-z]*">([0-9])[^0-9]*([0-9])' % year,row).groups()
                totalGoals.append(int(scores[0])+int(scores[1]))
                print totalGoals[-1]
                hits += 1
            elif year == 2000 and foundKnockouts and re.search('width:22%;.*>',row) != None:
                scores = re.search('width:22%;.*center">([0-9])[^0-9]*([0-9])',row).groups()
                totalGoals.append(int(scores[0])+int(scores[1]))
                print totalGoals[-1]
                hits += 1                
            elif foundKnockouts and re.search('title="UEFA Euro %i Final">[0-9]' % year,row) != None:
                if year == 2004:
                    totalGoals.append(1)  #easiest to do manually
                elif year == 1996:
                    totalGoals.append(3)  #NB aet
                else:
                    #print row
                    scores = re.search('title="UEFA Euro %i Final">([0-9])[^0-9]*([0-9])' % year,row).groups()
                    totalGoals.append(int(scores[0])+int(scores[1]))
                print totalGoals[-1]
                hits += 1                
                break
            elif foundKnockouts and hits == 7:
                break
    print 'Total games so far %i' % len(allDates)

#print allDates
#print totalGoals
print len(allDates),len(totalGoals)
print np.mean(totalGoals)

plt.plot(totalGoals,'x')
plt.show()