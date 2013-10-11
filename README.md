Monitor Process Resources Usage
===============================

Bench aims to be a handy tool with these functions:
  ~ -   Monitor CPU time (user time, sys time, real time)
    -   Monitor memory usage (vms usage, rss usage)
    -   Output to TSV(tab-delimited files)
    -   Output benchmarking metrics
    -   Visualize benchmarking over time

Examples
========

-   Example 1: simple command

<!-- -->

    > monitor.py sleep 2
    PID Prog    UsrTime SysTime RealTime    MaxVms  MaxRss  AvgVms  AvgRss  Path    Command
    26183   sleep   0.000   0.000   2.010   7581696 368640  7581696.0   368640.0    /home/zhanxw/anno/paper/benchmark.vcf   "sleep 2"
    26181   python  0.000   0.000   2.109   78802944    7118848 75075881.6664   6807216.41318   /home/zhanxw/anno/paper/benchmark.vcf   "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py sleep 2"

-   Example 2: complex shell commands with samping interval equaing 0.5
    second

<!-- -->

    > monitor.py -s -i 0.5 'sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait'
    PID Prog    UsrTime SysTime RealTime    MaxVms  MaxRss  AvgVms  AvgRss  Path    Command
    26561   python  0.000   0.000   4.007   77750272    6758400 77750272.0  6758400.0   /home/zhanxw/anno/paper/benchmark.vcf   "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py -s -i 0.5 sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait"
    26562   sh  0.000   0.000   3.506   12881920    1413120 12881920.0  1413120.0   /home/zhanxw/anno/paper/benchmark.vcf   "sh -c sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait"
    26563   sleep   0.000   0.000   1.503   7581696 368640  7581696.0   368640.0    /home/zhanxw/anno/paper/benchmark.vcf   "sleep 2"
    26564   sleep   0.000   0.000   3.506   7581696 368640  7581696.0   368640.0    /home/zhanxw/anno/paper/benchmark.vcf   "sleep 4"
    26565   seq 0.580   0.010   0.501   7602176 634880  7602176.0   634880.0    /home/zhanxw/anno/paper/benchmark.vcf   "seq 1000000"
    26559   python  0.000   0.000   4.507   77754368    7045120 77750843.0692   7045120.0   /home/zhanxw/anno/paper/benchmark.vcf   "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py -s -i 0.5 sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait"

-   Example 3: generate benmarking metrics and graphs to external file

::
  ~ \> monitor.py -t -o burnCpu.mon -g ./burnCpu

Result are stored in *burnCpu.mon*, *burnCpu.mon.trace.cpu*,
*burnCpu.mon.trace.mem* and *burnCpu.mon.png*.

*burnCpu.mon* content

    PID Prog    UsrTime SysTime RealTime    MaxVms  MaxRss  AvgVms  AvgRss  Path    Command
    29900   burnCpu 7.480   0.000   7.532   12730368    839680  12730368.0  839680.0    /home/zhanxw/mycode/bench   "./burnCpu"
    29898   python  0.000   0.000   7.732   78807040    7118848 76893692.4593   7018742.03273   /home/zhanxw/mycode/bench   "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py -t -o burnCpu.mon -g ./burnCpu"

*burnCpu.mon.trace.cpu* content

    PID Prog    UsrTime SysTime RealTime
    29900   burnCpu 0.06    0.0 1381423522.56
    29900   burnCpu 0.16    0.0 1381423522.66
    29900   burnCpu 0.26    0.0 1381423522.76
    29900   burnCpu 0.36    0.0 1381423522.86
    29900   burnCpu 0.46    0.0 1381423522.96
    29900   burnCpu 0.56    0.0 1381423523.06
    ...

*burnCpu.mon.trace.mem* content

    PID Prog    Time    VMS RSS
    29900   burnCpu 1381423522.56   12730368    839680
    29900   burnCpu 1381423522.66   12730368    839680
    29900   burnCpu 1381423522.76   12730368    839680
    29900   burnCpu 1381423522.86   12730368    839680
    29900   burnCpu 1381423522.96   12730368    839680

*burnCpu.mon.png* graph

![image](http://zhanxw.com/bench/burnCpu.mon.png)
NOTE
====

> Shell (/bin/sh) are used to execute commands. It's a convenient
> feature with some shell exploit hazard.
>
> bench requires [psutil](https://code.google.com/p/psutil/) to collect
> basic benchmarking metrics, and requires
> [numpy](http://www.numpy.org/) and
> [matplotlib](http://matplotlib.org/) to generate benchmark graphs.

Contact
=======

> Xiaowei Zhan<zhanxw[at]gmail.com\>
