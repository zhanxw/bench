#!/net/fantasia/home/zhanxw/python27/bin/python
import sys, os
def usage():
    print("Usage: ")
    print("%s [-i interval] [-o outputFile] commands" % sys.argv[0] )
    print

from time import time, sleep
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

class CPUUsage:
    def __init__(self):
        self.utime = 0 # user time
        self.stime = 0 # system time
        self.rtime = 0
        self.initTime = time()
    def add(self, utime, stime):
        self.utime = utime
        self.stime = stime
        #print "cpu time", self.utime, self.stime
    def finish(self):
        self.rtime = time() - self.initTime
    def getTime(self):
        #print "cpu time", self.utime, self.stime
        return (self.utime, self.stime, self.rtime)

## p is psutil instance
## interval is sampling interval
## q is queue to store result
def monitorProcess(p, interval, q):
    ##pid = p.pid
    ## print "monitor pid = ", pid
    res = [p.pid, p.getcwd(), p.cmdline, CPUUsage(), MemoryUsage(p.create_time)]
    from time import time, sleep
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

def runCommand(cmd):
    #print 'cmd = ', cmd
    ret = os.system(cmd)
    retcode = ret >> 8
    signalcode = ret & 0xff
    if signalcode != 0:
	sys.exit( signalcode + 128 )
    else:
	sys.exit( retcode )

def startMainProcess(command, q):
    proc = Process(target = runCommand, args = (' '.join(command),))
    proc.start()
    
    # cmd = "'" + ' '.join(command) + "'"
    # cmd = cmd.replace('\\', '\\\\')
    # cmd = ['/bin/sh', '-c', cmd]
    # print "psutil popen: ", cmd
    p = psutil.Process(proc.pid)
    # p = psutil.Popen(cmd)
    res = [p.pid, p.getcwd(), p.cmdline, None]
    while p.is_running():
        res[-1] = os.wait4(p.pid, 0)
	#print "wait4", p.pid
        ##print 'waitPid', res[-1]
    q.put(res)
    return

if __name__ == '__main__':
    try:
        import getopt
	optlist, args = getopt.getopt(sys.argv[1:], 'i:o:h')
	optlist = dict(optlist)
        interval = float(optlist.get('-i', 0.1))
        if '-o' in optlist:
            outFile = open(optlist['-o'], 'wt')
        else:
            outFile = sys.stderr
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
    ## waitPidResult = None

    import psutil
    from multiprocessing import Process, Queue
    q = Queue()
    
    ## print "command", args
    mainProc = Process(target = startMainProcess, args = (args, q))
    mainProc.start()
    while True:
	## any process is runing?
	isRunning = False;
        
        try: 
            parent = psutil.Process(mainProc.pid)
            if mainProc.is_alive() and parent.is_running(): # running
                #print 'parent is running', parent
		if parent.pid not in result:
                    p = Process(target=monitorProcess, args = (parent, interval, q))
                    result[parent.pid] = p
                    p.start()
		isRunning = True

		psList = parent.get_children(recursive=True)
		#print "len(child ps)", len(psList), [p.pid for p in psList]
		for p in psList:
		    if p.pid not in result:
                        proc = Process(target=monitorProcess, args = (p, interval, q))
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
	    v.join()
	    
    res = {} # key: pid, val: values including PID
    accuratePid = set()
    while not q.empty():
        a = q.get()
    	##print "q=", a
        # if isinstance(a[-1], MemoryUsage):
        #     print "avg= ", a[-1].getAverage()
        #     print "max = ", a[-1].getMax()
        #     print "cpu time = ", a[-2].getTime()
        pid = a[0]
        if pid in res:
            r = res[pid]
        else:
            r = ['NA' for h in HEADER]
        
        r[0] = a[0]
        r[1] = os.path.basename(a[2][0])
        if isinstance(a[-1], MemoryUsage):
            r[2], r[3], r[4] = ['%.2g' % i for i in a[-2].getTime()]
            r[5], r[6] = a[-1].getMax()
            r[7], r[8] = a[-1].getAverage()
        else:  # contain resource structure
            r[2] = a[-1][-1].ru_utime
            r[3] = a[-1][-1].ru_stime
            r[6] = a[-1][-1].ru_maxrss
	    accuratePid.add(r[0])
        r[9] = a[1]
        r[10] = '"%s"' % ' '.join(a[2])
        res[pid] = r
    #print res
    print >> outFile, '\t'.join(HEADER)
    highPriKeys = [k for k in res.keys() if k in accuratePid]
    lowPriKeys = [k for k in res.keys() if k not in accuratePid]
    for k in highPriKeys:
	v = res[k]
        print >> outFile, '\t'.join(map(str, v))
    ## print '*' * 50
    for k in lowPriKeys:
	v = res[k]
        print >> outFile, '\t'.join(map(str, v))

    outFile.close()
