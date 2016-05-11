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
injuryGoalsGr,injuryGoalsKO = [0,0,0,0], [0,0,0,0]

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
                                #NB reduce injury time goals to end of normal time
                                goalTimesGr.append(int(time[0])) #+int(time[1]))
                                if goalTimesGr[-1] == 45:
                                    injuryGoalsGr[0] += 1
                                elif goalTimesGr[-1] == 90:
                                    injuryGoalsGr[1] += 1
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
                            #NB reduce injury time goals to end of normal time
                            goalTimesKO.append(int(time[0]))#+int(time[1]))
                            if goalTimesKO[-1] == 45:
                                injuryGoalsKO[0] += 1
                            elif goalTimesKO[-1] == 90:
                                injuryGoalsKO[1] += 1
                            elif goalTimesKO[-1] == 105:
                                injuryGoalsKO[2] += 1
                            elif goalTimesKO[-1] == 120:
                                injuryGoalsKO[3] += 1
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
print '%.2f%% games are 0-0' % ((np.mean([totalGoals[i] == 0 for i in range(len(totalGoals))]))*100)

with open('euroGoals.csv','w') as csvfile:
    mywriter = csv.writer(csvfile)
    mywriter.writerow(['date','stage','goals'])
    for i in range(len(allDates)):
        mywriter.writerow([allDates[i],labels[i],totalGoals[i]])

goalTimes = goalTimesGr + goalTimesKO
print len(goalTimes)

print np.sum([goalTimesGr[i] <= 45 for i in range(len(goalTimesGr))])*100./len(goalTimesGr),"% first half groups"
print np.sum([45 < goalTimesGr[i] <= 90 for i in range(len(goalTimesGr))])*100./len(goalTimesGr),"% second half groups"
KOgoals90mins = np.sum([goalTimesKO[i] <= 90 for i in range(len(goalTimesKO))])
print np.sum([goalTimesKO[i] <= 45 for i in range(len(goalTimesKO))])*100./KOgoals90mins,"% first half KO"
print np.sum([45 < goalTimesKO[i] <= 90 for i in range(len(goalTimesKO))])*100./KOgoals90mins,"% second half KO"

#Extra time: 96 final stopped at 95, 2000 semi 1 at 117, final at 103, 
#  2004 semi 2 at 105+1 

nbinsGr,bins,patches = plt.hist(goalTimesGr,bins=np.arange(0.1,120.2,15),label='Group',weights=np.zeros_like(goalTimesGr)+1./len(goalTimesGr))
nbinsKO,bins,patches = plt.hist(goalTimesKO,bins=np.arange(0.1,120.2,15),label='Knockout',rwidth=0.6,weights=np.zeros_like(goalTimesKO)+1./len(goalTimesKO))
plt.xlabel('Time / minutes'); plt.ylabel('Fraction')
plt.xticks(range(0,121,15))
plt.legend(loc='upper left')
plt.title('Euro 1996-2012 goal time distribution')
plt.show()


#nbinsGr *= len(goalTimesGr)
#nbinsKO *= len(goalTimesKO)
injuryGoalsGr = np.asarray(injuryGoalsGr) / float(len(goalTimesGr))
injuryGoalsKO = np.asarray(injuryGoalsKO) / float(len(goalTimesKO))
print nbinsGr,injuryGoalsGr
print nbinsKO,injuryGoalsKO

with open('data/goaltimes.csv','w') as csvfile:
    mywriter = csv.writer(csvfile)
    mywriter.writerow(['phase','binTimes','goals','goalCategory'])
    for i in range(len(bins)-1):
        if i in [0,1,3,4,7]:
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsGr[i]),'reg'])
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),0,'inj'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsKO[i]),'reg'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),0,'inj'])
        elif i == 2:
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsGr[i])-injuryGoalsGr[0],'reg'])
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsGr[0],'inj'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsKO[i])-injuryGoalsKO[0],'reg'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsKO[0],'inj'])
        elif i == 5:
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsGr[i])-injuryGoalsGr[1],'reg'])
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsGr[1],'inj'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsKO[i])-injuryGoalsKO[1],'reg'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsKO[1],'inj'])
        elif i == 6:
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsGr[i])-injuryGoalsGr[2],'reg'])
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsGr[2],'inj'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsKO[i])-injuryGoalsKO[2],'reg'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsKO[2],'inj'])
        elif i == 7:
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsGr[i])-injuryGoalsGr[3],'reg'])
            mywriter.writerow(['Groups',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsGr[3],'inj'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*float(nbinsKO[i])-injuryGoalsKO[3],'reg'])
            mywriter.writerow(['Knockouts',str(15*i+1)+'-'+str(15*(i+1)),100*injuryGoalsKO[3],'inj'])