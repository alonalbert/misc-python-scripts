#!/usr/bin/python3
import re
import sys
import statistics



if __name__ == '__main__':
    file = sys.argv[1]
    with open(file) as f:
        lines = f.readlines()

    init = []
    latency = []
    for line in lines:
        line = line.strip()[43:]
        m = re.match(r' * (\d+): Store:init', line)
        if m != None:
            init.append(int(m[1]))
            latency.append([])
            continue
        m = re.match(r'Time OneGoogleProvider: (\d+)', line)
        if m != None:
            latency[-1].append(int(m[1]))

    first = []
    last = []
    for l in latency:
        first.append(l[0])
        last.append(l[-1])


    print('Average init: %s' % statistics.mean(init))
    print('Average latency (First): %s' % statistics.mean(first))
    print('Average latency (Last): %s' % statistics.mean(last))
