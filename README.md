Monitor Process Resources Usage
===============================

Bench is able to monitor:
  ~ -   CPU time (user time, sys time, real time)
    -   Memory usage (vms usage, rss usage)
    -   Output to TSV(tab-delimited files)

Examples
========

-   Example 1: simple command

<!-- -->

    > monitor.py  sleep 2
    PID Prog    UsrTime SysTime RealTime    MaxVms  MaxRss  AvgVms  AvgRss  Path    Command
    21056   python  0   0   1.9 77705216    6696960 77705216.0  6696960.0   /home/zhanxw    "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py sleep 2"
    21057   sleep   0   0   1.8 7581696 368640  7581696.0   368640.0    /home/zhanxw    "sleep 2"
    21054   python  0   0   2.1 77705216    6991872 74768556.8744   6687656.42056   /home/zhanxw    "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py sleep 2"

-   Example 2: complex shell commands

<!-- -->

    > monitor.py -i 0.1 'sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait'
    PID Prog    UsrTime SysTime RealTime    MaxVms  MaxRss  AvgVms  AvgRss  Path    Command
    21920   python  0   0   3.9 77713408    6701056 77713408.0  6701056.0   /home/zhanxw    "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py -i 0.1 sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait"
    21921   sh  0   0   3.8 12886016    1417216 12886016.0  1417216.0   /home/zhanxw    "sh -c sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait"
    21922   sleep   0   0   1.8 7581696 368640  7581696.0   368640.0    /home/zhanxw    "sleep 2"
    21923   sleep   0   0   3.8 7581696 368640  7581696.0   368640.0    /home/zhanxw    "sleep 4"
    21924   seq 0.55    0   0.4 7602176 630784  7602176.0   630784.0    /home/zhanxw    "seq 1000000"
    21918   python  0   0   4.1 77713408    7000064 76043060.5519   6826628.73828   /home/zhanxw    "/home/zhanxw/python27/bin/python /home/zhanxw/bin/monitor.py -i 0.1 sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait"

NOTE
====

> Shell (/bin/sh) are used to execute commands. It's a convenient
> feature with some shell exploit hazard.
>
> This version requires psutil.

Contact
=======

> Xiaowei Zhan<zhanxw[at]gmail.com\>

