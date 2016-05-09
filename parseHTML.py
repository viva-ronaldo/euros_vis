import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr,linregress
import re,sys

years = [1996,2000,2004,2008,2012]
#years = [2012]

allDates = []
totalGoals = []
goalTimesGr, goalTimesKO = [], []

for year in years:

    #group stages require separate pages
    for g in ['A','B','C','D']:
        hits, extraLines = 0, 0
        with open('data/UEFA_Euro_%i_Group_%s' % (year,g)) as myfile:
            for row in myfile:
                if re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row) != None:
                    date = re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row).groups()[0]
                    #print date
                    date = date.split(' ')
                    allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+str('%02i' % int(date[0]))))
                elif re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row) != None:
                    date = re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row).groups()[0]
                    #print date.replace('&#160;',' ')
                    date = date.split('&#160;')
                    allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+str('%02i' % int(date[0]))))

                if re.search('width:22%;.*>',row) != None:
                    scores = re.search('width:22%;.*center">([0-9])[^0-9]*([0-9])',row).groups()
                    totalGoals.append(int(scores[0])+int(scores[1]))
                    #print totalGoals[-1]
                    hits += 1

                #and goal times
                if 'alt="Goal"' in row:
                    if re.search('>([0-9]{1,3}|[0-9]{2,3}\+[0-9])\'',row) != None:
                        times = re.findall('>([0-9]{1,3}|[0-9]{2,3}\+[0-9]|45\+[0-9])\'',row)
                        for time in times:
                            if '+' in time:
                                time = time.split('+')
                                goalTimesGr.append(int(time[0])+int(time[1]))
                            else:
                                goalTimesGr.append(int(time))

                if hits == 6:
                    extraLines += 1
                if hits == 6 and extraLines == 20:
                    break

    #Revert to 90 minute totals: final 96 -1, 00 g5,7 -1, 04 g1 -2, g6 -1, 08 g2 -2, g3 -2
    foundKnockouts, extraLines = 0, 0
    hits = 0
    with open('data/UEFA_Euro_%i' % year) as myfile:
        for row in myfile:
            if 'id="Quarter-finals"' in row:
                foundKnockouts = 1
            if foundKnockouts and re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row) != None:
                date = re.search('>([0-9][0-9]? [A-Za-z]* [0-9]*)<',row).groups()[0]
                #print date
                date = date.split(' ')
                allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+str('%02i' % int(date[0]))))
            elif foundKnockouts and re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row) != None:
                date = re.search('>([0-9][0-9]?&#160;[A-Za-z]*?&#160;[0-9]*)<',row).groups()[0]
                #print date.replace('&#160;',' ')
                date = date.split('&#160;')
                allDates.append(int(date[2]+{'June':'06','July':'07'}[date[1]]+str('%02i' % int(date[0]))))


            if foundKnockouts and re.search('title="UEFA Euro %i knockout [a-z]*">[0-9]' % year,row) != None:
                scores = re.search('title="UEFA Euro %i knockout [a-z]*">([0-9])[^0-9]*([0-9])' % year,row).groups()
                totalGoals.append(int(scores[0])+int(scores[1]))
                if (year == 2004 and (hits+1) == 6):
                    totalGoals[-1] -= 1
                elif (year == 2004 and (hits+1) == 1) or (year == 2008 and (hits+1) == 2) or (year == 2008 and (hits+1) == 3):
                    totalGoals[-1] -= 2
                #print totalGoals[-1]
                hits += 1
            elif year == 2000 and foundKnockouts and re.search('width:22%;.*>',row) != None:
                scores = re.search('width:22%;.*center">([0-9])[^0-9]*([0-9])',row).groups()
                totalGoals.append(int(scores[0])+int(scores[1]))
                if (hits+1) == 5 or (hits+1) == 7:
                    totalGoals[-1] -= 1
                #print totalGoals[-1]
                hits += 1
            elif foundKnockouts and re.search('title="UEFA Euro %i Final">[0-9]' % year,row) != None:
                if year == 2004:
                    totalGoals.append(1)  #easiest to do manually
                elif year == 1996:
                    totalGoals.append(2)  #NB b.e.t.
                else:
                    scores = re.search('title="UEFA Euro %i Final">([0-9])[^0-9]*([0-9])' % year,row).groups()
                    totalGoals.append(int(scores[0])+int(scores[1]))
                    if year == 2000:
                        totalGoals[-1] -= 1
                #print totalGoals[-1]
                hits += 1

            #and goal times
            if 'alt="Goal"' in row or 'alt="Golden goal"' in row:
                if re.search('>([0-9]{1,3}|[0-9]{2,3}\+[0-9])\'',row) != None:
                    times = re.findall('>([0-9]{1,3}|[0-9]{2,3}\+[0-9])\'',row)
                    for time in times:
                        if '+' in time:
                            time = time.split('+')
                            goalTimesKO.append(int(time[0])+int(time[1]))
                        else:
                            goalTimesKO.append(int(time))

            if foundKnockouts and hits == 7:
                extraLines += 1
            if foundKnockouts and hits == 7 and extraLines == 20:
                break
    print 'Total games so far %i' % len(allDates)



labels = []
for i in range(len(allDates)):
    if (i % 31) < 24:
        labels.append('group')
    else:
        labels.append('knockout')

#print allDates
#print totalGoals
print len(allDates),len(totalGoals)
print np.mean(totalGoals)

with open('euroGoals.csv','w') as csvfile:
    mywriter = csv.writer(csvfile)
    mywriter.writerow(['date','stage','goals'])
    for i in range(len(allDates)):
        mywriter.writerow([allDates[i],labels[i],totalGoals[i]])

goalTimes = goalTimesGr + goalTimesKO
print len(goalTimes)

plt.hist(goalTimesGr,bins=range(0,121,15),label='Group',weights=np.zeros_like(goalTimesGr)+1./len(goalTimesGr))
plt.hist(goalTimesKO,bins=range(0,121,15),label='Knockout',rwidth=0.6,weights=np.zeros_like(goalTimesKO)+1./len(goalTimesKO))
plt.xlabel('Time / minutes'); plt.ylabel('Fraction')
plt.xticks(range(0,121,15))
plt.legend()
plt.title('Euro 1996-2012 goal time distribution')
plt.show()
