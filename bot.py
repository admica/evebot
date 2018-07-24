#!/usr/bin/python3
#Discord eve bot by admica

import asyncio, discord, time, threading, websocket, json
from discord.ext import commands
from discord.ext.commands import Bot
import aiohttp
import re
from queue import Queue
from datetime import datetime
import os
import requests

class Zbot:
    def __init__(self):
        self.date_start = datetime.now()
        self.pause = False
        self.count = 0 # global kill counter
        self.qcounter = Queue(maxsize=1) # share counter between main and thread

        self.dir_fits = './fits/' # end with trailing slash

        self.url_characters = 'https://esi.evetech.net/latest/characters/'

        self.regions = 'Aridia Black_Rise The_Bleak_Lands Branch Cache Catch The_Citadel Cloud_Ring Cobalt_Edge Curse Deklein Delve Derelik Detorid Devoid Domain Esoteria Essence Etherium_Reach Everyshore Fade Feythabolis The_Forge Fountain Geminate Genesis Great_Wildlands Heimatar Immensea Impass Insmother Kador The_Kalevala_Expanse Khanid Kor-Azor Lonetrek Malpais Metropolis Molden_Heath Oasa Omist Outer_Passage Outer_Ring Paragon_Soul Period_Basis Perrigen_Falls Placid Providence Pure_Blind Querious Scalding_Pass Sinq_Laison Solitude The_Spire Stain Syndicate Tash-Murkon Tenal Tenerifis Tribute Vale_of_the_Silent Venal Verge Vendor Wicked_Creek'.split(' ')

        with open('systems.txt', 'r') as f:
            raw = f.read()
            self.systems = eval(raw)

        with open('stargates.txt', 'r') as f:
            raw = f.read()
            self.stargates = eval(raw)

        self.corps = []
        with open('the.corps', 'r') as f:
            for line in f.readlines():
                self.corps.append(line.strip().split(":")[-1])

        self.ch = {}
        for name in ['main', 'debug']:
            with open('the.channel_{}'.format(name), 'r') as f:
                self.ch[name] = {}
                line = f.readlines()[1].strip()
                self.ch[name]['name'] = ':'.join(line.split(":")[:-1])
                self.ch[name]['id'] = line.split(":")[-1]

        with open('the.key', 'r') as f:
            self.private_key = f.readline().strip()

        self.admins = []
        with open('the.admins', 'r') as f:
            for line in f.readlines():
                self.admins.append(line.strip())

        self.loop = asyncio.new_event_loop()
        self.Bot = commands.Bot(command_prefix='#')
        self.q = asyncio.Queue()

    def start_timer(self):
        self.thread_timer = threading.Thread(target=self.timer_thread, args=(self.q,self.ch['main']))
        self.thread_timer.daemon = True
        self.thread_timer.start()

    def start(self):
        self.thread = threading.Thread(target=self.bot_thread, args=(self.q,self.loop,self.Bot,self.ch['main'],self.admins,self.private_key,self.qcounter,self.ch))
        self.thread.daemon = True
        self.thread.start()

    def bot_thread(self, q, loop, bot, channel, admins, private_key, qcounter, ch):
        asyncio.set_event_loop(loop)
        self.q = q
        self.qthread = qcounter
        self.date_last = self.date_start
        self.last = 0
        self.flag_first_count = False

        '''@bot.event
        async def on_message(message):
            try:
                print('author:'.format(message.author))
                print('call: {}'.format(message.call))
                print('channel: {}'.format(message.channel))
                print('channel_mentions: {}'.format(message.channel_mentions))
                print('clean_content: {}'.format(message.clean_content))
                print('content: {}'.format(message.content))
                print('edited_timestamp: {}'.format(message.edited_timestamp))
                print('embeds: {}'.format(message.embeds))
                print('id: {}'.format(message.id))
                print('mention_everyone: {}'.format(message.mention_everyone))
                print('mentions: {}'.format(message.mentions))
                print('nonce: {}'.format(message.nonce))
                print('pinned: {}'.format(message.pinned))
                print('raw_channel_mentions: {}'.format(message.raw_channel_mentions))
                print('raw_mentions: {}'.format(message.raw_mentions))
                print('raw_role_mentions: {}'.format(message.raw_role_mentions))
                print('reactions: {}'.format(message.reactions))
                print('role_mentions: {}'.format(message.role_mentions))
                print('server: {}'.format(message.server))
                print('system_content: {}'.format(message.system_content))
                print('timestamp: {}'.format(message.timestamp))
                print('tts: {}'.format(message.tts))
                print('type: {}'.format(message.type))
            except:
                pass

            await bot.process_commands(message)
        '''

        @bot.event
        async def on_ready():
            try:
                await bot.change_presence(game=discord.Game(name='Connecting...'))
                while True:
                    data = await self.q.get()
                    try:
                        print("DATA")
                        print(data)
                        event = data[0]
                        message = data[1]
                        channel = data[2]
                        channel_id = bot.get_channel(channel)
                        #print('bot.send_message({}, {})'.format(channel_id, message))

                        if message.startswith('#SECRET_STARTUP____'):
                            parts = message.split('____')
                            await bot.change_presence(game=discord.Game(name=parts))
                            print("Status Updated: {}".format(parts[-1]))
                        else:
                            await bot.send_message(channel_id, message)
                        #print('bot.send_message sent.')
                    except Exception as e:
                        print('Error in q: {}'.format(e))

                    event.set()
            except Exception as e:
                print("FATAL EXCEPTION: {}".format(e))
                self.do_restart()

        '''@bot.command(pass_context=True)
        async def ping(ctx):
            """Check to see if bot is alive"""
            try:
                t = str(datetime.now()-self.date_start)[:-7]
            except:
                t = 'Unknown'
            await bot.say("<@{}> :ping_pong: Running: {}".format(ctx.message.author, t))
        '''

        @bot.command(pass_context=True)
        async def pause(ctx):
            """Stop posting killmails."""
            try:
                if not self.pause:
                    self.pause = True
                    await bot.say("<@{}> :pause_button: ***Automatic killmail posting paused.***".format(ctx.message.author))
                else:
                    await bot.say("<@{}> Already paused.".format(ctx.message.author))
            except Exception as e:
                print("FATAL in pause: {}".format(e))
                self.do_restart()


        @bot.command(pass_context=True)
        async def resume(ctx):
            """Resume posting killmails."""
            try:
                if self.pause:
                    self.pause = False
                    await bot.say("<@{}> :bacon: ***Automatic killmail posting resumed.***".format(ctx.message.author))
                else:
                    await bot.say("<@{}> Not paused.".format(ctx.message.author))
            except Exception as e:
                print("FATAL in resume: {}".format(e))
                self.do_restart()


        @bot.command(pass_context=True)
        async def active(ctx):
            """Display the most active systems over the last 3 hours.
------------------------------
1. Finds all systems in eve with kill activity.
2. Filters by security status to show only high, low, or null systems.
3. Sort into most active by ships, pods, or npc's destroyed.
You can display anywhere up to 20 systems. (default num=10, sec=low, sort=ship)
------------------------------
FORMAT: #active [number] [security status] [sort order]
------------------------------
EXAMPLE: #active 3 null pod
Total Active Systems: 961. Top 5 By Pod Kills:
UALX-3 -   40 Ships,   64 Pods,     0 NPCs
E9KD-N -   95 Ships,   48 Pods,     0 NPCs
BW-WJ2 -   49 Ships,   43 Pods,     0 NPCs
------------------------------
EXAMPLE: #active 3 low npc
Total Active Systems: 309. Top 3 By NPC Kills:
Uemon   -  619 NPCs,    0 Ships,     0 Pods (Trusec:0.1974467784)
Otosela -  252 NPCs,    0 Ships,     0 Pods (Trusec:0.2381571233)
Azedi   -  153 NPCs,    0 Ships,     0 Pods (Trusec:0.2744148374)"""
            try:
                _id = ctx.message.author
                msg = ctx.message.content
                parts = msg.split()

                num = 5
                if len(parts) > 1:
                    try:
                        num = int(parts[1])
                    except Exception as e:
                        if parts[1] in ['null', 'high', 'low']:
                            parts = [ parts[0], num, parts[1] ]

                if num > 20:
                    num = 20
                    await bot.say("<@{}> Nah, {} sounds better to me.".format(_id, num))
                elif num < 1:
                    num = 3
                    await bot.say("<@{}> Nah, {} sounds better to me.".format(_id, num))

                sec ='low'
                if len(parts) > 2:
                    try:
                        sec = str(parts[1])
                    except Exception as e:
                        print("FAILED TO PARSE SEC FOR MAX: {}".format(e))
                    sec = sec.lower()
                    if sec not in ['low','null','high']:
                        sec = 'low'

                await bot.say("<@{}> Finding top {} most active {} sec systems in last 3 hours.".format(_id, num, sec))

                url_kills = 'https://esi.evetech.net/latest/universe/system_kills/'
                url_system = 'https://esi.evetech.net/latest/universe/systems/'
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(url_kills)
                    response = await raw_response.text()
                    response = eval(response)

                    # decide what to sort by
                    typ = 'ship_kills'
                    typ_name = 'Ship'
                    if len(parts) > 2:
                        try:
                            if parts[4].lower().startswith('p'):
                                typ = 'pod_kills'
                                typ_name = 'Pod'
                            elif parts[4].lower().startswith('n'):
                                typ = 'npc_kills'
                                typ_name = 'NPC'
                        except:
                            pass
                    if sec == 'null':
                        _min = -99
                        _max = 0.0
                    elif sec == 'low':
                        _min = 0.1
                        _max = 0.4
                    else: # high
                        _min = 0.5
                        _max = 100
                    print("response starting length {}".format(len(response)))

                    if len(parts) < 1:
                        hiccup = str(parts[1]).lower()
                        if hiccup.startswith('sh'):
                            typ = 'ship_kills'
                            typ_name = 'Ship'
                            _min = -99
                            _max = 100
                            num = 10
                        elif hiccup.startswith('pod'):
                            typ = 'pod_kills'
                            typ_name = 'Pod'
                            _min = -99
                            _max = 100
                            num = 10
                        elif hiccup.startswith('npc'):
                            typ = 'npc_kills'
                            typ_name = 'NPC'
                            _min = -99
                            _max = 100
                            num = 10
                        else:
                            pass

                    for i in range(len(response)):
                        print(self.systems[int(response[i]['system_id'])]['security_status'])
 

                    droplist = []
                    for i in range(len(response)):
                        #print('---')
                        #print(response[i])
                        #print(int(response[i]['system_id']))
                        #print(self.systems[int(response[i]['system_id'])])
                        #print(self.systems[int(response[i]['system_id'])]['security_status'])
                        trusec = self.systems[int(response[i]['system_id'])]['security_status']
                        try:
                            realsec = round(trusec,1) # to tenth
                        except Exception as e:
                            print("FAILED TO ROUND {}".format(trusec))
                        if realsec > _max or realsec < _min:
                            droplist.append(i)
                    print("droplist length {}".format(len(droplist)))

                    offset = 0
                    for i in droplist:
                        #print("Dropping {}".format(response[i-offset]))
                        del response[i-offset]
                        offset += 1
                    print("response length now {}".format(len(response)))

                    top = [i for i in response if self.systems[int(i['system_id'])]['security_status'] < _max and self.systems[int(i['system_id'])]['security_status'] > _min]
                    top = sorted(top, key=lambda k: k[typ])

                    kill_total = len(top)
                    top = top[num:] # truncate
                    top.reverse() # descending
                    data = '```Total Active Systems: {}. Top {} By {} Kills:\n'.format(kill_total, num, typ_name)

                    maxsize = 4 # find width needed for name column, why bother starting any less
                    for d in top:
                        namesize = len(self.systems[int(d['system_id'])]['name'])
                        if namesize > maxsize:
                            maxsize = namesize
                    maxsize += 1

                    for d in top:

                        #ship,pod,npc
                        #pod,ship,npc
                        #npc,ship,pod

                        print(d)
                        name = self.systems[(d['system_id'])]['name']
                        data += name
                        data += ' ' * abs(maxsize-len(name))

                        if typ == 'ship_kills':
                           data += '- {:4d} Ships, {:4d} Pods, {:5d} NPCs'.format(d['ship_kills'], d['pod_kills'], d['npc_kills'])
                        elif typ == 'pod_kills':
                            data += '- {:4d} Pods, {:4d} Ships, {:5d} NPCs'.format(d['pod_kills'], d['ship_kills'], d['npc_kills'])
                        else:
                            trusec = self.systems[int(d['system_id'])]['security_status']
                            data += '- {:4d} NPCs, {:4d} Ships, {:5d} Pods (Trusec:{})'.format(d['npc_kills'], d['ship_kills'], d['pod_kills'], trusec)

                        num -= 1
                        if num < 1:
                            break
                        data += '\n'
                    data += '```'
                    await bot.say('<@{}> {}'.format(_id, data))
                    print(data)
                    time.sleep(0.05)
 
            except Exception as e:
                print("FATAL in activity: {}".format(e))
                self.do_restart()


        @bot.command(pass_context=True)
        async def sys(ctx):
            """Get info about a specific system
------------------------------
FORMAT: #sys <name>
------------------------------
EXAMPLE: #sys bwf
[ Ships/Pods/NPCs ] http://evemaps.dotlan.net/system/BWF-ZZ
Name: BWF-ZZ [ 25/9/0 ]
Security Status: -0.6 (Trusec: -0.5754449964)
Planets: 10
Gates: 4
Stargate to IOO-7O (Sec:-0.5) [ 0/0/249 ]
Stargate to 8MG-J6 (Sec:-0.6) [ 2/2/32 ]
Stargate to RLSI-V (Sec:-0.5) [ 0/0/199 ]
Stargate to Oijanen (Sec:0.4) [ 7/4/63 ]"""
            _id = ctx.message.author
            msg = ctx.message.content
            parts = msg.split()

            if len(parts) == 2:
                sys = parts[-1].lower()
                print(sys)
            else:
                return

            matches = {}
            count = 0
            for system_id, d in self.systems.items():
                if sys == d['name'].lower():
                    count += 1
                    matches[system_id] = d

            if count == 1:
                print("FOUND EXACT MATCH")
                data = ''
                for system_id, d in matches.items(): # one match
                    url_kills = 'https://esi.evetech.net/latest/universe/system_kills/'
                    async with aiohttp.ClientSession() as session:
                        raw_response = await session.get(url_kills)
                        response = await raw_response.text()
                        response = eval(response)
                        _s,_p,_n = ('Unknown','Unknown','Unknown')
                        for dd in response:
                            if dd['system_id'] == system_id:
                                _s = dd['ship_kills']
                                _p = dd['pod_kills']
                                _n = dd['npc_kills']
                                break
                    data = '[ Ships/Pods/NPCs ] <http://evemaps.dotlan.net/system/{}>```'.format(d['name'].strip())
                    data += 'Name: {} [ {}/{}/{} ]\n'.format(d['name'], _s, _p, _n)

                    if d.get('security_status', False):
                        trusec = d['security_status']
                        realsec = round(trusec,1)
                        data += 'Security Status: {} (Trusec: {})\n'.format(realsec, trusec)

                    if d.get('planets', False):
                        num_planets = len(d['planets'])
                        num_belts,num_moons = (0,0)
                        for p in d['planets']:
                            if p.get('asteroid_belts', False):
                                num_belts += 1
                            elif p.get('moons', False):
                                num_moons += 1
                        data += 'Planets: {}, Belts: {}, Moons: {}\n'.format(num_planets, num_belts, num_moons)

                    if d.get('stargates', False):
                        gates = []
                        data += 'Gates: {}\n'.format(len(d['stargates']))
                        for gate in d['stargates']:
                            #print("Gate id: {}\n".format(gate))
                            stargate_id = self.stargates.get(gate, False)
                            if stargate_id:
                                dest = self.stargates[gate].get('destination', False)
                                #print("Dest: {}\n".format(dest))
                                if dest:
                                    sys_id = dest['system_id']
                                    name = self.systems[sys_id].get('name', False)
                                    stat = self.systems[sys_id].get('security_status', False)
                                    if name is not False and stat is not False:
                                        _s,_p,_n = ('Unknown','Unknown','Unknown')
                                        for dd in response:
                                             if dd['system_id'] == sys_id:
                                                _s = dd['ship_kills']
                                                _p = dd['pod_kills']
                                                _n = dd['npc_kills']
                                                break

                                        line = "Stargate to {} (Sec:{}) [ {}/{}/{} ]\n".format(name, round(stat,1), _s, _p, _n)
                                        data += line
                    data += '```'
                await bot.say('<@{}> {}'.format(_id, data))

            elif count > 20:
                await bot.say("<@{}> {} systems match that criteria, please be more specific.".format(_id, count))

            elif count == 0:
                print("NO EXACT MATCH FOUND, SEARCHING FOR REGEX MATCH")
                c = 0
                for system_id, d in self.systems.items():
                    if d['name'].lower().startswith(sys):
                        c += 1
                        matches[system_id] = d

                if c == 1:
                    for system_id, d in matches.items(): # one match

                        url_kills = 'https://esi.evetech.net/latest/universe/system_kills/'
                        async with aiohttp.ClientSession() as session:
                            raw_response = await session.get(url_kills)
                            response = await raw_response.text()
                            response = eval(response)
                            _s,_p,_n = ('Unknown','Unknown','Unknown')
                            for dd in response:
                                if dd['system_id'] == system_id:
                                    _s = dd['ship_kills']
                                    _p = dd['pod_kills']
                                    _n = dd['npc_kills']
                                    break

                        data = '[ Ships/Pods/NPCs ] <http://evemaps.dotlan.net/system/{}>```'.format(d['name'].strip())
                        data += 'Name: {} [ {}/{}/{} ]\n'.format(d['name'], _s, _p, _n)

                        if d.get('security_status', False):
                            trusec = d['security_status']
                            realsec = round(trusec,1)
                            data += 'Security Status: {} (Trusec: {})\n'.format(realsec, trusec)

                        if d.get('planets', False):
                            num_planets = len(d['planets'])
                            num_belts,num_moons = (0,0)
                            for p in d['planets']:
                                if p.get('asteroid_belts', False):
                                    num_belts += 1
                                elif p.get('moons', False):
                                    num_moons += 1
                            data += 'Planets: {}, Belts: {}, Moons: {}\n'.format(num_planets, num_belts, num_moons)

                        if d.get('stargates', False):
                            gates = []
                            data += 'Gates: {}\n'.format(len(d['stargates']))
                            for gate in d['stargates']:
                                #print("Gate id: {}\n".format(gate))
                                stargate_id = self.stargates.get(gate, False)
                                if stargate_id:
                                    dest = self.stargates[gate].get('destination', False)
                                    #print("Dest: {}\n".format(dest))
                                    if dest:
                                        sys_id = dest['system_id']
                                        name = self.systems[sys_id].get('name', False)
                                        stat = self.systems[sys_id].get('security_status', False)
                                        if name is not False and stat is not False:
                                            _s,_p,_n = ('Unknown','Unknown','Unknown')
                                            for dd in response:
                                                 if dd['system_id'] == sys_id:
                                                    _s = dd['ship_kills']
                                                    _p = dd['pod_kills']
                                                    _n = dd['npc_kills']
                                                    break

                                            line = "Stargate to {} (Sec:{}) [ {}/{}/{} ]\n".format(name, round(stat,1), _s, _p, _n)
                                            data += line
                        data += '```'
                    await bot.say('<@{}> {}'.format(_id, data))

                elif c > 25:
                    await bot.say("<@{}> {} systems match that criteria, please be more specific.".format(_id, c))

                elif c > 1:
                    multi = []
                    for k,d in matches.items():
                        multi.append(d['name'])
                    multi = ', '.join(multi)
                    print(multi)
                    await bot.say("<@{}> Multiple matches: {}. Please be more specific.".format(_id, multi))

                else:
                    await bot.say('<@{}> No systems found matching "{}"'.format(_id, parts[-1]))

            elif count > 1:
                await bot.say("<@{}> That's strange, multiple matches given a complete system name?!".format(_id))


        @bot.command(pass_context=True)
        async def save(ctx):
            """Save EFT ship fittings.
------------------------------
Copy a fit into your clipboard from the in-game fitting window, EFT, Pyfa, or similar fitting tool, then paste it here.
------------------------------
FORMAT: #save <name> <EFT-Fit>
------------------------------
EXAMPLE: #save FrigKiller [Caracal, Caracal fit]
Ballistic Control System II
Ballistic Control System II
Nanofiber Internal Structure II
Nanofiber Internal Structure II

50MN Cold-Gas Enduring Microwarpdrive
Warp Disruptor II
Stasis Webifier II
Large Shield Extender II
Large Shield Extender II

Rapid Light Missile Launcher II, Caldari Navy Inferno Light Missile
Rapid Light Missile Launcher II, Caldari Navy Inferno Light Missile
Rapid Light Missile Launcher II, Caldari Navy Inferno Light Missile
Rapid Light Missile Launcher II, Caldari Navy Inferno Light Missile
Rapid Light Missile Launcher II, Caldari Navy Inferno Light Missile

Medium Anti-EM Screen Reinforcer I
Medium Core Defense Field Extender I
Medium Core Defense Field Extender I

Warrior II x5
            """
            try:
                _id = ctx.message.author
                msg = ctx.message.content
                msg = msg[6:]
                parts = msg.split()
                #print(msg)

                register = ''
                found_start = False
                found_end = False
                count = 0
                count_ch = 6
                fit_start = 0
                for part in parts:
                    count += 1
                    count_ch += len(part)
                    if part.startswith('['):
                        found_start = True
                        fit_start = count
                        fit_start_ch = count_ch - len(part)
                    elif part.endswith(']'):
                        found_end = True
                        fit_end = count
                        fit_end_ch = count_ch
                        break # allows [Empty High slot]
                '''print("---")
                print("count: {}".format(count))
                print("count_ch: {}".format(count_ch))
                print("fit_start: {}".format(fit_start))
                print("fit_end:   {}".format(fit_end))
                print("fit_start_ch: {}".format(fit_start_ch))
                print("fit_end_ch:   {}".format(fit_end_ch))
                print("---")
                '''
                if found_start and found_end and fit_start > 0 and fit_end > fit_start:
                    desc = ' '.join(parts[fit_start-1:fit_end])
                    #print(desc)

                    group = str(desc.split(',')[0])
                    group = group[1:].replace(' ','_')

                    name = ' '.join(parts[:fit_start-1])
                    filename = self.fix_filename(name)
                    #print(filename)

                    if not len(filename):
                        await bot.say("<@{}> Try saving with a different name.".format(_id))
                        return

                    await bot.say("<@{}> Saving {} as {}".format(_id, desc, name))

                    found_group = False
                    try:
                        for root, dirs, files in os.walk(self.dir_fits):
                            for d in dirs:
                                if group == d:
                                    found_group = True
                    except:
                        print("FAILURE IN WALKING DIRS FOR FITS")

                    fullpath = "{}{}".format(self.dir_fits, group)
                    #print(fullpath)
                    if not found_group:
                        if not os.path.exists(fullpath):
                            os.mkdir(fullpath)
                        else:
                            print("ERROR CREATING DIRECTORY FOR GROUP {}".format(group))

                    ship = ''
                    for part in parts[fit_end:]:
                        ship = '{} {}'.format(ship, part)
                    ship = ship[:-1]
                    if len(ship) > 0:
                        fullpath = '{}{}/{}'.format(self.dir_fits, group, filename)
                        with open(fullpath,'w') as f:
                            f.write(msg)
                            await bot.say('<@{}> Saved {}'.format(_id, fullpath[1:]))
                            print(msg)

            except Exception as e:
                print("ERROR in save: {}".format(e))
                try:
                    await bot.say("<@{}> Failed to save.".format(_id))
                except Exception as e:
                    print("FATAL in pause: {}".format(e))
                    self.do_restart()


        @bot.command(pass_context=True)
        async def show(ctx):
            """Show saved ship types or fits for a specified ship
------------------------------
DESCRIPTIONL Show all ships that have saved fits.
FORMAT: #show
EXAMPLE: #show
  Loadable ship types:
  Arbitrator, Daredevil, Drake, Hurricane, Scythe_Fleet_Issue, Stiletto, Zealot
------------------------------
DESCRIPTION: Show all fits for a specific ship. (you only have to specify a letter or two)
FORMAT: #show <ship>
EXAMPLE: #show dra
  bait_drake
  lights_drake_fleet
  heavy_fleet_drake
------------------------------
DESCRIPTION: Show a specific fit for a specific ship.
FORMAT: #show <ship> <fit name>
EXAMPLE: #show drake lights_drake_fle
  Damage Control II
  Nanofiber Internal Structure II
  <the rest of the lights_drake_fleet fit here>
            """
            _id = ctx.message.author
            msg = ctx.message.content
            parts = msg.split()
            cmd = parts[0]

            if len(parts) == 1:
                data = []
                for root, dirs, files in os.walk(self.dir_fits):
                    for d in dirs:
                        data.append(d)
                if len(data):
                    data.sort()
                    await bot.say("<@{}> Loadable ship types:\n{}".format(_id, ', '.join(data)))
                return

            if len(parts) > 1:
                raw_group = self.fix_filename(parts[1])
                group = ''
                for word in raw_group.split('_'):
                    group += '{}_'.format(word.capitalize())
                group = group[:-1]

            if len(parts) > 1:
                data = ''
                fullpath = '{}{}'.format(self.dir_fits, group)
                for root, dirs, files in os.walk(fullpath):
                    for filename in files:
                        data = "{}\n{}".format(data, filename)
                data = data[1:]
                if len(data) and len(parts) == 2:
                    await bot.say("<@{}> Loadable {} fits:\n{}".format(_id, group, data))
                    return
                elif len(data) and len(parts) == 3:
                    print("LOADED GROUP, NOW ONTO FITS")
                else:
                    found = False
                    raw_group = raw_group.lower()
                    for root, dirs, files in os.walk(self.dir_fits):
                        for d in dirs:
                            if raw_group == d.lower():
                                group = d
                                found = True
                                break
                            elif d.lower().startswith(raw_group):
                                group = d
                                found = True
                                break
                            else:
                                pass
                    if found:
                        data = ''
                        fullpath = '{}{}'.format(self.dir_fits, group)
                        for root, dirs, files in os.walk(fullpath):
                            for filename in files:
                                data = "{}\n{}".format(data, filename)
                        data = data[1:]
                        if len(data) and len(parts) == 2:
                            await bot.say("<@{}> Loadable {} fits:\n{}".format(_id, group, data))
                            return
                        elif len(data) and len(parts) == 3:
                            #print("FIXED AND LOADED GROUP, NOW ONTO FITS")
                            pass

                    else:
                        await bot.say("<@{}> No {} fits found.".format(_id, group))
                        return

            if len(parts) == 3:
                filename = self.fix_filename(parts[2])
                if not len(filename):
                    return

                fullpath = '{}{}/{}'.format(self.dir_fits, group, filename)
                if os.path.isfile(fullpath):
                    with open(fullpath,'r') as f:
                            data = f.read(4096)
                            await bot.say("<@{}> {}{}/{}".format(_id, self.dir_fits[1:], group, data))
                else:
                    found = False
                    raw_filename = filename.lower()
                    for root, dirs, files in os.walk(self.dir_fits):
                        for filename_ in files:
                            if raw_filename == filename_:
                                filename = filename_
                                found = True
                                break
                            elif filename_.lower().startswith(raw_filename):
                                filename = filename_
                                found = True
                                break
                            else:
                                pass
                    if found:
                        fullpath = '{}{}/{}'.format(self.dir_fits, group, filename)
                        with open(fullpath,'r') as f:
                            data = f.read(4096)
                            await bot.say("<@{}> {}{}/{}".format(_id, self.dir_fits[1:], group, data))
                    else:
                        await bot.say("<@{}> Can't find that {} fit, try again.".format(_id, group))
                return

            await bot.say("<@{}> I'm sorry Dave, I can't allow you to do that.".format(_id))

        @bot.command(pass_context=True)
        async def count(ctx):
            """Show how many killmails seen since last restart and last asked."""
            try:
                _id = ctx.message.author
                x = []
                while not self.qthread.empty():
                    x.append(self.qthread.get_nowait())
                if not len(x):
                    x = [self.last]
                x = x[-1]
                print(x)
                await bot.say("<@{}> {} kills since last restart at {}".format(_id, x, str(self.date_start)[:-7]))

                print("last: {}".format(self.last))
                now = datetime.now()
                dt = str(now - self.dt_last)[:-7]
                self.dt_last = datetime.now()

                diff = x - self.last
                if not self.flag_first_count:
                    await bot.say("<@{}> {} kills since last asked {} ago.".format(_id, diff, dt))
                else:
                    self.flag_first_count = False

                if self.last < 0:
                    self.last = 0
                else:
                    self.last = x

            except Exception as e:
                try:
                    print("Error in count: {}".format(e))
                    await bot.say("<@{}> Error in count.".format(_id))

                except Exception as e:
                    print("FATAL in count: {}".format(e))
                    self.do_restart()


        @bot.command(pass_context=True)
        async def map(ctx):
            """Fetch a dotlan map for any region, example: #map forge"""
            _id = ctx.message.author
            #http://evemaps.dotlan.net/map/Tribute/M-OEE8#jumps
            url = 'http://evemaps.dotlan.net/map/'
            try:
                name = ctx.message.content
                name = name.split()
                if len(name) > 2:
                    name = name[1:]
                    name = '_'.join(name)
                else:
                    name = name[1]
                print('Processing map request for {}'.format(name))

                found = False
                for region in self.regions:
                    if name == region.lower():
                        found = True
                        print('Exact match found! {}'.format(name))
                        break

                if not found:
                    print("No exact match found, checking nicknames.")
                    found = True
                    if name in ['bleak','lands','land']:
                        name = 'the_bleak_lands'
                    elif name == 'citadel':
                        name = 'the_citadel'
                    elif name in ['cloud','ring']:
                        name = 'cloud_ring'
                    elif name in ['cobalt','edge']:
                        name = 'cobalt_edge'
                    elif name in ['eth','ether','etherium','ethereum','reach']:
                        name = 'etherium_reach'
                    elif name in ['every','shore']:
                        name = 'everyshore'
                    elif name in ['fey','feyth','faith']:
                        name = 'feythabolis'
                    elif name == 'forge':
                        name = 'the_forge'
                    elif name in ['great','wildlands','wild','wildland']:
                        name = 'great_wildlands'
                    elif name in ['kal','kalev','kalevala','expanse']:
                        name = 'the_kalevala_expanse'
                    elif name == 'azor':
                        name = 'kor-azor'
                    elif name == 'trek':
                        name = 'lonetrek'
                    elif name == 'heath':
                        name = 'molden_heath'
                    elif name == 'passage':
                        name = 'outer_passage'
                    elif name == 'ring':
                        name = 'outer_ring'
                    elif name == 'soul':
                        name = 'paragon_soul'
                    elif name == 'basis':
                        name = 'period_basis'
                    elif name in ['falls','fall']:
                        name = 'perrigen_falls'
                    elif name == 'blind':
                        name = 'pure_blind'
                    elif name == 'pass':
                        name = 'scalding_pass'
                    elif name in ['laison','liason','sink']:
                        name = 'sinq_laison'
                    elif name in ['spire','spires']:
                        name = 'the_spire'
                    elif name in ['syn','sin']:
                        name = 'syndicate'
                    elif name in ['murkon','murk']:
                        name = 'tash-murkon'
                    elif name in ['vale','of','silent']:
                        name = 'vale_of_the_silent'
                    elif name == 'creek':
                        name = 'wicked_creek'
                    else:
                        print("No nickname match found.")
                        found = False
                    if not found:
                        for region in self.regions:
                            print("checking {} = {}".format(name,region.lower()))
                            if region.lower().startswith(name):
                                name = region
                                found = True
                                break
                if found:
                    url = '<{}{}#jumps>'.format(url, name)
                    print('Sending link: {}'.format(url))
                    await bot.say(url)

            except Exception as e:
                print("Map failure: {}".format(e))
                try:
                    await bot.say("<@{}> Hmm, something went wrong.".format(_id))
                except Exception as e:
                    self.do_restart()


        @bot.command(pass_context=True)
        async def status(ctx):
            """Get some statistics."""
            try:
                _id = ctx.message.author
                await bot.say("<@{}> Killmails post to channel: {} id: {}".format(_id, self.ch['main']['name'], self.ch['main']['id']))

                corps = []
                count = 0
                with open('the.corps','r') as f:
                    for line in f.readlines():
                        corps.append(line.strip().split(":")[0])
                        count += 1
                corps = ', '.join(corps)
                await bot.say("<@{}> Watching kills/losses for {} corps: {}".format(_id, count, corps))

                if self.pause:
                    await bot.say("<@{}> Currently paused. :pause_button:>".format(_id))
                else:
                    await bot.say("<@{}> Actively posting killmails. :bacon:".format(_id))

                try:
                    start = str(self.date_start)[:-7]
                except:
                    start = 'Unknown'
                try:
                    t = str(datetime.now()-self.date_start)[:-7]
                except:
                    t = 'Unknown'
                await bot.say("<@{}> Running: {} (Started {})".format(_id, t, start))

            except Exception as e:
                print("ERROR in status: {}".format(e))
                try: 
                    await bot.say("<@{}> Error in status.".format(_id))
                except Exception as e:
                    self.do_restart()
               

        @bot.command(pass_context=True)
        async def price(ctx):
            """crypto price check, example: #price bitcoin, #price iota"""
            _id = ctx.message.author
            msg = ctx.message.content
            coin = msg.split()[1]
            url = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(coin)
            try:
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(url)
                    response = await raw_response.text()
                    response = eval(response)[0]
                    await bot.say("<@{}> {} price: ${}".format(_id, coin.upper(), response['price_usd']))
                    await bot.say("<@{}> {} % change last 1h:  {}%".format(_id, coin.upper(), response['percent_change_1h']))
                    await bot.say("<@{}> {} % change last 24h: {}%".format(_id, coin.upper(), response['percent_change_24h']))
                    await bot.say("<@{}> {} volume last 24h: ${}".format(_id, coin.upper(), response['24h_volume_usd']))
            except Exception as e:
                print("<@{}> Error in price command: {}".format(_id, e))
                await bot.say("<@{}> Sorry, I don't know how to lookup {}.".format(_id, coin))

        @bot.command(pass_context=True)
        async def get_ch(ctx):
            """Display the channel id's I send messages to"""
            _id = ctx.message.author
            for key in self.ch:
                await bot.say("<@{}> {}: [{}] id: {}".format(_id, key, self.ch[key]['name'], self.ch[key]['id']))

        @bot.command(pass_context=True)
        async def set_ch(ctx):
            """Set the channel id's I send messages to"""
            try:
                if str(ctx.message.author) in admins:
                    msg = ctx.message.content.split()
                    if len(msg) == 4:
                        key, name, channel_id = msg[1:]
                        if key in self.ch:
                            try:
                                with open('the.channel_{}'.format(key),'w') as f:
                                    f.write("{}:{}\n".format(name, channel_id))
                                    self.ch[key]['name'] = name
                                    self.ch[key]['id'] = channel_id
                                    await bot.say("<@{}> {} output channel set to {} id: {}".format(_id, key, name, channel_id))
                            except Exception as e:
                                await bot.say("<@{}> Failed to set {} output channel.".format(_id, key))
                        else:
                            await bot.say("<@{}> {} is an invalid key.".format(_id, key))
                    else:
                        await bot.say("<@{}> Usage: {} <key> <name> <channel_id>".format(_id, msg[0]))
            except Exception as e:
                print("ERROR in set_channel: {}".format(e))

        @bot.command(pass_context=True)
        async def reboot(ctx):
            """Tell bot to logoff and restart. (permissions required)"""
            if str(ctx.message.author) in admins:
                try:
                    await bot.say("Rebooting, please wait.")
                except:
                    pass
                try:
                    await bot.logout()
                except:
                    pass
                self.running = False
                self.do_restart()

        @bot.command(pass_context=True)
        async def die(ctx):
            """Tell bot to logoff. (permissions required)"""
            _id = ctx.message.author
            if str(ctx.message.author) in admins:
                await bot.say("<@{}> Shutting down.".format(_id))
                await bot.logout()
                self.running = False
                import sys
                sys.exit(0)
            else:
                await bot.say("<@{}> You are not an admin, ignoring command.".format(_id))

        try:
            bot.run(private_key)
        except Exception as e:
            print("FATAL in bot.run(): {}".format(e))
            self.do_restart()


    def send(self, channel, message):
        event = threading.Event()
        try:
            channel = channel['id']
        except:
            pass        
        try:
            self.q.put_nowait([event, message, channel])
            event.wait()
        except Exception as e:
            print("FATAL in send: {}".format(e))
            self.do_restart()


    def run(self, debug=False):
        """main loop runs forever"""
        if debug:
            channel = self.ch['debug']
        else:
            channel = self.ch['main']

        while True:
            try:
                _url = 'wss://zkillboard.com:2096'
                _msg = '{"action":"sbu","channel":"killstream"}'
                ws = websocket.create_connection(_url)
                print('Main Connected to: {}'.format(_url))
                ws.send(_msg)
                print('Main Subscribed with: {}'.format(_msg))

                self.running = True
                while self.running:
                    time.sleep(0.1)
                    if self.Bot._is_ready.is_set():

                        while True:
                            try:
                                time.sleep(0.1)
                                raw = ws.recv()
                                d = json.dumps(raw)
                                url = d['zkb']['url']

                                subj = '---'
                                post = False
                                for attacker in d['attackers']:
                                    c = attacker.get('corporation_id','none')
                                    if str(c) in self.corps:
                                        subj = 'Win'
                                        post = True
                                        break

                                if not post:
                                    c = d['victim'].get('corporation_id', 'none')
                                    if str(c) not in self.corps:
                                        subj = 'Lose'
                                        post = True

                                self.count += 1
                                self.incr() # handle counter queue

                                msg = '`{}` {}'.format(subj, url)
                                if self.pause:
                                    if post:
                                        print('Sending: {}'.format(msg))
                                        send(channel, msg)
                                        time.sleep(0.01)
                                    else:
                                        print('{} is not interesting'.format(msg))
                                        time.sleep(0.01)
                                else:
                                    print("Paused, ignoring {}".format(msg))

                            except Exception as e:
                                print('Exception caught: {}'.format(e))
                                time.sleep(1)
                                self.do_restart()

            except KeyboardInterrupt:
                self.running = False

            except Exception as e:
                print("Unknown Error {}".format(e))

            x = 60
            print('Sleeping {} seconds...'.format(x))
            time.sleep(x)
            print('Restarting...')
            self.do_restart()

    def get_char(self, character_id):
        """lookup character info from ESI"""
        try:
            r = requests('{}'.format(character_id))
            d = eval(r)
            return len(d)

        except Exception as e:
            print("ERROR IN GET_CHAR: {}".format(e))
            return False

    def fix_filename(self, filename):
        """replace or remove suspect characters"""
        filename = str(filename).strip()
        filename = filename.replace(' ','_')
        filename = filename.replace('-','_')
        filename = filename.replace('/','_')
        filename = filename.replace('\\','_')
        filename = filename.replace('"','_')
        filaname = filename.replace("'",'_')
        filename = filename.replace('[','_')
        filename = filename.replace(']','_')
        filename = filename.replace('(','_')
        filename = filename.replace(')','_')
        filename = filename.replace('{','_')
        filename = filename.replace('}','_')
        filename = filename.replace('\`','_')
        while filename.startswith('.'):
            filename = filename[1:]
        while filename.startswith('\`'):
            filename = filename[1:]
        return filename


    def incr(self):
        """queue the details from the last mails"""
        try:
            if self.qcounter.full():
                junk = self.qcounter.get()
            self.qcounter.put(self.count[-1])

        except Exception as e:
            print("FATAL in incr: {}".format(e))
            self.do_restart()


    def timer_thread(self, q, chan, debug=False):
        """thread loop runs forever updating status"""
        channel = chan['id']
        self.running = True
        self.message = 'Calculating...'

        while True:
            try:
                status = 'Unknown'
                online = 'Unknown'
                kills = 'Unknown'
                ready = False

                _url = 'wss://zkillboard.com:2096'
                _msg = '{"action":"sbu","channel":"public"}'
                wss = websocket.create_connection(_url)
                print('Timer Thread Connected to: {}'.format(_url))
                wss.send(_msg)
                print('Timer Thread Subscribed with: {}'.format(_msg))

                while self.running:
                    time.sleep(0.1)
                    raw = wss()
                    d = eval(raw)
                    if 'tqStatus' in d:
                        status = d['tqStatus']
                        online = d['tqCount']
                        kills = d['kills']
                        ready = True

                    if ready:
                        event = threading.Event()
                        self.message = '#SECRET_STATUP____{} {} {} Kills'.format(online, status, kills)
                        q.put_nowait([event, self.message, channel])
                        event.wait()

                        wss.close()
                        raise ZeroDivisionError

                    else:
                        print("Collecting data {} {} {}".format(status, online, kills))
            except Exception as e:
                print("SLEEPING AFTER TIMER_THREAD {}".format(e))
                time.sleep(600)


    def do_restart(self):
        try:
            self.running = False
            import os,sys
            sys.exit(0)
            os.execv(__file__, sys.argv)
        except Exception as e:
            print("Failing to restart")
            time.sleep(15)

if __name__ == '__main__':

    import time
    time.sleep(1)

    bot = Zbot()
    try:
        bot.start()
        bot.start_timer()
        bot.run()
    except Exception as e:
        print("FATAILITY IN MAIN: {}".format(e))
        bot.do_restart()

