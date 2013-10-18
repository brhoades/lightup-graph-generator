from ggplot import *
import numpy as np
from scipy import interpolate 
import pandas as pd
import re
import copy

fn2 = "validityenforced-2-res.log"
fn1 = "randomplace-2-res.log"
dn = []
dn.append( "Validity Enforced")
dn.append( "Random" )
smfctr = 0.0003 #>0.0001 < 0.001 works best
x_axis_label = "Fitness Evaluations"
x_axis_ticks = 0 # 0 == auto
y_axis_label = "Average Fitness Over 5 Runs"
graph_label = "Provided Problem Initialization"

#to be automatically determined later
st = 0
en = 0 
stp = 0

log = []
log.append( open( ''.join(["logs/", fn1]), 'r' ) )
log.append( open( ''.join(["logs/", fn2]), 'r' ) )

probs = []

lrun = 0
run = re.compile(r'Run [0-9]+')
end = re.compile(r'Run best')
thisrun = []
thissim = []
inrun = False
for i in range(0,2):
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
            thisrun = [[], []]
            continue
        if inrun:
            linel = line.split('\t')
            #if necessary, determine our step, start, and end
            if st == 0:
                st = int(linel[0])
                lrun = int(linel[0])
            elif stp == 0 and lrun != 0:
                stp = int(linel[0])-lrun
            thisrun[0].append( float(linel[1]) )    
            thisrun[1].append( float( linel[2].rstrip('\n')) )
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
        da[runname] = pd.Series(probs[pri][i][1], index=index)
        db[runname] = pd.Series(probs[pri][i][0], index=index)
        
    bestdata.append(pd.DataFrame(da))
    avgdata.append(pd.DataFrame(db))  
   
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
plt.show(1)