#!/usr/bin/env python
import sys, os

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
    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except:
        print >> sys.stderr, "Cannot import matplotlib, skipping generating graphs"
        return
    
    plt.rc('legend', fontsize=6)
    plt.rc('ytick', labelsize = 'small')
    fig = plt.figure(figsize = (15, 15))
    ax = fig.add_subplot(3, 3, 1)
    ## increase space between subplots
    fig.subplots_adjust(wspace = .5, hspace = .5)

    getProgName = lambda x: x.split()[0].split('/')[-1]
    dg['prog'] = dg.apply(lambda x: getProgName(x['cmd']) + '(%d)' % x['pid'] ,axis = 1)
    dg.index = dg['prog']
    dg[['utime']].plot(kind = 'barh', title = "User Time (s)", ax = ax)
    plt.ylabel('')
    # plt.yticks(rotation = 45) # this does not produce nice looking graphs

    ax = fig.add_subplot(3, 3, 2)    
    dg[['stime']].plot(kind = 'barh', title = "System Time (s)", ax = ax)
    plt.ylabel('')        

    ax = fig.add_subplot(3, 3, 3)    
    dg[['rtime']].plot(kind = 'barh', title = "Real Time (s)", ax = ax)
    plt.ylabel('')

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
    plt.ylabel('')
    
    dg[['avgRss']] = dg[['avgRss']] / rssScale[0]
    ax = fig.add_subplot(3, 3, 5)
    dg[['avgRss']].plot(kind = 'barh', title = "Avg RSS (" + rssScale[1]+")", ax = ax)
    plt.ylabel('')
    
    vmsScale = scaleUnit(dRaw[['vms']])
    dg[['maxVms']] = dg[['maxVms']] / vmsScale[0]
    ax = fig.add_subplot(3, 3, 6)
    dg[['maxVms']].plot(kind = 'barh', title = "Max VMS (" + vmsScale[1]+")", ax = ax)
    plt.ylabel('')
    
    dg[['avgVms']] = dg[['avgVms']] / vmsScale[0]
    ax = fig.add_subplot(3, 3, 7)
    dg[['avgVms']].plot(kind = 'barh', title = "Avg VMS (" + vmsScale[1]+")", ax = ax)
    plt.ylabel('')    

    def calculateYLimit(x, coef = 1.5):
        a, b = x.min(), x.max()
        c = (a + b) / 2
        d = c - a
        if d == 0.0:
            return (a - 1, b + 1)
        return (c - d * 1.5, c + d * 1.5)
        
    dRaw['prog'] = dRaw.apply(lambda x: getProgName(x['cmd']) + '(%d)' % x['pid'] ,axis = 1)
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

    import time
    import psutil
    import numpy as np
    import pandas as pd
    
    if outTrace:
        print >> sys.stderr, '\t'.join(['pid', 'ppid', 'utime', 'stime', 'rtime', 'rss', 'vms', 'cwd', 'cmd'])
        
    startTime = time.time()
    mainProc = psutil.Popen(command, shell = False)

    result = [] # time, pid, cwd, cmd, cpu_times, mem_info

    # gather metrics while process/sub-process is still running.
    activeSet = set()   ##
    activeSet.add(mainProc)
    while activeSet:
        ## put all processes to the active queuee
        newActiveSet = set()
        mainProc.poll()  ## need to call poll() so is_running() can work
        for p in activeSet:
            if p in newActiveSet: continue
            try:
                children = p.children()
                for c in children:
                    if c.is_running():
                        newActiveSet.add(c)
            except psutil.NoSuchProcess:
                continue
        activeSet |= newActiveSet

        ## examine each active proc
        ## remove inactive proc
        toRemoveSet = set()
        for p in activeSet:
            try:
                val = [
                    time.time() - startTime,
                    p.pid,
                    p.ppid(),
                    p.cpu_times(),
                    p.memory_info(),
                    p.cwd(),
                    p.cmdline()
                ]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
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
                if val[1] != None:
                    print >> sys.stderr, '\t'.join(map(str, [val[1], val[2], val[3].user, val[3].system,val[0], val[4].rss, val[4].vms, val[5], ' '.join(val[6])]))
                else:
                    print >> sys.stderr, '\t'.join(map(str, [None, None, None, None, val[0], None, None, None,None]))
                
            if val[1] != None:
                result.append(val)
                
            if not p.is_running():
                toRemoveSet.add(p)
        activeSet -= toRemoveSet

        ## automatically increase check interval to save memory
        if intervalScaling and len(result) % 1000 == 0:
            interval = intervalScaling
            intervalScaling *= 2
        ## wait a bit
        time.sleep(interval)
    
    # Summarize results
    df = pd.DataFrame.from_items([('pid', [i[1] for i in result]),
                                  ('ppid', [i[2] for i in result]),
                                  ('utime', [i[3].user for i in result]),
                                  ('stime', [i[3].system for i in result]),
                                  ('rtime', [i[0] for i in result]),
                                  ('rss', [i[4].rss for i in result]),
                                  ('vms', [i[4].vms for i in result]),
                                  ('cwd', [i[5] for i in result]),
                                  ('cmd', [' '.join(i[6]) for i in result])
    ])
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
    dOut = dOut.drop_duplicates(subset = 'pid')
    dOut = pd.concat([dOut.drop(['cwd','cmd'], axis = 1), dOut[['cwd','cmd']]], axis = 1)
    # print df
    # print dOut
    if outFile != sys.stderr:
        dOut.to_csv(outFile + '.csv', index = False)
    elif not quietMode:
        printTable(dOut)

    if outGraph:
        if outFile == sys.stderr:
            draw(df, dOut, "bench.png")
        else:
            draw(df, dOut, outFile + ".png")
