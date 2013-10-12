#!/net/fantasia/home/zhanxw/python27/bin/python
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

class MemoryUsage:
    def __init__(self, t = None, trace = False):
        self.vms = 0 # virtual memory, how many mem are claimed
        self.rss = 0 # resident memory, how many mem are in physical used
        self.totalTime = 0
        if t:
            self.lastTime = t
        else:
            self.lastTime = time()
        self.maxVms = -1
        self.maxRss = -1
        self.interval = interval
        self.trace = trace
        self.points = []

    def add(self, time, vms, rss):
        if self.trace:
            self.points.append( (time, vms, rss))
        self.maxVms = max(self.maxVms, vms)
        self.maxRss = max(self.maxRss, rss)

        newTime = (time - self.lastTime)
        if newTime == 0.0: 
            return
        self.vms = self.vms * (self.totalTime) + vms * newTime
        self.rss = self.rss * (self.totalTime) + rss * newTime
        self.totalTime += newTime
        self.lastTime = time
        
        self.vms /= self.totalTime
        self.rss /= self.totalTime
        #print "in add", self.vms, self.rss

    def getAverage(self):
        return (self.vms, self.rss)

    def getMax(self):
        return (self.maxVms, self.maxRss)

    def getTrace(self):
	return self.points
    
class CPUUsage:
    def __init__(self, trace = False):
        self.utime = 0 # user time
        self.stime = 0 # system time
        self.rtime = 0
        self.initTime = time()
	self.trace = trace
	self.points = []
	
    def add(self, utime, stime):
	if self.trace:
	    self.points.append( ( utime, stime, time()))
        self.utime = utime
        self.stime = stime
        #print "cpu time", self.utime, self.stime
    def finish(self):
        self.rtime = time() - self.initTime
    def getTime(self):
        #print "cpu time", self.utime, self.stime
        return (self.utime, self.stime, self.rtime)
    def getTrace(self):
	return self.points
    
## p is psutil instance
## interval is sampling interval
## q is queue to store result
def monitorProcess(p, q, interval, trace):
    ##pid = p.pid
    ## print "monitor pid = ", pid
    try:
	res = [p.pid, p.getcwd(), p.cmdline, CPUUsage(trace = trace), MemoryUsage(p.create_time, trace = trace)]

        while p.is_running():
            try:
                t = time()
                c = p.get_cpu_times()
                res[-2].add(c.user, c.system)
                m = p.get_memory_info()
                res[-1].add(t, m.vms, m.rss)
                sleep(interval)
            except:
                break
        res[-2].finish()
        q.put(res)
    except NoSuchProcess:
	pass

# start a process 
def startMainProcess(useShell, command, q):
    initTime = time()
    if useShell:
	proc = Process(target = os.system, args = (' '.join(command),))
	proc.start()
	p = psutil.Process(proc.pid)

    else:
	p = psutil.Popen(command, shell = False)

    res = [p.pid, p.getcwd(), p.cmdline, None, None, None]
    while p.is_running():
        #print "wait4", p.pid
	res[-1] = os.wait4(p.pid, 0)
	if useShell:
	    res[-2] = proc.exitcode
	else:
	    res[-2] = p.returncode
	res[-3] = time() - initTime
        ##print 'waitPid', res[-1]
    q.put(res)
    return

def usage():
    print("Usage: ")
    print("%s [-i interval] [-o outputFile] [-s] commands" % sys.argv[0] )
    print(" -i interval: sampling interval")
    print(" -o outputFile: output benchmark to file instead of stderr")
    print(" -s: use /bin/sh -c 'cmd' to execute")
    print(" -t: output trace of benchmarking metrics (default: stderr; use -o to change)")
    print(" -g: output a PNG graph showing cpu and memory usage (need matplotlib and numpy)")
    print(" -q: quiet mode, not output summary line")
    print

