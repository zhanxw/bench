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

def usage():
    print("Usage: ")
    print("%s [-i interval] [-o outputFile] [-s] [-t] [-g] [-q] commands" % sys.argv[0] )
    print(" -i interval: sampling interval")
    print(" -o outputFile: benchmark summary printed to 'outputFile' (default: stderr)")
    #print(" -s: use /bin/sh -c 'cmd' to execute")
    print(" -t: output trace of benchmarking metrics (default: stderr; use -o to change)")
    print(" -g: output a PNG graph showing cpu and memory usage (need matplotlib and numpy)")
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
    from collections import deque
    mainProc = psutil.Popen(command, shell = False)

    result = [] # time, pid, cwd, cmd, cpu_times, mem_info

    # gather metrics while process/sub-process is still running.
    while True:
        # record process at one snapshot
        needToWait = False        
        queue = deque()
        mainProc.poll() 
        queue.append(mainProc)
        while len(queue) > 0:
            # print "len(queue) = ", len(queue), queue
            p = queue.popleft()

            if not p.is_running():
                continue
            needToWait = True
            # print (p), p.is_running()
            # append metrics
            try:
                val = [
                    time.time(),
                    p.pid,
                    p.ppid(),
                    p.cwd(),
                    p.cmdline(),
                    p.cpu_times(),
                    p.memory_info()
                ]
            except psutil.AccessDenied:
                val = [
                    time.time(),
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

            if intervalScaling and len(result) % 1000 == 0:
                interval = intervalScaling
                intervalScaling *= 2
                
            # append children
            children = p.children()
            for c in children:
                if c.is_running():
                    queue.append(c)
            time.sleep(interval)

        if not needToWait:
            break
    
    # Clean up results
    nResult = len(result)
    startTime = 0
    for i in xrange(nResult):
        if i == 0:
            startTime = result[i][0]
        result[i][0] -= startTime
        # print result[i]

    # Summarize results
    import pandas as pd
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
    dfUniq = df[['pid','ppid','cwd','cmd']].drop_duplicates()
    dfUniq.index = dfUniq['pid']
    dfMax = df[['pid','utime','stime', 'rtime', 'rss','vms']].groupby('pid').max()
    dfMax.columns = ['utime', 'stime', 'rtime', 'maxRss', 'maxVms']
    dfMean = df[['pid', 'rss','vms']].groupby('pid').mean()
    dfMean.columns = ['avgRss', 'avgVms']
    dOut = pd.concat([dfUniq, dfMax, dfMean], axis = 1)
    # print dOut
    if outFile == sys.stderr:
        if not quietMode:
            printTable(dOut)
    else:
        dOut.to_csv(outFile + '.csv', index = False)
    sys.exit(0)
