import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate 
import matplotlib.cm as cm
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
            thisrun = [[] for i in range(7)]
            continue
        if inrun:
            linel = line.split('\t')
            #if necessary, determine our step, start, and end
            if st == 0:
                st = int(linel[0])
                lrun = int(linel[0])
            elif stp == 0 and lrun != 0:
                stp = int(linel[0])-lrun
            for i in range(7):
                thisrun[i].append( float(linel[i].rstrip('\n')) ) 
            lrun = int(linel[0])
    probs.append(copy.deepcopy(thissim))
    thissim = []

#Now that we have our step, start, and end initialize our index
#index = [i for i in range(st,en,stp)]
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
indicies = []
for pri in range(len(probs)):
    da = {}
    db = {}
    indicies.append(probs[pri][0][0])
    for i in range(len(probs[pri])):
        runname = ''.join(['run', str(i+1)])
        for j in range(2,7,2):
            da[''.join([runname, '.', str(j)])] = pd.Series(probs[pri][i][j], index=probs[pri][i][0])
        for j in range(1,7,2):
            db[''.join([runname, '.', str(j)])] = pd.Series(probs[pri][i][j], index=probs[pri][i][0])
        
    bestdata.append(pd.DataFrame(da))
    avgdata.append(pd.DataFrame(db))  
    print(pd.DataFrame(db))
#autogenerate our run count
if y_axis_label == "":
    y_axis_label = ''.join(['Average Subfitness Over ', str(len(probs[0])), ' Runs'])

#grab our individual means and prepare to plot them
for i in range(len(bestdata)):
    bestdata[i]['mean'] = bestdata[i].mean(1)
    bestdata[i]['index'] = pd.Series(indicies[i], index=indicies[i])
for i in range(len(avgdata)):
    avgdata[i]['mean'] = avgdata[i].mean(1)
    avgdata[i]['index'] = pd.Series(indicies[i], index=indicies[i])
    
mdataframed = {}
for i in range(len(bestdata)):
    # print("\n", bestdata[i]['index'], "\n", bestdata[i]['mean'])
    s = interpolate.UnivariateSpline(bestdata[i]['index'], bestdata[i]['mean'], s=smfctr)
    mdataframed[''.join([dn[i], ' Avg Best'])] = s(iindex)
                        
#for i in range(len(avgdata)):
    #s = interpolate.UnivariateSpline(avgdata[i]['index'], avgdata[i]['mean'], s=smfctr)
    #mdataframed[''.join([dn[i], ' Average'])] = s(iindex)
                        
#mdataframed['Fitness Evaluations'] = iindex
mdataframe = pd.DataFrame(mdataframed, index=iindex)

colors = iter(cm.rainbow(np.linspace(0, 1, len(mdataframed))))
print( colors )
for subplot in mdataframe:
    plt.plot(iindex, mdataframe[subplot], color=next(colors), label=subplot)
plt.autoscale(axis='x', tight=True)
#fig.set_xticks(np.arange(st,en-stp,x_axis_ticks))
#fig.set_yticks(np.arange(0,1.,0.1))


plt.xlabel(y_axis_label)
plt.xlabel(x_axis_label)
plt.title(graph_label)
plt.legend(loc=3, borderaxespad=0.)
plt.grid( )
plt.show(1)
#plt.savefig('out.png')