if __name__ == '__main__':
    try:
        import getopt
	optlist, args = getopt.getopt(sys.argv[1:], 'i:o:hstg')
	optlist = dict(optlist)
        interval = float(optlist.get('-i', 0.1))
	if interval <= 0:
	    print >> sys.stderr, "Sampling interval should be larger than zero, but [ %s ] given" % optlist.get('-i')
	    sys.exit(1)
	    
        if '-o' in optlist:
            outFile = open(optlist['-o'], 'wt')
        else:
            outFile = sys.stderr
	    
	useShell = '-s' in optlist
	outGraph = '-g' in optlist
	outTrace = '-t' in optlist
	trace = outGraph or outTrace
	quietMode = '-q' in optlist
	
        if '-h' in optlist:
            usage()
            sys.exit(0)

        if len(args) == 0:
	    print >> sys.stderr, "No command(s) given, exiting..."
	    sys.exit(1)
	## print 'args = ', args
	## commands = args
    except:
        usage()
	raise
        sys.exit(1)

    ## store results
    result = {} # key: pid, val: [cmd, command, cpu_usage, mem_usage]

    import psutil
    from multiprocessing import Process, Queue
    q = Queue()
    
    ## print "command", args
    mainProc = Process(target = startMainProcess, args = (useShell, args, q))
    mainProc.start()
    while True:
	## any process is runing?
	isRunning = False;
        
        try: 
            parent = psutil.Process(mainProc.pid)
            if mainProc.is_alive() and parent.is_running(): # running
                #print 'parent is running', parent
		if parent.pid not in result:
                    p = Process(target=monitorProcess, args = (parent, q, interval, trace))
                    result[parent.pid] = p
                    p.start()
		isRunning = True

		psList = parent.get_children(recursive=True)
		#print "len(child ps)", len(psList), [p.pid for p in psList]
		for p in psList:
		    if p.pid not in result:
                        proc = Process(target=monitorProcess, args = (p, q, interval, trace))
                        result[p.pid] = proc
                        proc.start()

		    if p.is_running():
			isRunning = True
        except psutil.NoSuchProcess:
            ## print 'no such process'
            pass
	if not isRunning:
	    break

	sleep(interval)

    ## outputs
    HEADER = ['PID', 'Prog', 'UsrTime', 'SysTime', 'RealTime',
              'MaxVms', 'MaxRss', 'AvgVms', 'AvgRss', 'Path',
              'Command']
    pythonPid = os.getpid()
    ## print "pythonPid = ", pythonPid
    for k, v in result.iteritems():
	if v.is_alive() and v.pid != pythonPid:
	    v.join(interval)
	    v.terminate()
	    
    res = {} # key: pid, val: values including PID
    cpuTraceOutput = []
    memTraceOutput = []
    accuratePid = set()
    while not q.empty():
        a = q.get()
        pid = a[0]
        if pid in res:
            r = res[pid]
        else:
            r = ['NA' for h in HEADER]
        
        r[0] = a[0]
	try: 
	    progName = os.path.basename(a[2][0])
	    r[1] = progName
	except:
	    pass
        r[9] = a[1]
        r[10] = '"%s"' % ' '.join(a[2])
        if isinstance(a[-1], MemoryUsage):
            r[2], r[3], r[4] = ['%.3f' % i for i in a[-2].getTime()]
            r[5], r[6] = a[-1].getMax()
            r[7], r[8] = a[-1].getAverage()

	    # output trace
	    if trace:
		cpuTrace = a[-2].getTrace()
		for cpuEntry in cpuTrace:
		    cpuTraceOutput.append([r[0], r[1], cpuEntry]) 
		memTrace = a[-1].getTrace()	
		for memEntry in memTrace:
		    memTraceOutput.append([r[0], r[1], memEntry])
		
        else:  # contain resource structure
            r[2] = a[-1][-1].ru_utime
            r[3] = a[-1][-1].ru_stime
            r[6] = a[-1][-1].ru_maxrss

	    accuratePid.add(r[0])
	    summaryLine = "%.2fu %.2fs %.2fr (rss)%dkb %d %s" % (r[2], r[3], a[-1][-3], int(r[6]/1024), a[-1][-2], ' '.join(a[2]))
	    ## print summaryLine
        res[pid] = r
    #print res
    print >> outFile, '\t'.join(HEADER)
    highPriKeys = [k for k in res.keys() if k in accuratePid]
    lowPriKeys = [k for k in res.keys() if k not in accuratePid]
    for k in highPriKeys:
	v = res[k]
        print >> outFile, '\t'.join(map(str, v))
    for k in lowPriKeys:
	v = res[k]
        print >> outFile, '\t'.join(map(str, v))

    if outFile != sys.stderr:
	outFile.close()

    CPU_TRACE_HEADER = ['PID', 'Prog', 'UsrTime', 'SysTime', 'RealTime']
    MEM_TRACE_HEADER = ['PID', 'Prog', 'Time', 'VMS', 'RSS']

    if outTrace:
	## output cpu trace
	if outFile == sys.stderr:
	    traceFile = outFile
	    print '-' * 50
	else:
	    traceFile = open(optlist['-o']+'.trace.cpu', 'wt')
	    print >>traceFile, '\t'.join(CPU_TRACE_HEADER)
	for cpuEntry in cpuTraceOutput:
	    print >> traceFile, '\t'.join(map(str, unlist(cpuEntry)))

	if outFile != sys.stderr:
	    traceFile.close()
	## output mem trace
	if outFile == sys.stderr:
	    traceFile = outFile
	    print '-' * 50
	else:
	    traceFile = open(optlist['-o']+'.trace.mem', 'wt')
	print >>traceFile, '\t'.join(MEM_TRACE_HEADER)
	for memEntry in memTraceOutput:
	    print >> traceFile, '\t'.join(map(str, unlist(memEntry)))
	if outFile != sys.stderr:
	    traceFile.close()

    # check if matplotlib is available
    hasMatplotlib = False
    try:
	from numpy  import array
	from pylab import *
	hasMatplotlib = True
    except:
	pass
    
    if outGraph:
	if not hasMatplotlib:
	    print >> sys.stderr, "Cannot find matplotlib, which is required for outputing graph."
	    sys.exit(1)
	    
	figure(figsize = (16, 8))
	subplot(1, 2, 1)
	from itertools import groupby
	data = groupby(cpuTraceOutput, key = lambda x: '%s (%d)' % (x[1], x[0]))
	for d in data:
	    legendKey = d[0]
	    a = [list(i[2:][0]) for i in d[1]]
	    #print a
	    v = array(a).transpose()
	    #print v
	    v[2, :] -= min(v[2, :])
	    
	    step(v[2,:], v[0,:], label = "User " + legendKey)
	    step(v[2,:], v[1,:], label = "Sys " + legendKey)
	xlabel("Real Time (second)")
	title("CPU Time Benchmark (second)")
	legend()

	subplot(1, 2, 2)
	data = groupby(memTraceOutput, key = lambda x: '%s (%d)' % (x[1], x[0]))
	memUnit = "b"
	for d in data:
	    legendKey = d[0]
	    a = [list(i[2:][0]) for i in d[1]]
	    #print a
	    v = array(a).transpose()
	    #print v
	    v[0, :] -= min(v[0, :])
	    v[1, :] /= 1024
	    v[2, :] /= 1024
	    memUnit = "kb"

	    if mean(v[1, :]) > 1024 and mean(v[2, :]) > 1024:
		v[1, :] /= 1024
		v[2, :] /= 1024
		memUnit = "Mb"
	    if mean(v[1, :]) > 1024 and mean(v[2, :]) > 1024:
		v[1, :] /= 1024
		v[2, :] /= 1024
		memUnit = "Gb"
		
	    step(v[0,:], v[1,:], label = "VMS " + legendKey)
	    step(v[0,:], v[2,:], label = "RSS " + legendKey)
	xlabel("Real Time (s)")
	title("Memory Benchmark (%s)" % memUnit )
	legend()

	if outFile == sys.stderr:
	    savefig("benchmark" + time.strftime("_%m%d_%H%M"),dpi=72)
	else:
	    savefig(optlist['-o'] + '.png', dpi = 72)

    if not quietMode:
	print >> sys.stderr, summaryLine
