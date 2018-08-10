#!/usr/bin/python3

d = eval(open('items.txt','r').read())
z = d.copy()

""" # reduce dictionaries to just the name key
for x in z:
    if len(d[x].keys()) > 1:
        name = d[x]['name']
        d[x] = {}
        d[x]['name'] = name
"""

# turn dict of dicts into dict of strings (just the english names)
for x in z:
    dd = d[x].get('name',None)
    if dd is not None:
        if type(dd) == type({}):
            name = dd.get('en',None)
            if name is not None:
                d[x] = name

f = open('items.txt','w')
f.write(str(d))
f.close()
