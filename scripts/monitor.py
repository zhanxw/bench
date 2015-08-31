#!/usr/bin/env python
import sys, os
from time import time, sleep, strftime

def unlist(a):
    """
    a is list, and it may contain another list, this function unlist recusrively.
    a = [1, 2, [3, 4], [5, [6]]]
    unlist(a) == [1, 2, 3, 4, 5, 6]
    """
    ret = []
    for i in a:
        if isinstance(i, list):
            ret.extend(unlist(i))
        elif isinstance(i, tuple):
            ret.extend(unlist(list(i)))
        else:
            ret.append(i)
    return ret

# d is is pandas.DataFrame
def printTable(d, sep = '\t', outFile = sys.stderr):
    print >> outFile, sep.join(d.columns)
    for l in d.iterrows():
        print >> outFile, sep.join([str(i) for i in l[1]])

def calculateMean(timePoint, value):
    #print "tp = ", timePoint
    #print "value = ", value
    if len(value) == 1:
        return value
    value = value[0:-1]
    weight = timePoint[1:] - timePoint[0:-1]
    totalSpan = timePoint[-1] - timePoint[0]
    if any((i < 0 for i in weight)):
        print >> sys.stderr, "Timepoint is not monotonelly increasing!"
        return 0.
    if totalSpan == 0.0:
        return value[0]
    avg = np.sum(weight * value) / totalSpan
    return avg
        
def draw(dRaw, dg, outFile):
    import matplotlib
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize = (18, 18))
    dg['prog'] = dg.apply(lambda x: x['cmd'].split()[0] + '(%d)' % x['pid'] ,axis = 1)
    dg.index = dg['prog']
    ax = fig.add_subplot(3, 3, 1)
    dg[['utime']].plot(kind = 'barh', title = "User Time (s)", ax = ax)
    ax = fig.add_subplot(3, 3, 2)    
    dg[['stime']].plot(kind = 'barh', title = "System Time (s)", ax = ax)
    ax = fig.add_subplot(3, 3, 3)    
    dg[['rtime']].plot(kind = 'barh', title = "Real Time (s)", ax = ax)
    def scaleUnit(x):
        if (x.max() > 1024 ** 3).all():
            return ( 1024 ** 3, "Gb")
        if (x.max() > 1024 **  2).all():
            return ( 1024 ** 2, "Mb")
        if (x.max() > 1024).all():
            return ( 1024, "Kb")
        return ( 1, "B") 
    rssScale = scaleUnit(dRaw[['rss']])
    dg[['maxRss']] = dg[['maxRss']] / rssScale[0]
    ax = fig.add_subplot(3, 3, 4)    
    dg[['maxRss']].plot(kind = 'barh', title = "Max RSS (" + rssScale[1]+")", ax = ax)
    
    dg[['avgRss']] = dg[['avgRss']] / rssScale[0]
    ax = fig.add_subplot(3, 3, 5)
    dg[['avgRss']].plot(kind = 'barh', title = "Avg RSS (" + rssScale[1]+")", ax = ax)
    
    vmsScale = scaleUnit(dRaw[['vms']])
    dg[['maxVms']] = dg[['maxVms']] / vmsScale[0]
    ax = fig.add_subplot(3, 3, 6)
    dg[['maxVms']].plot(kind = 'barh', title = "Max VMS (" + vmsScale[1]+")", ax = ax)
    
    dg[['avgVms']] = dg[['avgVms']] / vmsScale[0]
    ax = fig.add_subplot(3, 3, 7)
    dg[['avgVms']].plot(kind = 'barh', title = "Avg VMS (" + vmsScale[1]+")", ax = ax)
    

    def calculateYLimit(x, coef = 1.5):
        a, b = x.min(), x.max()
        c = (a + b) / 2
        d = c - a
        return (c - d * 1.5, c + d * 1.5)
        
    dRaw['prog'] = dRaw.apply(lambda x: x['cmd'].split()[0] + '(%d)' % x['pid'] ,axis = 1)
    dRaw['rss'] = dRaw['rss'] / rssScale[0]
    ax = fig.add_subplot(3, 3, 8)        
    for k, v in dRaw.groupby('prog'):
        plt.plot(v['rtime'], v['rss'], label = k, marker = '.')

    plt.ylim(calculateYLimit(dRaw['rss']))
    plt.title("RSS (%s) vs. Real Time (s)" % rssScale[1])
    plt.legend()
    #plt.legend(bbox_to_anchor=(1.05, 1), loc = 2)

    dRaw[['vms']] = dRaw[['vms']] / vmsScale[0]
    ax = fig.add_subplot(3, 3, 9)        
    for k, v in dRaw.groupby('prog'):
        plt.plot(v['rtime'], v['vms'], label = k, marker = '.')
    plt.ylim(calculateYLimit(dRaw['vms']))
    plt.title("VMS (%s) vs. Real Time (s)" % vmsScale[1])
    plt.legend()    
    #plt.legend(bbox_to_anchor=(1.05, 1), loc = 2)

    fig.savefig(outFile)
    
