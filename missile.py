#!/usr/bin/python -OOtt

import operator

s = {}

s['malediction'] = {}
s['malediction']['name'] = 'Malediction'
s['malediction']['low'] = 33.0 # signature radius
s['malediction']['big'] = 70.1 # signature radius with MWD
s['malediction']['slow'] = 760.0 # base speed with MWD off
s['malediction']['fast'] = 5407.5 # mwd speed (+5%, base is 5150.0)
s['malediction']['a_low'] =  [ 'Precision Light Missile', 38.8, 18.8, 306.0, 21.1, 'None' ] # missile type, dps, radius, velocity, desc
s['malediction']['a_medium'] = [ 'Light Missile', 44.5, 30.0, 255.0, 42.2, 'None' ]
s['malediction']['a_high'] =  [ 'Fury Light Missile', 54.3, 51.8, 214.0, 31.6, 'None' ]
s['malediction']['b_low'] =  [ 'Precision Light Missile', 47.7, 18.8, 306.0, 21.1, 'BCS' ]
s['malediction']['b_medium'] = [ 'Light Missile', 54.7, 30.0, 255.0, 42.2, 'BCS' ]
s['malediction']['b_high'] =  [ 'Fury Light Missile', 66.7, 51.8, 214.0, 31.6, 'BCS' ]

s['orthrus'] = {}
s['orthrus']['name'] = 'Orthrus'
s['orthrus']['low'] = 203.0
s['orthrus']['big'] = 1190.0
s['orthrus']['slow'] = 288.0
s['orthrus']['fast'] = 2183.0
s['orthrus']['a_low'] =  [ 'Precision Light Missile', 342.0, 18.8, 306.0, 38.0, '2xBCS' ]
s['orthrus']['a_medium'] = [ 'Light Missile', 391.0, 30.0, 255.0, 75.9, '2xBCS' ]
s['orthrus']['a_high'] =  [ 'Fury Light Missile', 478.0, 51.8, 214.0, 57.0, '2xBCS' ]
s['orthrus']['b_low'] =  [ 'Precision Light Missile', 286.0, 17.6, 324.0, 42.3, 'BCS+MGE' ]
s['orthrus']['b_medium'] = [ 'Light Missile', 327.0, 28.2, 270.0, 84.7, 'BCS+MGE' ]
s['orthrus']['b_high'] =  [ 'Fury Light Missile', 399.0, 48.6, 227.0, 63.5, 'BCS+MGE' ]

s['typhoon'] = {}
s['typhoon']['name'] = 'Typhoon'
s['typhoon']['low'] = 825.0
s['typhoon']['big'] = 4540.0
s['typhoon']['slow'] = 193.0
s['typhoon']['fast'] = 1404.0
s['typhoon']['a_low'] =  [ 'Precision Heavy Missile', 643.0, 93.8, 146.0, 40.9, '2xBCS' ]
s['typhoon']['a_medium'] = [ 'Heavy Missile', 738, 105.0, 122.0, 81.7, '2xBCS' ]
s['typhoon']['a_high'] =  [ 'Fury Heavy Missile', 865, 181.0, 102.0, 61.3, '2xBCS' ]
s['typhoon']['b_low'] =  [ 'Precision Heavy Missile', 538, 88.1, 154.0, 44.8, 'BCS+MGE' ]
s['typhoon']['b_medium'] = [ 'Heavy Missile', 617, 98.7, 129.0, 89.6, 'BCS+MGE' ]
s['typhoon']['b_high'] =  [ 'Fury Heavy Missile', 723, 170.0, 108.0, 67.2, 'BCS+MGE' ]

# EFT fits used for above
s['orthrus']['eft'] = '''[Orthrus, Trya Tadaruwa's Orthrus]
Ballistic Control System II
Ballistic Control System II
Damage Control II
Sentient Signal Amplifier

50MN Cold-Gas Enduring Microwarpdrive
Caldari Navy Warp Scrambler
Large Shield Extender II
Large Shield Extender II
Republic Fleet Warp Disruptor

Medium Energy Neutralizer II
Rapid Light Missile Launcher II,Caldari Navy Mjolnir Light Missile
Rapid Light Missile Launcher II,Caldari Navy Mjolnir Light Missile
Rapid Light Missile Launcher II,Caldari Navy Mjolnir Light Missile
Rapid Light Missile Launcher II,Caldari Navy Mjolnir Light Missile
Rapid Light Missile Launcher II,Caldari Navy Mjolnir Light Missile

Medium Anti-EM Screen Reinforcer II
Medium Anti-Thermal Screen Reinforcer II
Medium Hydraulic Bay Thrusters II

Acolyte II x3
Acolyte II x2'''

