#!/usr/bin/python3
# Prereq for Discord eve bot by admica
# Generate a static map of system_id to system name and info for every system in eve.
# Currently generates 8235 mappings.

from time import sleep
import requests

# start from here
leftoff = 0

url = 'https://esi.evetech.net/latest/universe/systems/'

r = requests.get(url)
rlist = eval(r.text)
print("{} system id's fetched.".format(len(rlist)))
with open('systems_list.txt','w') as f:
    f.write(r.text)

f = open('systems.txt','a')
d = {}
count = 0
for s in rlist:
    try:
        if int(s) > leftoff:
            r = requests.get('{}{}'.format(url, s))
            dd = eval(r.text)
            d[s] = dd
            print(dd)
            sleep(.25)
            count += 1
            print(count)

    except Exception as e:
        print("ERROR with {} system: {}".format(s, e))

with open('systems.txt','w') as f:
    f.write(str(d))

import sys
sys.exit(0)

