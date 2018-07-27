#!/usr/bin/python3
# Prereq for Discord eve bot by admica

from time import sleep
import requests

# start from here
leftoff = 0

url = 'https://esi.evetech.net/latest/universe/constellations/'

try:
    f = open('const_list.txt','r')
    l = eval(f.read())
    f.close()
except:
    r = requests.get(url)
    rlist = eval(r.text)
    print("{} constellation id's fetched.".format(len(rlist)))
    with open('const_list.txt','w') as f:
        f.write(r.text)
    l = eval(r.text)

f = open('const.txt','a')
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
        print("ERROR {} const: {}".format(e, g))

with open('const.txt','w') as f:
    f.write(str(d))

import sys
sys.exit(0)