s['typhoon']['eft'] = '''[Typhoon, typhoon]
Ballistic Control System II
Missile Guidance Enhancer II
Damage Control II
Energized Adaptive Nano Membrane II
Nanofiber Internal Structure II
Nanofiber Internal Structure II
Large Ancillary Armor Repairer, Nanite Repair Paste

500MN Quad LiF Restrained Microwarpdrive
Warp Disruptor II
Federation Navy Stasis Webifier
Large Micro Jump Drive
Heavy Capacitor Booster II, Navy Cap Booster 800

Heavy Energy Neutralizer II
Rapid Heavy Missile Launcher II, Scourge Precision Heavy Missile
Rapid Heavy Missile Launcher II, Scourge Precision Heavy Missile
Rapid Heavy Missile Launcher II, Scourge Precision Heavy Missile
Rapid Heavy Missile Launcher II, Scourge Precision Heavy Missile
Rapid Heavy Missile Launcher II, Scourge Precision Heavy Missile
Rapid Heavy Missile Launcher II, Scourge Precision Heavy Missile

Large Hydraulic Bay Thrusters I
Large Hydraulic Bay Thrusters I
Large Ionic Field Projector II

Federation Navy Hammerhead x5
Hobgoblin II x5
Warrior II x5'''

s['malediction']['eft'] = '''[Malediction, Malediction fit]

Damage Control II
Small Ancillary Armor Repairer
Overdrive Injector System II
Overdrive Injector System II

5MN Quad LiF Restrained Microwarpdrive
Warp Disruptor II
Initiated Compact Warp Scrambler

Light Missile Launcher II, Scourge Fury Light Missile
Light Missile Launcher II, Scourge Fury Light Missile
Light Missile Launcher II, Scourge Fury Light Missile

Small Polycarbon Engine Housing II
Small Ionic Field Projector II'''

drf = {}
drf['Auto-Targeting Cruise Missile'] = 0.882
drf['Auto-Targeting Heavy Missile'] = 0.682
drf['Auto-Targeting Light Missile'] = 0.604
drf['Citadel Cruise Missile'] = 0.882
drf['Citadel Torpedo'] = 1.00
drf['Cruise Missile'] = 0.882
drf['Fury Cruise Missile'] = 0.908
drf['Fury Heavy Missile'] = 0.882
drf['Fury Light Missile'] = 0.682
drf['Heavy Assault Missile'] = 0.882
drf['Heavy Missile'] = 0.682
drf['Javelin Heavy Assault Missile'] = 0.895
drf['Javelin Rocket'] = 0.682
drf['Javelin Torpedo'] = 0.967
drf['Light Missile'] = 0.604
drf['Precision Cruise Missile'] = 0.735
drf['Precision Heavy Missile'] = 0.583
drf['Precision Light Missile'] = 0.561
drf['Rage Heavy Assault Missile'] = 0.920
drf['Rage Rocket'] = 0.882
drf['Rage Torpedo'] = 0.967
drf['Rocket'] = 0.644
drf['Torpedo'] = 0.944

