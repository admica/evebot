#!/usr/bin/python3
# Prereq for Discord eve bot by admica
# Generate a static map of system_id to system name for every system in eve.
# Currently generates 8235 mappings.

from time import sleep
import requests

# start from here
leftoff = 1

url = 'https://esi.evetech.net/dev/universe/systems/'

r = requests.get(url)
rlist = eval(r.text)
print("{} system id's fetched.".format(len(rlist)))
with open('systems_list.txt','w') as f:
    f.write(r.text)

f = open('systems.txt','a')
for s in rlist:
    try:
        if int(s) > leftoff:
            r = requests.get('{}{}'.format(url, s))
            d = eval(r.text)
            name = d['name']
            text = '"{}":"{}",'.format(s,name)
            try:
                print(text)
            except Exception as e:
                print("UNPRINTABLE system {}".format(s))
            f.write(text)
            f.flush()
            sleep(.05)
    except Exception as e:
        print("ERROR with {} system: {}".format(s, e))

# don't forget to remove final char
# then include { and } at start and end to make eval()'able.
