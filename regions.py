#!/usr/bin/python3
# Prereq for Discord eve bot by admica

from time import sleep
import requests

# start from here
leftoff = 0

url = 'https://esi.evetech.net/latest/universe/regions/'

try:
    f = open('regions_list.txt','r')
    l = eval(f.read())
    f.close()
except:
    r = requests.get(url)
    rlist = eval(r.text)
    print("{} region id's fetched.".format(len(rlist)))
    with open('regions_list.txt','w') as f:
        f.write(r.text)
    l = eval(r.text)

f = open('regions.txt','a')
d = {}
count = 0
for g in l:
    try:
        if int(g) > leftoff:
            fullurl = '{}{}'.format(url, g)
            print(fullurl)
            r = requests.get(fullurl)
            dd = eval(r.text)
            d[g] = dd
            print(dd)
            sleep(.5)
            count += 1
            print(count)

    except Exception as e:
        print("ERROR {} region: {}".format(e, g))

with open('regions.txt','w') as f:
    f.write(str(d))

import sys
sys.exit(0)

