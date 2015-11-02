Monitor Process Resources Usage
===============================

Bench aims to be a handy tool with these functions:

-   Monitor CPU time (user time, system time, real time)
-   Monitor memory usage (virtual memory usage, resident memory usage)
-   Output to TSV(tab-delimited files)
-   Output benchmark metrics
-   Visualize performance metrics (memory consumptions) over time

Examples
========

We showed several examples below. **Please note that all output are tabularized for demonstration purpose.**

Example 1: A simple command
---------------------------

This will start the process *sleep* for 2 seconds. The tabular output below was from the actual command: `monitor.py sleep 2 2>&1 | column -t -s $'\t'`.
If you simply run `monitor.py sleep 2`, you will get tab-deliminated outputs in standard error (stderr).
    
        $> monitor.py sleep 2
        pid     ppid    utime  stime  rtime         rss     vms      maxRss  maxVms   avgRss    avgVms     cwd                                cmd
        133692  133675  0.0    0.0    1.9368159771  774144  6066176  774144  6066176  774144.0  6066176.0  /home/zhanxw/mycode/bench/scripts  sleep 2


Example 2: A complex shell command with a sampling interval of 0.1 second
-------------------------------------------------------------------------

This example will use shell to start 3 processes: `sleep 2`, `sleep 4` and `seq 1000000`. As you can see, bench monitors all 4 processes.

        $> monitor.py sh -c 'sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait'
        pid     ppid    utime  stime  rtime            rss     vms      maxRss  maxVms   avgRss    avgVms     cwd                                cmd
        135004  134985  0.0    0.0    3.9532430172     798720  4558848  798720  4558848  798720.0  4558848.0  /home/zhanxw/mycode/bench/scripts  sh -c sleep 2 & sleep 4 & seq 10000000 >/dev/null & wait
        135006  135004  0.0    0.0    3.95348381996    655360  6066176  655360  6066176  655360.0  6066176.0  /home/zhanxw/mycode/bench/scripts  sleep 4
        135005  135004  0.0    0.0    1.83160495758    774144  6066176  774144  6066176  774144.0  6066176.0  /home/zhanxw/mycode/bench/scripts  sleep 2
        135007  135004  0.05   0.0    0.0599648952484  720896  6090752  720896  6090752  720896.0  6090752.0  /home/zhanxw/mycode/bench/scripts  seq 10000000


Example 3: Generating performance metrics into an external file
---------------------------------------------------------------

Here we used a small program, `burnCpu`. It will keep the CPU running for several seconds. Its source code is under `src/`.

The option `-t` will enable outputting traces. That means at several time stops, performance metrics of each processes will be written to standard error as well as a separate comma-separated file, `$prefix.trace.csv`.

The option `-g` will generate a graph which contains several sub-figures, including timings for each process, memory consumption for each process, and memory consumption over each process' running time.

The option `-o` will specify the output prefix. The default value will be `bench`, meaning, you will get `bench.csv`. You can overwrite this value by using `-o` option.
    
        $> monitor.py -t -g -o burnCpu ./burnCpu
        pid     ppid    utime  stime  rtime            rss      vms       cwd                                cmd
        135471  135454  0.04   0.0    0.0441780090332  1449984  12984320  /home/zhanxw/mycode/bench/scripts  ../src/burnCpu
        135471  135454  0.2    0.0    0.205282926559   1449984  12984320  /home/zhanxw/mycode/bench/scripts  ../src/burnCpu
        135471  135454  0.38   0.0    0.381079912186   1449984  12984320  /home/zhanxw/mycode/bench/scripts  ../src/burnCpu
        ...


Additional results are stored in *burnCpu.csv* and *burnCpu.trace.csv* in the Comma-separated format (CSV).

*burnCpu.csv* file contents:

    pid,ppid,utime,stime,rtime,rss,vms,maxRss,maxVms,avgRss,avgVms,cwd,cmd
    144433,144416,5.4,0.0,5.40555810928,1404928,12984320,1404928,12984320,1404928.0,12984320.0,/home/zhanxw/mycode/bench/scripts,../src/burnCpu

*burnCpu.trace.csv* file contents:

    pid,ppid,utime,stime,rtime,rss,vms,cwd,cmd
    144433,144416,0.03,0.0,0.0423669815063,1404928,12984320,/home/zhanxw/mycode/bench/scripts,../src/burnCpu
    144433,144416,0.19,0.0,0.20046210289,1404928,12984320,/home/zhanxw/mycode/bench/scripts,../src/burnCpu
    144433,144416,0.36,0.0,0.373480081558,1404928,12984320,/home/zhanxw/mycode/bench/scripts,../src/burnCpu
    ...


When `-g` optioned is specified, bench will generate several performance metrics in the file *burnCpu.png*:

![image](http://zhanxw.com/bench/burnCpu.png)

Notes
=====

To benchmark a complex command or combination of commands, you can use shell (sh or bash) . For example, you can use `sh -c 'command arg1 arg2 ... '` (see Example 2).

Bench requires [psutil](https://pypi.python.org/pypi/psutil) to collect basic performance metrics, [numpy](http://www.numpy.org/) and [pandas](http://pandas.pydata.org/) for statistical calculations, and optionally [matplotlib](http://matplotlib.org/) for graphs.
In this release, we used psutil 3.1.1, numpy 1.8.2, pandas 0.16.2 and matplotlib 1.4.3.

Contact
=======

For questions or comments, please [visit the github repo](https://github.com/zhanxw/bench) or email zhanxw[at]gmail.com.
