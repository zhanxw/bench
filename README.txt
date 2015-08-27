Monitor Process Resources Usage
===============================

Bench aims to be a handy tool with these functions:

    -  Monitor CPU time (user time, sys time, real time)
    -  Monitor memory usage (vms usage, rss usage)
    -  Output to TSV(tab-delimited files)
    -  Output benchmarking metrics
    -  Visualize benchmarking over time

Examples
========

-  Example 1: simple command

.. raw:: html

   <!-- -->

::

    > monitor.py sleep 2
    pid     ppid    cwd     cmd     utime   stime   rtime   maxRss  maxVms  avgRss  avgVms
    99627   99626   /home/zhanxw/mycode/bench       sleep 2 0.0     0.0     1.8569419384    835584  6066176 835584  6066176

-  Example 2: complex shell commands with samping interval equaing 0.5
   second

.. raw:: html

   <!-- -->

::

    > monitor.py sh -c 'sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait'
    pid     ppid    cwd     cmd     utime   stime   rtime   maxRss  maxVms  avgRss  avgVms
    100673  100672  /home/zhanxw/mycode/bench       sh -c sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait 0.0     0.0     3.6947889328    897024  4558848 897024  4558848
    100674  100673  /home/zhanxw/mycode/bench       sleep 2 0.0     0.0     1.68072605133   684032  6066176 684032  6066176
    100675  100673  /home/zhanxw/mycode/bench       sleep 4 0.0     0.0     3.86425089836   700416  6066176 700416  6066176

-  Example 3: generate benmarking metrics to external file

The small program, burnCpu, will keep CPU running for several seconds.
Its source code is under src/.

::

    > monitor.py -t -o burnCpu ./burnCpu
    [1440476547.641628, 104060, 104059, '/home/zhanxw/mycode/bench/src', ['./burnCpu'], pcputimes(user=0.0, system=0.0), pmem(rss=1425408, vms=12984320)]
    [1440476547.79734, 104060, 104059, '/home/zhanxw/mycode/bench/src', ['./burnCpu'], pcputimes(user=0.15, system=0.0), pmem(rss=1425408, vms=12984320)]
    [1440476547.960703, 104060, 104059, '/home/zhanxw/mycode/bench/src', ['./burnCpu'], pcputimes(user=0.32, system=0.0), pmem(rss=1425408, vms=12984320)]
    [1440476548.127665, 104060, 104059, '/home/zhanxw/mycode/bench/src', ['./burnCpu'], pcputimes(user=0.48, system=0.0), pmem(rss=1425408, vms=12984320)]
    ...

Additional result are stored in *burnCpu.csv*, *burnCpu.trace.csv* in
the Comma-separated format (CSV).

*burnCpu.csv* content

::

    pid,ppid,cwd,cmd,utime,stime,rtime,maxRss,maxVms,avgRss,avgVms
    104060,104059,/home/zhanxw/mycode/bench/src,./burnCpu,5.88,0.0,5.87858390808,1425408,12984320,1425408,12984320

*burnCpu.trace.csv* content

::

    pid,ppid,cwd,cmd,utime,stime,rtime,rss,vms
    104060,104059,/home/zhanxw/mycode/bench/src,./burnCpu,0.0,0.0,0.0,1425408,12984320
    104060,104059,/home/zhanxw/mycode/bench/src,./burnCpu,0.15,0.0,0.155711889267,1425408,12984320
    104060,104059,/home/zhanxw/mycode/bench/src,./burnCpu,0.32,0.0,0.319074869156,1425408,12984320
    104060,104059,/home/zhanxw/mycode/bench/src,./burnCpu,0.48,0.0,0.486037015915,1425408,12984320
    104060,104059,/home/zhanxw/mycode/bench/src,./burnCpu,0.65,0.0,0.653388023376,1425408,12984320
    ...

By using the trace output file, *burnCpu.trace.csv*, you can draw
benchmarking graphs, such as:

|image| NOTE ====

    Shell (/bin/sh) can be used to execute commands. You can use "sh -c
    'command arg1 arg2 ... '".

    bench requires `psutil <https://pypi.python.org/pypi/psutil>`__ to
    collect basic benchmarking metrics. We used psutil version 3.1.1 in
    development.

Contact
=======

    Xiaowei Zhan

.. |image| image:: http://zhanxw.com/bench/burnCpu.mon.png