def calc(attacker, missile_type, victim, ship_speed, slot='a', web=0):
    """attacker -> dictionary of ship, shooting missiles to include high, medium, and low loadout
    victim -> dictionary of victim ship to include sig radius and speeds for both on and off propmod
    victim_speed -> slow or fast
    slot -> assumes attackers a_low/med/high loadout, but can be other prefixes to calculate other loadouts
    web -> percentage webs on the victim, 60=T2, 81=2xT2 webs, 90=daredevil"""

    zlow = '{}_low'.format(slot)
    zmedium = '{}_medium'.format(slot)
    zhigh = '{}_high'.format(slot)

    # raw damage
    # missile explosion radius
    # missile explosion velocity
    # missile damage reduction factor
    if missile_type == 'low':
        mtype = attacker[zlow][0]
        f = drf[mtype]
        dmg = attacker[zlow][1]
        e = attacker[zlow][2]
        ve = attacker[zlow][3]
        max_range = attacker[zlow][4]
        desc = attacker[zlow][5]
    elif missile_type == 'medium':
        mtype = attacker[zmedium][0]
        f = drf[ mtype ]
        dmg = attacker[zmedium][1]
        e = attacker[zmedium][2]
        ve = attacker[zmedium][3]
        max_range = attacker[zmedium][4]
        desc = attacker[zmedium][5]
    else: # 'high'
        mtype = attacker[zhigh][0]
        f = drf[ mtype ]
        dmg = attacker[zhigh][1]
        e = attacker[zhigh][2]
        ve = attacker[zhigh][3]
        max_range = attacker[zhigh][4]
        desc = attacker[zhigh][5]

    # target signature radius
    # target velocity
    if ship_speed == 'slow':
        s = victim['low']
        if web > 0:
            vt = victim['slow'] - (1-(web/100.0))
        else:
            vt = victim['slow']
    else: # 'fast'
        s = victim['big']
        if web > 0:
            vt = victim['fast'] * (1-(web/100.0))
        else:
            vt = victim['fast']

    # take the minimum of 3 possible calculations
    reduction = [ dmg ] # full damage
    reduction.append( dmg*(s/e) ) # sig reduced
    reduction.append( dmg*(((s/e)*(ve/vt))**f) ) # sig and velocity reduction
    damage = int(min(reduction))

    if web > 0:
        text = '{} + {} + {} = {} DPS to {} doing {}m/s ({}% web) to {}km'.format(attacker['name'], desc, mtype, damage, victim['name'], int(vt), web, max_range)
    else:
        text = '{} + {} + {} = {} DPS to {} doing {}m/s to {}km'.format(attacker['name'], desc, mtype, damage, victim['name'], int(vt), max_range)
    return ( text, damage, attacker['name'], mtype, victim['name'], ship_speed )


def matrix(x, y):
    data = []
    data.append(calc(s[x], 'low', s[y], 'slow', slot='a', web=0))
    data.append(calc(s[x], 'low', s[y], 'fast', slot='a', web=0))
    data.append(calc(s[x], 'low', s[y], 'fast', slot='a', web=60))
    data.append(calc(s[x], 'medium', s[y], 'slow', slot='a', web=0))
    data.append(calc(s[x], 'medium', s[y], 'fast', slot='a', web=0))
    data.append(calc(s[x], 'medium', s[y], 'fast', slot='a', web=60))
    data.append(calc(s[x], 'high', s[y], 'slow', slot='a', web=0))
    data.append(calc(s[x], 'high', s[y], 'fast', slot='a', web=0))
    data.append(calc(s[x], 'high', s[y], 'fast', slot='a', web=60))
    data.append(calc(s[x], 'low', s[y], 'slow', slot='b', web=0))
    data.append(calc(s[x], 'low', s[y], 'fast', slot='b', web=0))
    data.append(calc(s[x], 'low', s[y], 'fast', slot='b', web=60))
    data.append(calc(s[x], 'medium', s[y], 'slow', slot='b', web=0))
    data.append(calc(s[x], 'medium', s[y], 'fast', slot='b', web=0))
    data.append(calc(s[x], 'medium', s[y], 'fast', slot='b', web=60))
    data.append(calc(s[x], 'high', s[y], 'slow', slot='b', web=0))
    data.append(calc(s[x], 'high', s[y], 'fast', slot='b', web=0))
    data.append(calc(s[x], 'high', s[y], 'fast', slot='b', web=60))
    data.sort(key=operator.itemgetter(2))
    return data

data = matrix('malediction', 'malediction')
for item in data:
    print(item[0])
print
data = matrix('malediction', 'orthrus')
for item in data:
    print(item[0])
print
data = matrix('malediction', 'typhoon')
for item in data:
    print(item[0])
print

data = matrix('orthrus', 'malediction')
for item in data:
    print(item[0])
print
data = matrix('orthrus', 'orthrus')
for item in data:
    print(item[0])
print
data = matrix('orthrus', 'typhoon')
for item in data:
    print(item[0])
print

data = matrix('typhoon', 'malediction')
for item in data:
    print(item[0])
print

data = matrix('typhoon', 'orthrus')
for item in data:
    print(item[0])
print

data = matrix('typhoon', 'typhoon')
for item in data:
    print(item[0])