def usage():
    print("Usage: ")
    print("%s [-i interval] [-o outputFile] [-s] [-t] [-g] [-q] commands" % sys.argv[0] )
    print(" -i interval: sampling interval")
    print(" -o outputFile: benchmark summary printed to 'outputFile' (default: stderr)")
    print(" -t: output trace of benchmarking metrics (default: stderr; use -o to change)")
    print(" -g: output a PNG graph showing cpu and memory usage (need matplotlib)")
    print(" -q: quiet mode, do not output anything to the console")
    print

if __name__ == '__main__':
    try:
        import getopt
        optlist, args = getopt.getopt(sys.argv[1:], 'i:o:hstgq')
        optlist = dict(optlist)
        interval = float(optlist.get('-i', 0.1))
        ## to avoid record too many snapshots, scale up the value of interval
        if '-i' in optlist:
            intervalScaling = None
        else:
            intervalScaling = 2 * interval
            
        if interval <= 0:
            print >> sys.stderr, "Sampling interval should be larger than zero, but [ %s ] given" % optlist.get('-i')
            sys.exit(1)
            
        if '-o' in optlist:
            outFile = optlist['-o']
        else:
            outFile = sys.stderr
            
        # useShell = '-s' in optlist
        outGraph = '-g' in optlist
        outTrace = '-t' in optlist
        trace = outGraph or outTrace
        quietMode = '-q' in optlist
        
        if '-h' in optlist:
            usage()
            sys.exit(0)

        if len(args) == 0:
            print >> sys.stderr, "No command(s) given. See helps below..."
            usage()
            sys.exit(0)
        ## print 'args = ', args
        command = args
    except:
        usage()
        raise
        sys.exit(1)

    import psutil
    import time
    import numpy as np
    import pandas as pd
    
    from collections import deque
    startTime = time.time()
    mainProc = psutil.Popen(command, shell = False)

    result = [] # time, pid, cwd, cmd, cpu_times, mem_info

    # gather metrics while process/sub-process is still running.
    mainProc.poll()  ## need to call poll() so is_running() can work
    activeSet = set()   ##
    active.add(mainProc.pid)
    while activeSet:
        ## put all processes to the active queuee
        newActiveSet = set()
        for p in activeSet:
            if p in newActiveSet: continue
            children = p.children()
            for c in children:
                if c.is_running():
                    newActiveSet.add(c)
        activeSet |= newActiveSet

        ## examine each active proc
        ## remove inactive proc
        for p in activeSet:
            try:
                val = [
                    time.time() - startTime,
                    p.pid,
                    p.ppid(),
                    p.cwd(),
                    p.cmdline(),
                    p.cpu_times(),
                    p.memory_info()
                ]
            except psutil.AccessDenied:
                val = [
                    time.time() - startTime,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
                ]
            if outTrace:
                print >> sys.stderr, val
            if val[1] != None:
                result.append(val)
                
            if not p.is_running():
                activeSet.del(p)

        ## automatically increase check interval to save memory
        if intervalScaling and len(result) % 1000 == 0:
            interval = intervalScaling
            intervalScaling *= 2
        ## wait a bit
        time.sleep(interval)
    
    # Summarize results
    df = pd.DataFrame.from_items([('pid', [i[1] for i in result]),
                       ('ppid', [i[2] for i in result]),
                       ('cwd', [i[3] for i in result]),
                       ('cmd', [' '.join(i[4]) for i in result]),
                       ('utime', [i[5].user for i in result]),
                       ('stime', [i[5].system for i in result]),
                       ('rtime', [i[0] for i in result]),
                       ('rss', [i[6].rss for i in result]),
                       ('vms', [i[6].vms for i in result])])
    if outFile != sys.stderr:
        df.to_csv(outFile + ".trace.csv", index = False)
        
    # Group by pid
    def f(x):
        tp = np.copy(x['rtime'])
        x['utime'] = np.max(x['utime'])
        x['stime'] = np.max(x['stime'])
        x['rtime'] = np.max(x['rtime'])
        x['maxRss'] = np.max(x['rss'])
        x['maxVms'] = np.max(x['vms'])
        x['avgRss'] = calculateMean(tp, x['rss'])
        x['avgVms'] = calculateMean(tp, x['vms'])
        return x
    dOut = df.groupby('pid').apply(f)
    dOut = dOut.drop_duplicates()
    # dOut = pd.concat([dfUniq, dfMax, dfMean], axis = 1)
    # print dOut
    if outFile == sys.stderr:
        if not quietMode:
            printTable(dOut)
    else:
        dOut.to_csv(outFile + '.csv', index = False)

    if outGraph:
        if outFile == sys.stderr:
            draw(df, dOut, "bench.png")
        else:
            draw(df, dOut, outFile + ".png")
