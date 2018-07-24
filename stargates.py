#!/usr/bin/python3
# Prereq for Discord eve bot by admica
# Generate a static map of stargates for every system in eve.
# Currently generates 13824 mappings.

from time import sleep
import requests

# start from here
leftoff = 0

url = 'https://esi.evetech.net/latest/universe/stargates/'

f = open('stargates_list.txt','r')
l = eval(f.read())
f.close()

f = open('stargates.txt','a')
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
        print("ERROR {} system: {}".format(e, g))

with open('stargates.txt','w') as f:
    f.write(str(d))

import sys
sys.exit(0)

