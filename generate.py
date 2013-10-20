from ggplot import *
import numpy as np
from scipy import interpolate 
import pandas as pd
import re
import copy
import sys

fn = []
#fn2 = "MOEA-probdist-0.861.txt"
#fn1 = "MOEA-tournament-0.861.txt"
dn = []
#dn.append( "Tournament Selection")
#dn.append( "Roulette Wheel Selection" )
smfctr = 0.0003 #>0.0001 < 0.001 works best
x_axis_label = "Fitness Evaluations"
x_axis_ticks = 0 # 0 == auto
y_axis_label = "" #if blank, set to "Average Subfitness Over # Runs"
graph_label = "Easy Graph NSGA-II"

args = sys.argv[1:]
argument = re.compile('\-[A-Za-z]')
for i in range(0, len(args), 2):
    if argument.match(args[i]):
        if args[i] == "-t":
            graph_label = args[i+1]
        continue
    
    fn.append(args[i])
    dn.append(args[i+1])

#to be automatically determined later
st = 0
en = 0 
stp = 0

log = []
for file in fn:
    log.append( open(file, 'r' ) )

probs = []

lrun = 0
run = re.compile(r'Run [0-9]+')
end = re.compile(r'\=SPACER\=')
thisrun = []
thissim = []
inrun = False
for i in range(0,len(log)):
    for line in log[i]:
        if end.match(line):
            inrun = False
            thissim.append(thisrun)
            #first time through we determine step, start, and end automatically
            if en == 0:
                en = lrun+stp #+stp due to graphing
            continue
        if run.match(line):
            inrun = True
            thisrun = [[] for i in range(6)]
            continue
        if inrun:
            linel = line.split('\t')
            #if necessary, determine our step, start, and end
            if st == 0:
                st = int(linel[0])
                lrun = int(linel[0])
            elif stp == 0 and lrun != 0:
                stp = int(linel[0])-lrun
            for i in range(6):
                thisrun[i].append( float(linel[i+1]) )    
            lrun = int(linel[0])
    probs.append(copy.deepcopy(thissim))
    thissim = []

#Now that we have our step, start, and end initialize our index
index = [i for i in range(st,en,stp)]
#and our interpolation index
iindex = [i for i in range(st,en)]

if x_axis_ticks == 0:
    x_axis_ticks = int(en-stp/10)

bestdata = []
avgdata = [] 
   
# probs
# pri: [log1] [log2]
# problem (log1): [run1][run2][run3]...
# run (run1): [0][1]
# 0 => average list [.3,.5] 1 => bestlist [0.2, 1]
for pri in range(len(probs)):
    da = {}
    db = {}
    for i in range(len(probs[pri])):
        runname = ''.join(['run', str(i+1)])
        for j in range(1,6,2):
            da[''.join([runname, '.', str(j)])] = pd.Series(probs[pri][i][1], index=index)
        for j in range(0,6,2):
            db[''.join([runname, '.', str(j)])] = pd.Series(probs[pri][i][0], index=index)
        
    bestdata.append(pd.DataFrame(da))
    avgdata.append(pd.DataFrame(db))  

#autogenerate our run count
if y_axis_label == "":
    y_axis_label = ''.join(['Average Subfitness Over ', str(len(probs[0])), ' Runs'])

#grab our individual means and prepare to plot them
for i in range(len(bestdata)):
    bestdata[i]['mean'] = bestdata[i].mean(1)
for i in range(len(avgdata)):
    avgdata[i]['mean'] = avgdata[i].mean(1)


mdataframed = {}
for i in range(len(bestdata)):
    s = interpolate.UnivariateSpline(index, bestdata[i]['mean'], s=smfctr)
    mdataframed[''.join([dn[i], ' Avg Best'])] = s(iindex)
                        
for i in range(len(avgdata)):
    s = interpolate.UnivariateSpline(index, avgdata[i]['mean'], s=smfctr)
    mdataframed[''.join([dn[i], ' Average'])] = s(iindex)
                        
mdataframed['Fitness Evaluations'] = iindex
mdataframe = pd.DataFrame(mdataframed)


fig = mdataframe.plot(x='Fitness Evaluations')
plt.autoscale(axis='x', tight=True)
fig.set_xticks(np.arange(st,en-stp,x_axis_ticks))
fig.set_yticks(np.arange(0,1.,0.1))


fig.set_ylabel(y_axis_label)
fig.set_xlabel(x_axis_label)
plt.title(graph_label)

plt.grid( )
# plt.show(1)
plt.savefig('out.png')