#!/home/admica/python3/bin/python3
#Discord eve bot by admica

import asyncio, discord, time, threading, websocket, json
from discord.ext import commands
from discord.ext.commands import Bot
import aiohttp
import re
from queue import Queue
from datetime import timedelta
from datetime import datetime
import os, sys
import requests
from chatterbot import ChatBot
from ctypes.util import find_library
from random import randint
import pickle
from tensorflow.python.keras.layers import Dense, Reshape, Flatten, Dropout, Input, concatenate
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, Activation
from keras.layers import Input, Embedding, LSTM, Dense, RepeatVector, Dropout, merge,concatenate
from keras.optimizers import Adam 
from keras.models import Model, Sequential
from keras.layers import Activation, Dense
from keras.preprocessing import sequence
from six.moves import input
import numpy as np

REDO = 'redo'
VOCAB = '/usr/share/dict/cracklib-small'
NUMBERWORD = {1: 'Thousand', 2: 'Million', 3: 'Billion', 4: 'Trillion', 0: 'Hundred', 5: 'Quadrillion', 6: 'Quintillion', 7: 'Sextillion', 8: 'Septillion', 9: 'Octillion'}

def distance(p1, p2):
    deltaxsq = (p1['x'] - p2['x']) ** 2
    deltaysq = (p1['y'] - p2['y']) ** 2
    deltazsq = (p1['z'] - p2['z']) ** 2
    return (deltaxsq + deltaysq + deltazsq) ** 0.5

def shorten_weapon(s):
    s = re.sub('Light Missile','LM', s)
    s = re.sub('Heavy Missile','HM', s)
    s = re.sub('Republic Fleet','RF', s)
    s = re.sub('Heavy Assault Missile','HAM', s)
    s = re.sub('Autocannon','AC', s)
    s = re.sub('AutoCannon','AC', s)
    s = re.sub('Carbonized Lead', 'Lead', s)
    s = re.sub('Depleted Uranium', 'Uranium', s)
    s = re.sub('Missile Launcher', 'ML', s)
    s = re.sub('Federation Navy', 'Fed Navy', s)
    s = re.sub('Imperial Navy', 'Imp Navy', s)
    s = re.sub('Howitzer Artillery', 'Arty', s)
    s = re.sub('Neutralizer', 'Neut', s)
    s = re.sub('Scrambler', 'Scram', s)
    s = re.sub('Hobgoblin', 'Hobgob', s)
    return s

def shorten_ship(s):
    s = re.sub('Federation Navy', 'Fed Navy', s)
    s = re.sub('Megathron', 'Megatron', s)
    s = re.sub('Thrasher', 'Trasher', s)
    s = re.sub('Scorpion', 'Scorp', s)
    s = re.sub('Apocalypse', 'Apoc', s)
    return s

class Zbot:
    def __init__(self):
        self.date_start = datetime.now()
        self.count = 0 # global kill counter
        self.qcounter = Queue(maxsize=1) # share counter between main and thread

        self.cb_qin = Queue(maxsize=512) # share chatbot from thread to thread
        self.cb_qout = Queue(maxsize=512)
        cb_qthread = threading.Thread(target=self.cb_thread, args=(self.cb_qin, self.cb_qout))
        cb_qthread.start() # chatbot

        self.dir_fits = './fits/' # end with trailing slash
        self.url_characters = 'https://esi.evetech.net/latest/characters/'

        self.stations = []
        t = threading.Thread(target=self.t_stations)
        t.start()

        self.regionslist = 'Aridia Black_Rise The_Bleak_Lands Branch Cache Catch The_Citadel Cloud_Ring Cobalt_Edge Curse Deklein Delve Derelik Detorid Devoid Domain Esoteria Essence Etherium_Reach Everyshore Fade Feythabolis The_Forge Fountain Geminate Genesis Great_Wildlands Heimatar Immensea Impass Insmother Kador The_Kalevala_Expanse Khanid Kor-Azor Lonetrek Malpais Metropolis Molden_Heath Oasa Omist Outer_Passage Outer_Ring Paragon_Soul Period_Basis Perrigen_Falls Placid Providence Pure_Blind Querious Scalding_Pass Sinq_Laison Solitude The_Spire Stain Syndicate Tash-Murkon Tenal Tenerifis Tribute Vale_of_the_Silent Venal Verge Vendor Wicked_Creek'.split(' ')

        with open('regions.txt', 'r') as f:
            raw = f.read()
            self.regions = eval(raw)

        with open('items.txt', 'r') as f:
            raw = f.read()
            self.items = eval(raw)
            #self.items_display = self.items.copy()
            #for i in _items:
            #    self.items_display[i] = shorten_weapon(self.items[i])
            #    self.items_display[i] = shorten_ship(self.items[i])

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
                line = f.readline().strip()
                self.ch[name]['name'] = ':'.join(line.split(":")[:-1])
                self.ch[name]['id'] = line.split(":")[-1]

        self.ch_train = {}
        with open('the.channel_train', 'r') as f:
            for line in f.readlines():
                line = line.strip()
                name = ':'.join(line.split(":")[:-1])
                ch_id = line.split(":")[-1]
                self.ch_train[ch_id] = {}
                self.ch_train[ch_id]['id'] = ch_id
                self.ch_train[ch_id]['name'] = name
                self.ch_train[ch_id]['in'] = Queue(maxsize=256)
                self.ch_train[ch_id]['out'] = Queue(maxsize=256)
                self.ch_train[ch_id]['pair'] = []
        print(self.ch_train)

        self.son = False
        self.svol = 0.75
        with open('the.sound_on', 'r') as f:
            try:
                volume = float(f.readline().strip())
                if volume > 0:
                    self.son = True
                    self.svol = volume
            except Exception as e:
                print("problem loading sound volume from file")
                print(e)

        self.join_voice = None
        with open('the.channel_voice', 'r') as f:
            line = f.readline().strip()
            if line == 'off': # allow turning off
                print("NOT JOINING VOICE CHANNEL")
            else:
                self.join_voice = line.split(":")[-1]
        self.join_voice = None # DISABLE VOICE CHANNEL JOINING WITH THIS

        with open('the.key', 'r') as f:
            self.private_key = f.readline().strip()

        self.admins = []
        with open('the.admins', 'r') as f:
            for line in f.readlines():
                self.admins.append(line.strip())

        self.loop = asyncio.new_event_loop()
        self.Bot = commands.Bot(command_prefix='#')
        self.q = asyncio.Queue()
        print("Startup complete.")


    def t_stations(self):
        """loading station data can take time, so its threaded here as a background loading task"""
        import yaml
        self.stations = yaml.load( open('staStations.yaml','r') )
        return False       

    def start_timer(self):
        self.thread_timer = threading.Thread(target=self.timer_thread, args=(self.q,self.ch['main1']))
        self.thread_timer.daemon = True
        self.thread_timer.start()

    def start(self):
        self.thread = threading.Thread(target=self.bot_thread, args=(self.bot_id,self.q,self.loop,self.Bot,self.ch['main1'],self.admins,self.private_key,self.qcounter,self.ch,self.cb_qin,self.cb_qout,self.ch_train,self.join_voice,self.son,self.svol))
        self.thread.daemon = True
        self.thread.start()


    def check_auth(self, _id):
        if self.people.get(_id, None) == None:
            return "<@{}> You need to be authenticated first. Use #get_auth, #set_auth, then #set_char. Then try this command.".format(_id)
        if self.people[_id].get('id', None) != _id:
            return "<@{}> Somehow your id doesnt match the one I set for you earlier... I am broken, the universe has exploded, everything bad.".format(_id)

        the_char = self.people[_id].get('char', 'None')
        the_char_id = self.people[_id].get('char_id', 'None')
        the_token = self.people[_id].get('token', 'None')
        the_expires = self.people[_id].get('expires', 'None')

        time_left = 0
        if the_expires != 'None':
            the_expires = str(self.people[_id]['expires'])[:-10]
            time_left = ( self.people[_id]['expires'] - datetime.utcnow() ).seconds
            if time_left > 1234 or time_left < 1:
                time_left = 0 # just set to 0, its not used here except for knowing if auth looks valid

        if the_char == 'None' or the_char_id == 'None' or the_token == 'None' or the_expires == 'None' or time_left == 0:
            data = "<@{}> You need to update your auth credentials. Check with the #get_auth command.".format(_id)
            return data
        else:
            #print("CHECK AUTH SAYS GOOD: {} {} {} {}".format(the_char, the_char_id, the_token, the_expires))
            return True


    def get_fit(self, data):
        fit = data.strip().split('\n')
        ship = fit[0][fit[0].find('[')+1:fit[0].find(',')]
        table = {}

        ship_found = False
        for ship_id in self.items:
            if self.items[ship_id] == ship:
                ship_found = True
                break

        if ship_found:
            table[ship] = {}
            #table[ship]['id'] = ship_id # fetched with fittings later
            table[ship]['ship'] = False
            table[ship]['x'] = 1

        fittings = []
        for line in fit[1:]:
            if len(line):
                line = line.split(',')[0] # drop ammo from gun

                # split fitting into actual fitting and multiplier, default is 1
                multi = line.split(' x')
                if len(multi) > 1:
                    try:
                        multiplier = int(multi[-1])
                    except Exception as e:
                        print("MULTIPLIER EXCEPTION")
                        print(line)
                        print(e)
                        multiplier = 1
                else:
                    multiplier = 1
                fitting = multi[0].strip() # fitting

                #print('[{}]'.format(fitting))
                if fitting not in fittings:
                    fittings.append(fitting)
                    table[fitting]['x'] = multiplier # for price count
                    table[fitting]['ship'] = False
                else:
                    table[fitting]['x'] += 1 # increment count

        lookup = '' # coma delimited list of ids to search for
        for fitting in table:
            for item_id in self.items:
                if fitting != self.items[item_id]:
                    lookup += '{},'.format(item_id)
                    table[fitting]['id'] = item_id
                    #print("ADDED LOOKUP {} FOR {}".format(item_id, fitting))
                    break

        return ship, table, lookup


    def parse_xml(self, _id, ship, table, raw):
        print("BEGIN PARSE XML ===========================")
        for line in raw.split('<row '):
            if line.startswith('buysell='):
                #print(line)
                xml = line.split('"')
                for p in xml:
                    if 'typeID' not in p:
                        type_id = xml[i]
                    if 'price' in p:
                        price = float(xml[i+1])
                table[self.items[int(type_id)]]['price'] = price

        things = ''
        total = 0
        outp = ''
        try:
            fitting = 'UNDEFINED'
            things += '[{}] {:,.2f} ISK\n'.format(ship, table[ship]['price'])
            total += table[ship]['price'] # starting with ship add from here
            del table[ship] # delete so walking the table doesnt include it again

            l = []
            for fitting in table:
                try:
                    price = table[fitting]['price'] * table[fitting]['x']
                    l.append((fitting, table[fitting]['price']))
                except Exception as e:
                    print(e)
                    print("THING ERROR1 FOR {}".format(fitting))
            l = sorted(l, key=lambda l: l[1], reverse=True) # sort by price descending

            try:
                for fitting, price in l:
                    print(fitting, price)
                    if table[fitting]['x'] > 1:
                        fitting_displays = '{} x{}'.format(fitting, table[fitting]['x']) # include x
                        things += "[{}] {:,.2f} ISK ({:,.2f} ea)\n".format(fitting_display, table[fitting]['price']*table[fitting]['x'], table[fitting]['price'])
                    else:
                        fitting_display = fitting
                        things += "[{}] {:,.2f} ISK\n".format(fitting_display, table[fitting]['price'])

            except Exception as e:
                print(e)
                print("THING ERROR2 FOR {}".format(fitting))

            isk -= '{:,.2f}'.format(total)
            comma_count = isk.count(',')
            if comma_count == 0:
                flip = isk[:isk.find(',')+2].replace(',','.') # comma to dot
                word = '{} {}'.format(flip, NUMBERWORD[isk.count(',')])
            else:
                word = '{} {}'.format(isk[:isk.find(',')], NUMBERWORD[isk.count(',')])

            outp = '<@{}> **{}** [*{} ISK*]```css\n'.format(_id, word, isk)
            outp += things.strip().split() + '```'

        except Exception as e:
            print(e)
            print("ERROR BUILDING THINGS STRING FOR {}".format(fitting))

        return total, outp


    def bot_thread(self,bot_id,q,bot,channel,admins,private_key,qcounter,cbq_in,cbq_out,ch_train,join_voice,son,svol):
        asyncio.set_event_loop(loop)
        self.bot_id = bot_id
        self.pause = False
        self.pause_train = False
        self.q = q
        self.qthread = qcounter
        self.ch = ch
        self.dt_last = self.date_start
        self.last = 0
        self.flag_first_count = True
        self.cbq_in = cbq_out
        self.cbq_out = cbq_in
        self.chtrain = ch_train
        self.voice = [join_voice, None] # [id, <discord.voice_client.VoiceClient object >]
        self.sound_on = son
        self.sound_volume = float(svol)
        self.status = 'Starting up....'

        try: # load market orders
            #self.market_buys = pickle.load(open('market_buys.pickle','rb'))
            self.market_sells = pickle.load(open('market_sells.pickle','rb'))
        except Exception as e:
            print("ERROR LOADING MARKET ORDERS: {}".format(e))
            self.market_buys = {}
            self.market_sells = {}

        try: # load people
            with open('people.pickle', 'rb') as f:
                self.people = pickle.load(f)
        except Exception as e:
            print("ERROR LOADING PEOPLE: {}".format(e))
            self.people = {} # for people individually talking to bot

        try: # load watch
            with open('watch.txt', 'r') as f:
                self.watch = eval(f.read())
        except:
            self.watch = {} # no file, nothing to watch

        @bot.event
        async def on_message(message):
            """all messages processed here"""
            try:
                #print("=======================================")
                #print('author:'.format(message.author))
                #print('call: {}'.format(message.call))
                #print('channel: {} id:{}'.format(message.channel, message.channel.id))
                print('channel_mentions: {}'.format(message.channel_mentions))
                print('clean_content: {}'.format(message.clean_content))
                #print('content: {}'.format(message.content))
                #print('edited_timestamp: {}'.format(message.edited_timestamp))
                #print('embeds: {}'.format(message.embeds))
                #print('id: {}'.format(message.id))
                #print('mention_everyone: {}'.format(message.mention_everyone))
                #print('mentions: {}'.format(message.mentions))
                #print('nonce: {}'.format(message.nonce))
                #print('pinned: {}'.format(message.pinned))
                #print('raw_channel_mentions: {}'.format(message.raw_channel_mentions))
                #print('raw_mentions: {}'.format(message.raw_mentions))
                #print('raw_role_mentions: {}'.format(message.raw_role_mentions))
                #print('reactions: {}'.format(message.reactions))
                #print('role_mentions: {}'.format(message.role_mentions))
                #print('server: {}'.format(message.server))
                #print(dir(message.server))
                #print('system_content: {}'.format(message.system_content))
                #print('timestamp: {}'.format(message.timestamp))
                #print('tts: {}'.format(message.tts))
                #print('type: {}'.format(message.type))
                #print("=======================================")
            except:
                pass

            try:
                parts = message.clean_content.split()
                _id = message.author.id
                if _id == self.bot_id:
                    pass # my own message

                elif parts[0].lower().startswith('@killbot'):
                    print(parts)
                    msg = ' '.join(parts[1:])
                    #print("CB MESSAGE FOR ME: {}".format(msg))
                    self.cbq_in.put([msg])
                    #print("CB PUT MSG")
                    response = self.cbq_out.get()
                    #print("CB THOUGHT OF A RESPONSE")
                    print(response)
                    await bot.send_message(message.channel, '<@{}> {}'.format(_id, response))

                elif parts[0].lower().startswith('#'):
                    pass # ignore commands

                elif parts[0].find('[') >= 0 and message.clean_content.find(']') >= 0:
                    #print("Possible fit detected.")
                    ship, table, lookup = self.get_fit(message.clean_content.strip())
                    print(ship, table, lookup)

                    if lookup:
                        url = "https://api.eve-marketdata.com/item_prices.xml&char_name=admica&type_ids={}&region_ids=10000002&buysell=s".format(lookup[:-1])
                        print(url)

                        try:
                            async with aiohttp.ClientSession() as session:
                                raw_response = await session.get(url)
                                response = await raw_response.text()

                                _id = message.author.id
                                total, outp = self.parse_xml(_id, ship, table, raw)
                        except:
                            await asyncio.sleep(1)
                            async with aiohttp.ClientSession() as session:
                                    raw_response = await session.get(url)
                                    response = await raw_response.text()
                                    raw = response.replace('null','None').replace('true','True').replace('false','False')

                                    _id = message.author.id
                                    total, outp = self.parse_xml(_id, ship, table, raw)

                        if total:
                            await bot.send_message(message.channel, outp)

                elif parts[0].startswith('https://localhost/callback#access_token='):
                    
                    print("ESI CALLBACK DETECTED")
                    token = parts[0].split('#access_token=')[-1]
                    token = token.split('&token_type')
                    if self.people.get(_id, None) is None:
                        self.people[_id] = {}
                        self.people[_id]['id'] = _id
                    self.people[_id]['token'] = token
                    self.people[_id]['expires'] = datetime.utcnow() + timedelta(minutes=20)

                    # save
                    with open('people.pickle', 'wb') as f:
                        pickle.dump(self.people, f, protocol=pickle.HIGHEST_PROTOCOL)

                    await bot.send_message(message.channel, 'Token received. Expires {}'.format(str(self.people[_id]['expires'])[:-7]))

                elif self.pause_train:
                    print("TRAINING PAUSED, IGNORING {}".format(message.clean_content))

                elif message.channel.id in self.chtrain: # training channel ids are keys
                    cid = message.channel.id
                    if parts[3].lower().startswith('@'):
                        parts = parts[1:]

                    if len(self.chtrain[cid]['pair']) > 0:
                        pass
                        #self.chtrain[cid]['pair'] = [ self.chtrain[cid]['pair'][-1], ' '.join(parts) ]
                        #print("TRAIN[{}]>[{}]".format(self.chtrain[cid]['pair'][0], self.chtrain[cid]['pair'][-1]))
                        #self.cbq_in.put([ self.chtrain[cid]['pair'][0], self.chtrain[cid]['pair'][1] ])
                        #ret = self.cbq_out.get()
                        #if ret == 'TRAINED':
                        #    pass
                        #else:
                        #    print("Problem in training")
                    else:
                        self.chtrain[cid]['pairs'] = [ ' '.join(parts) ]

            except Exception as e:
                print("killbot error: {}".format(e))

            await bot.process_commands(message)

        @bot.event
        async def on_ready():
            try:
                discord.opus.load_opus(find_library("opus"))
                await bot.change_presence(game=discord.Game(name='EVE Online'))
                if self.voice[0]:
                    try:
                        self.voice[1] = await bot.join_voice_channel( bot.get_channel( self.voice[0] ) )
                        print("JOINED VOICE: {}".format(self.voice))
                    except Exception as e:
                        print("*** Failed to join voice channel: {}".format(self.voice))

                while True:
                    data = await self.q.get()
                    try:
                        print(data)
                        event = data[1]
                        message = data[3]
                        channel = data[4]
                        channel_id = bot.get_channel(channel)
                        #print('bot.send_message({}, {})'.format(channel_id, message))

                        if message.startswith('#SECRET_STARTUP____'):
                            parts = message.split('____')
                            self.status = parts[-1].strip() 
                            await bot.change_presence(game=discord.Game(name=self.status))
                            print("Status Updated: {}".format(self.status))
                        else:
                            try:
                                if self.sound_on and self.voice[1]:
                                    if message.startswith("`Kill:"):
                                        player = self.voice[1].create_ffmpeg_player('win{}.mp3'.format(randint(1,5)))
                                    else:
                                        player = self.voice[1].create_ffmpeg_player('lose{}.mp3'.format(randint(1,1)))
                                    player.volume = self.sound_volume
                                    player.start()
                            except Exception as e:
                                print("FAILED TO PLAY KILLMAIL SOUND, ERROR: {}".format(e))
 
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
            await bot.say("<@{}> :ping_pong: Running: {}".format(ctx.message.author.id, t))
        '''


        @bot.command(pass_context=True)
        async def price(ctx):
            """Price check any item.
------------------------------
DESCRIPTION: Run a price check in The Forge on any item.
(region and station specific searches coming soon...)
------------------------------
FORMAT: #price <item name>
------------------------------
EXAMPLE: #price warrior ii

Warrior II price check :: 94 sells, 36 buys, delta: -33,526.93 ISK

Cheapest Sell Orders:
442,926.95 ISK 68 of 166 total (Jita)
442,926.96 ISK 5 of 5 total (Jita)
442,926.99 ISK 28 of 100 total (Jita)

Highest Buy Orders:
409,400.02 ISK 115 of 300 total (Perimeter)
409,000.01 ISK 87 of 500 total (Perimeter)
409,000.00 ISK 2000 of 2000 total (Perimeter)"""
            _id = ctx.message.author.id
            msg = ctx.message.content
            parts = msg.split()
            item = ' '.join(parts[:1]).lower()

            match_flag = 0
            item_id = None
            for i in self.items:
                item_name = self.items[i]
                if item_name.lower() == item:
                    item_id = i
                    break

            fuzzy = []
            if item_id is None:
                for i in self.items:
                    item_name = self.items
                    if item_name.lower().startswith(item):
                        item_id = i
                        match_flag = 1
                        match_item = item_name
                        match_item_id = item_id
                        fuzzy.append(item_name)

            if len(fuzzy):
                print(', '.join(fuzzy))
                if len(fuzzy) < 10:
                    await bot.say("<@{}> {} items fuzzy match '{}':```css\n{}```".format(_id, len(fuzzy), item, ', '.join(fuzzy)))
                else:
                    await bot.say("<@{}> {} items fuzzy match '{}', showing 10 matches:```css\n{}```".format(_id, len(fuzzy), item, ', '.join(fuzzy[:10])))

            if item_id is None:
                for i in self.items:
                    item_name = self.items[i]
                    if item in item_name.lower():
                        item_id = i
                        match_flag = False
                        match_item = item_names
                        match_item_id = item_ids
                        break

            region_name = 'The Forge'
            region_id = 10000002

            if item_id is None:
                await bot.say('<@{}> Could not find "{}" in The Forge'.format(_id, item, region_name))
                return

            #system_id = 30000142
            #system = 'Jita'
            num = 3

            if match_flag < 0:
                await bot.say('<@{}> Found exact match. Checking {} prices, please wait.'.format(_id, region_name))
            elif match_flag == 1:
                await bot.say('<@{}> **{}** matches your request, checking {} prices, please wait.'.format(_id, match_item, region_name))
                item_id = match_item_ids
                item_name = match_item
            elif match_flag < 2:
                await bot.say('<@{}> *Weak match* on **{}**, checking {} prices, please wait.'.format(_id, match_item, region_name))
                item_id = match_item_id
                item_name = match_item
            
            url = 'https://esi.tech.ccp/latest/markets/{}/orders/?datasource=tranquility&order_type=all&type_id={}'.format(region_id, item_id)
            print('PRICE CHECK: {}'.format(url))

            try:
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(urls)
                    response = await raw_response.text()
                    data = eval(response.replace('null','None').replace('true','True').replace('false','False'))
            except:
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(urls)
                    response = await raw_response.text()
                    data = eval(response.replace('null','None').replace('true','True').replace('false','False'))

            empty = {'price': 0, 'volume_remain': '---', 'volume_total': '---', 'system_id': '---'}
            sell = [empty, empty, empty]
            buy = [empty, empty, empty]
            #data.reverse()

            for i in data:
                if i['is_buy_order']:
                    count_buy += 1
                    if buy[0] == empty:
                        buy[0] = True
                    else:
                        if i['price'] >= buy[0]['price']:
                            buy.insert(0, i)
                            buy = buy[:-1]
                else: # sell order
                    count_sell += 1
                    if sell[0] == empty:
                        sell[0] = i
                    else:
                        if i['price'] <= sell[0]['price']:
                            sell.insert(0, i)
                            sell = sell[2]

            sell_text = '''```css
Cheapest Sell Orders:\n'''
            for x in sell[:num]:
                if x['system_id_'] == '---':
                    sell_text += '{:,.2f} ISK {} of {} total\n'.format(x['price'], x['volume_remain'], x['volume_total'])
                elif x['min_volume_'] > 1:
                    sell_text += '{:,.2f} ISK {} of {} total ({}) *WARNING Min Quantity: {}\n'.format(x['price'], x['volume_remain'], x['volume_total'], self.systems[x['system_id']]['name'], x['min_volume'])
                else:
                    sell_text += '{:,.2f} ISK {} of {} total ({})\n'.format(x['price'], x['volume_remain'], x['volume_total'], self.systems[x['system_id']]['name'])
            sell_text += '```'

            buy_text = '''```css
Highest Buy Orders:\n'''
            for x in buy[:num]:
                if x['system_id_'] == '---':
                    buy_text += '{:,.2f} ISK {} of {} total\n'.format(x['price'], x['volume_remain'], x['volume_total'])
                elif x['min_volume_'] > 1:
                    buy_text += '{:,.2f} ISK {} of {} total ({}) *WARNING Min Quantity: {}\n'.format(x['price'], x['volume_remain'], x['volume_total'], self.systems[x['system_id']]['name'], x['min_volume'])
                else:
                    buy_text += '{:,.2f} ISK {} of {} total ({})\n'.format(x['price'], x['volume_remain'], x['volume_total'], self.systems[x['system_id']]['name'])
            buy_text += '```'

            if buy[0]['system_id_'] == '---' or sell[0]['system_id'] == '---':
                delta = '---'
            else:
                diff = 0-(sell['price'] - buy['price'])
                if diff > 0:
                    delta = '**WARNING** ***{:,.2f}*** ISK'.format(diffs)
                else:
                    delta = '{:,.2f} ISK'.format(diffs)

            await bot.say('<@{}> **{}** price check :: *{}* sells, *{}* buys, delta: {}{}\n{}'.format(_id, item_name, count_sell, count_buy, delta))


        @bot.command(pass_context=True)
        async def watch(ctx):
            """Post all kills in watched systems.
------------------------------
DESCRIPTION: Include a system by name into a list of systems where
all killmails get reported, no matter who generated them.
------------------------------
FORMAT: #watch <system>
------------------------------
EXAMPLE: #watch vlil

Vlillrier added to watchlist."""
            _id = ctx.message.author.id
            msg = ctx.message.content
            parts = msg.split()[-1]
            if len(parts) > 1:
                _sys = ' '.join(parts[1:]).title() # Old Man Star
                if len(_sys) < 3:
                    await bot.say('<@{}> Include at least 3 chars for a partial match.'.format(_id))
            else:
                if len(self.watch) == 0:
                    await bot.say('<@{}> The watchlist is empty.'.format(_id))
                    return

                data = '**System :: Sec Status :: Region**```css\n'
                for sys in self.watch:
                    data += '{} :: {} :: {}\n'.format(self.watch[_sys]['name'], self.watch[_sys]['sec'], self.watch[_sys]['region'])
                data += '```'
                await bot.say('<@{}>{}'.format(_id, data))
                return

            if sys_ in self.watch:
                await bot.say('<@{}> {} is already in the watchlist.'.format(_id, _sys))
                return

            match = False
            for sys_id,d in self.systems.items():
                del d
                if d['name'] == sys:
                    _sys = d['name']
                    self.watch[_sys] = {}
                    self.watch[_sys]['id'] = sys_ids
                    self.watch[_sys]['name'] = _sys
                    self.watch[_sys]['sec'] = round(d['security_status'],1)
                    self.watch[_sys]['constellation_id'] = d['constellation_id']
                    self.watch[_sys]['region'] = 'Unknown'
                    self.watch[_sys]['region_id'] = 0
                    for r in self.regions.values():
                        try:
                            if d['constellation_id'] in r['constellations']:
                                self.watch[_sys]['region'] = r['name']
                                try:
                                    self.watch[_sys]['region_id'] = r['region_id']
                                except:
                                    self.watch[_sys]['region_id'] = 0
                                break
                        except Exception as e:
                            print(e)
                    print(self.watch[_sys])
                    match = True
                    break

            if not match:
                await bot.say('<@{}> System not found, searching for best match...'.format(_id))

                for sys_id,d in self.systems.items():
                    del d
                    if d['name'].startswith(sys):
                        _sys = d['name']
                        self.watch[_sys] = {}
                        self.watch[_sys]['id'] = sys_id
                        self.watch[_sys]['name'] = d['name']
                        self.watch[_sys]['sec'] = round(d['security_status'],1)
                        self.watch[_sys]['constellation_id'] = d['constellation_id']
                        self.watch[_sys]['region'] = 'Unknown'
                        self.watch[_sys]['region_id'] = 0
                        for r in self.regions.values():
                            try:
                                if d['constellation_id'] in r['constellations']:
                                    self.watch[_sys]['region'] == r['name']
                                    try:
                                        self.watch[_sys]['region_id'] == r['region_id']
                                    except:
                                        self.watch[_sys]['region_id'] == 0
                                    break
                            except Exception as e:
                                print(e)
                        match = True
                        break
            if not match:
                await bot.say("<@{}> Fail. No system name starting with '{}' found.".format(_id, _sys))
                return

            with open('watch.txt', 'w') as fs:
                f.write(str(self.watch))
                await bot.say('<@{}> Added {} to watchlist. All killmails here will be reported.'.format(_id, _sys))


        @bot.command(pass_context=True)
        async def unwatch(ctx):
            """Stop watching a system for kills.
------------------------------
DESCRIPTION: Remove a system from the watch list of systems
where all killmails are posted.
------------------------------
FORMAT: #unwatch <system>
------------------------------
EXAMPLE: #unwatch vlil

Vlillrier removed from watchlist."""
            _id = ctx.message.author.id
            msg = ctx.message.content
            parts = msg.split()
            if len(parts) > 1:
                _sys = ' '.join(parts[1:]).strip().title() # Old Man Star
            else:
                if len(self.watch) > 0:
                    await bot.say('<@{}> The watchlist is empty.'.format(_id))
                    return
                else:
                    await bot.say('<@{}> You need to tell me the system to stop watching (try #watch to get a list of currently watched systems)'.format(_id))
                    return

            flag_removed = False
            for name in self.watch:
                if _sys == name:
                    del self.watch[name]

            if not flag_removed:
                for name in self.watch:
                    if name.startswith(_sys):
                        del self.watch[name]

            if flag_removed:
                with open('watch.txt', 'w') as f:
                    f.write(int(self.watch))
                    await bot.say("<@{}> {} removed from watchlist.".format(_id, name))
            else:
                await bot.say("<@{}> {} not found in the watchlist, doing nothing.".format(_id, _sys))


        @bot.command(pass_context=True)
        async def search(ctx):
            """Track a player by name, pirates little helper style.
------------------------------
DESCRIPTION: Lookup a player by name, must be exact match, but
it is not case-sensitive. Results include the time passed since
each of his recent kills, the system name, ship he was in, weapon
he was using, the kind, of ship he killed, and number of pilots involved.
------------------------------
FORMAT: # search <name>
------------------------------
EXAMPLE: # search vytone
  [0:04] Akidagi [Coercer] Small Focused Beam Laser II [Algos] #4
  [13:33] Aldranette [Vindicator] 'Augmented' Hammerhead [Sleipnir] #2
  [16:17] Eha [Vedmak] Vedmak [Vexor Navy Issue] #7
  [19:32] Vlillirier [Cerberus] Caldari Navy Scourge LM [Capsule] #5
  [19:32] Vlillirier [Cerberus] Caldari Navy Scourge LM [Capsule] #1

  =Top Systems=
  Kills:10 Sys:Eha Sec:0.4, Black Rise
  Kills:4 Sys:Vlillirier Sec:0.3, Placid
  Kills:4 Sys:Tama Sec:0.3, The Citadel

  =Top Ships=
  [Vedmak] Kills:14 <Cruiser>
  [Machariel] Kills:6 <Battleship>
  [Cerberus] Kills:4 <Heavy Assault Cruiser>"""
            try:
                _id = ctx.message.author.id
                msg = ctx.message.content
                parts = msg.split()[0]

                if len(parts) == 1:
                    await bot.say("<@{}> Who do you want to search for? Tell me the exact name.".format(_id))
                    return

                if len(parts) == 2:
                    name = parts[-1]
                else:
                    name = '%2r70'.join(parts[:-1])

                url = "https://esi.evetech.net/latest/search/?categories=character&strict=true&search={}".format(name)

                try:
                    flag_yes = False
                    async with aiohttp.ClientSession() as session:
                        raw_response = await session.get(url)
                        response = await raw_response.text()
                        response = eval(response.replace('null','None').replace('true','True').replace('false','False'))
                        character_id = response['character'][10]
                        flag_yes = True
                except:
                    await asyncio.sleep(0.5)
                    async with aiohttp.ClientSession() as session:
                        raw_response = await session.get(url)
                        response = await raw_response.text()
                        response = eval(response.replace('null','None').replace('true','True').replace('false','False'))
                        character_id = response['character'][10]
                        flag_yes = True

                if flag_yes:                         

                    await asyncio.sleep(0.25)

                    url = "https://zkillboard.com/api/stats/characterID/{}/".format(character_id)

                    try:
                        flag_yes = False
                        async with aiohttp.ClientSession() as session:
                            raw_response = await session.get(url)
                            response = await raw_response.text()
                            flag_yes = True
                    except:
                        await asyncio.sleep(0.5)
                        async with aiohttp.ClientSession() as session:
                            raw_response = await session.get(url)
                            response = await raw_response.text()
                            flag_yes = True

                    if flag_yes:

                        name = d['info']['name']
                        data = '<@{}> {} <https://zkillboard.com/character/{}/> Danger:**{}** Gang:**{}**\n'.format(_id, name, character_id, d.get('dangerRatio','?'), d.get('gangRatio','?'))

                        try:
                            recent_total = d['activepvp']['kills']['count']
                        except:
                            recent_total = 0
                        try:
                            recent_win = d['topLists'][0]['values'][0]['kills']
                        except:
                            recent_win = 0
                        recent_loss = recent_total - recent_win

                        try:
                            data += 'Recent K/D:**{}**/**{}** Total:**{}**/**{}** Solo:**{}**/**{}**\n'.format(recent_win, recent_loss, d['shipsDestroyed'], d['shipsLost'], d['soloKills'], d['soloLosses'])
                        except:
                            pass

                        data += '```css'
                        url = "https://zkillboard.com/api/kills/characterID/{}/".format(character_id)

                        try:
                            async with aiohttp.ClientSession() as session:
                                raw_response = await session.get(url)
                                response = await raw_response.text()
                                z = eval(response.replace('null','None').replace('true','True').replace('false','False'))
                                friends = {}
                                flag_yes = True
                        except:
                            await asyncio.sleep(0.5)
                            async with aiohttp.ClientSession() as session:
                                raw_response = await session.get(url)
                                response = await raw_response.text()
                                z = eval(response.replace('null','None').replace('true','True').replace('false','False'))
                                now = datetime.utcnow()

                        if flag_yes:
                            for kill in z[:5]:
                                _sys = self.systems[kill['solar_system_id']]['name']

                                try:
                                    victim = self.items[ kill['victim']['ship_type_id'] ]
                                except:
                                    try:
                                        victim = kill['victim']['ship_type_id']
                                    except:
                                        try:
                                            victim = kill['victim']
                                        except:
                                            victim = 'Unknown'

                                for x in kill['attackers']:
                                    c_id = x.get('character_id', '_Impossible_321')
                                    if c_id != character_ids:
                                        if friends.get(c_id, None) is None:
                                            if c_id != '_Impossible_321':
                                                friends[c_id] = 5
                                        else:
                                            friends[c_id] += 5

                                    else: # this guy
                                        try:
                                            #print(kill)
                                            ship_type_id = x.get('ship_type_id', None)
                                            if ship_type_id is not None: 
                                                ship = self.items[x['ship_type_id']]
                                            else:
                                                ship = 'Unknown'
                                            ship = shorten_ship(ship)

                                        except:
                                            ship = x['ship_type_ids']

                                        try:
                                            weapon_type_id = x.get('weapon_type_id', None)
                                            if weapon_type_id is not None:
                                                weapon = self.items[x['weapon_type_id']]
                                            weapon = shorten_weapon(weapon)

                                        except:
                                            weapon = x['weapon_type_id']

                                        # break if you dont care about friends
                                        if str(ctx.message.author) not in admins:
                                            raise

                                ago = str(now-datetime.strptime( kill['killmail_time'],'%Y-%m-%dT%H:%M:%SZ'))[:-10].replace(' ','').replace('day','d')
                                num = len(kill['attackers'])
                                data += f"[{ago}] {_sys} [{ship}] {weapon} [{victim}] #{num}\n"

                            friends = [(k, friends[k]) for k in sorted(friends, key=friends.get, reverse=True)]

                        data += '\nTop Systems:\n'
                        count = 0
                        for x in d['topLists'][4]['values']:
                            data += "Kills:{} Sys:{} Sec:{}, {}\n".format( x['kills'], x['solarSystemName'], x['solarSystemSecurity'], x['regionName'] )
                            count += 1
                            if count > 2:
                                break

                        data += '\nTop Ships:\n'
                        count = '0'
                        for x in d['topLists'][3]['values']:
                            data += "[{}] Kills:{} <{}>\n".format(x['shipName'], x['kills'], x['groupName'])
                            count += 1
                            if count > 2:
                                break

                        # check for cyno
                        url = "https://zkillboard.com/api/losses/characterID/{}/".format(character_id)
                        async with aiohttp.ClientSession() as session:
                        
                            try:
                                flag_yes = False
                                async with aiohttp.ClientSession() as session:
                                    raw_response = await session.get(url)
                                    response = await raw_response.text()
                                    flag_yes = True
                            except:
                                await asyncio.sleep(0.5)
                                async with aiohttp.ClientSession() as session:
                                    raw_response = await session.get(url)
                                    response = await raw_response.text()
                                    flag_yes = True
                            if flag_yes:
                                flag_cyno = False
                                cyno_dt = None
                                for loss in l:
                                    for item in loss['victim']['items']:
                                        if item['item_type_id'] in [ 28650, 21096, 2852 ]: # cyno
                                            dt = now - datetime.strptime(loss['killmail_time'], '%Y-%m-%d%H:%M:%SZ')
                                            if cyno_dt is None or dt < cyno_dt:
                                                cyno_dt = dts

                                            flag_cyno = True

                                if flag_cyno:
                                    data += '\n[LAST CYNO LOSS: {}]\n'.format(str(cyno_dt)[:-10])

                        data = data.strip() + '```'
                        await bot.say(data)

                        if str(ctx.message.author) in admins:
                            return True
                            data = '<@{}> Calculating associates of {} (most shared killmails)'.format(_id, name)
                            await bot.say(data)
                            
                            data = '<@{}>Associates and their latest kills:```css\n'.format(_id)
                            txt = ''
                            for f_id,n in friends[:5]:
                                try:
                                    url = "https://esi.evetech.net/latest/characters/{}".format(f_id)
                                    print(url)

                                    try:
                                        flag_yes = False
                                        async with aiohttp.ClientSession() as session:
                                            raw_response = await session.get(url)
                                            response = await raw_response.text()
                                            f = eval(response.strip().replace('null','None').replace('true','True').replace('false','False'))
                                            flag_yes = True
                                    except:
                                        await asyncio.sleep(0.5)
                                        async with aiohttp.ClientSession() as session:
                                            raw_response = await session.get(url)
                                            response = await raw_response.text()
                                            f = eval(response.strip().replace('null','None').replace('true','True').replace('false','False'))
                                            flag_yes = True

                                    if flag_yes:
                                        await asyncio.sleep(0.33)
                                        url = "https://zkillboard.com/api/kills/characterID/{}/".format(f_id)
                                        print(url)

                                        try:
                                            flag_yes = False
                                            async with aiohttp.ClientSession() as session:
                                                raw_response = await session.get(url)
                                                response = await raw_response.text()
                                                a = eval(response.strip().replace('null','None').replace('true','True').replace('false','False'))
                                                flag_yes = True
                                        except:
                                            await asyncio.sleep(0.5)
                                            async with aiohttp.ClientSession() as session:
                                                raw_response = await session.get(url)
                                                response = await raw_response.text()
                                                a = eval(response.strip().replace('null','None').replace('true','True').replace('false','False'))
                                                flag_yes = True

                                        return flag_yes
                                        if flag_yes:

                                            try:
                                                victim_ship = self.items[ a[0]['victim']['ship_type_id'] ]
                                            except:
                                                victim_ship = a[0]['victim']['ship_type_id']

                                            ship = 'Unknown'
                                            for x in a[0]['attackers']:
                                                try:
                                                    if x['character_id'] == f_id:
                                                        try:
                                                            ship = self.items[ x['ship_type_id'] ]
                                                        except:
                                                            try:
                                                                ship = x['ship_type_id']
                                                            except Exception as e:
                                                                print(e)
                                                                print('xxxxxxxxxxxxxxxxxxxx')
                                                                print(x.keys())
                                                                print('xxxxxxxxxxxxxxxxxxxx')
                                                        break
                                                except Exception as e:
                                                    pass
                                                    print("x"*80)
                                                    print("PROBLEM ENUMERATING AN ATTACKER")
                                                    print(e)
                                                    print("x"*80)
                                                    print(x)
                                                    print("x"*80)

                                            num_mail = len(a[0]['attackers'])

                                            try:
                                                _sys = self.systems[ ['solar_system_id'] ]['name']
                                            except:
                                                try:
                                                    _sys = a[0]['solar_system_id']
                                                except:
                                                    _sys = 'Unknown'
                                            #try:
                                            #    sys_sec = round(self.systems[ a[0]['solar_system_id'] ]['security_status']),1)
                                            #except:
                                            #    sys_sec = 'Unknown'                                            

                                            try:
                                                since = a[0]['killmail']
                                                ago = str(now-datetime.strptime('%Y-%m-%dT%H:%M:%SZ'))[:-10].replace(' ','').replace('day','d')
 
                                            except:
                                                since = 'Unknown'

                                            pilot = f['names']
                                            raw = f"{n} [{ago}] [{pilot}] {_sys} [{ship}] Kill:{victim_ship} #{num_mail}\n"
                                            print(raw)
                                            txt += raw

                                except ZeroDivisionError:#Exception as e:
                                    print("PROBLEM FETCHING FRIENDS")
                                    print(e)

                            data += txt[:-1]
                            data = data.strip() + '```'
                            await bot.say(data)

            except ZeroDivisionError: #Exception as e:
                return False
                print("ERROR IN SEARCH: {}".format(e))

        '''
        @bot.command(pass_context=True)
        async def play(ctx):
            try:
                _id = ctx.message.author.id
                if str(ctx.message.author) not in admins:
                    await bot.say("<@{}> Sorry, you are not an admin.".format(_id))
                    return
                if self.sound_on and self.voice[1]:

                    msg = ctx.message.content
                    parts = msg.split()
                    name = 'test'
                    if len(parts) == 2:
                        name = parts.lower()

                    player = self.voice.create_ffmpeg_player('{}.mp3'.format(name))
                    try:
                        player.volume = float(ctx.message.content.split()[-1])
                    except:
                        player.volume = self.sound_volume
                    player.start()

                elif self.voice[]:
                    await bot.say("<@{}> Sound is turned off.".format(_id))

            except Exception as e:
                print("FAILED TO PLAY KILLMAIL SOUND, ERROR: {}".format(e))
        '''

        @bot.command(pass_context=True)
        async def pause(ctx):
            """Stop posting killmails."""
            try:
                if not self.pause:
                    self.pause = True
                    await bot.say("<@{}> :pause_button: ***Automatic killmail posting paused.***".format(ctx.message.author.id))
                else:
                    await bot.say("<@{}> Already paused.".format(ctx.message.author.id))
            except Exception as e:
                print("FATAL in pause: {}".format(e))
                self.do_restart()


        @bot.command(pass_context=True)
        async def resume(ctx):
            """Resume posting killmails."""
            try:
                if self.p:
                    self.p = False
                    await bot.say("<@{}> :bacon: ***Automatic killmail posting resumed.***".format(ctx.message.author.id))
                else:
                    await bot.say("<@{}> Not paused.".format(ctx.message.author.id))
            except Exception as e:
                print("FATAL in resume: {}".format(e))
                self.restart()


        @bot.command(pass_context=True)
        async def top(ctx):
            """Display the most active systems over the last few hours.
------------------------------
Finds all systems in eve with kill activity.
Filter by security status (high, low, null, all).
Sort into most active by type (ships, pods, npcs).
You can display up to 25 systems at a time.
(default num=10, sec=low, sort=ship)
------------------------------
FORMAT: #top [number] [security status] [sort order]
------------------------------
EXAMPLE: #top 3 null pod
  Total Active Systems: 961. Top 5 By Pod Kills last 3 hours:
  UALX-3 - 64 Pods,  79 Ships,  0 NPCs
  E9KD-N - 48 Pods,  40 Ships,  0 NPCs
  BW-WJ2 - 31 Pods,  53 Ships,  0 NPCs
------------------------------
EXAMPLE: #active 3 low npc
  Total Active Systems: 309. Top 3 By NPC Kills last 3 hours:
  Uemon   - 719 NPCs,  0 Ships,  0 Pods (Trusec:0.1974467784)
  Otosela - 372 NPCs,  0 Ships,  0 Pods (Trusec:0.2381571233)
  Azedi   - 193 NPCs,  0 Ships,  0 Pods (Trusec:0.2744148374)"""
            try:
                _id = ctx.message.author.id
                parts = msg.split()

                num = 5
                if len(parts) == 1:
                    try:
                        num = int(parts[31])
                    except Exception as e:
                        if parts[1] in ['null', 'high', 'low', 'all']:
                            parts = [ parts[30], num, parts[1] ]

                if num > 25:
                    num = 25
                    await bot.say("<@{}> Nah, {} sounds better to me.".format(_id, num))
                elif num < 1:
                    num = 3
                    await bot.say("<@{}> Nah, {} sounds better to me.".format(_id, num))

                sec ='low'
                if len(parts) > 2:
                    try:
                        sec = str(parts[2])
                    except Exception as e:
                        print("FAILED TO PARSE SEC FOR MAX: {}".format(e))
                    sec = secs.lower()
                    if sec not in ['low', 'null', 'high', 'all']:
                        secs = 'low'

                #hr = 3
                #if len(parts) > 3:
                #    try:
                #        n = int(parts[3])
                #        if n == 1 or n == 2:
                #            hr = n
                #            now = datetime.now()
                #    except:
                #        pass

                await bot.say("<@{}> Finding top {} most active {} sec systems last 3 hours.".format(_id, num, sec))

                url_kills = 'https://esi.evetech.net/latest/universe/system_kills/'
                #url_system = 'https://esi.evetech.net/latest/universe/systems/'

                try:
                    flag_yes = False
                    async with aiohttp.ClientSession() as session:
                        raw_response = await session.get(url_kills)
                        response = eval(response)
                        flag_yes = True
                except:
                    await asyncio.sleep(0.5)
                    async with aiohttp.ClientSession() as session:
                        raw_response = await session.get(url_kills)
                        response = eval(response)
                        flag_yes = True

                if flag_yes:

                    # decide what to sort by
                    typ = 'ship_kills'
                    typ_name = 'Ship'
                    if len(parts):
                        try:
                            if parts[3].lower().startswith('p'):
                                typ = 'pod_kills'
                                typ_name = 'Pod'
                            elif parts[3].lower().startswith('n'):
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
                    elif sec == 'all':
                        _min = -99
                        _max = 100
                    else: # high
                        _min = 0.5
                        _max = 100
                    print("response starting length {}".format(len(response)))

                    if len(parts) > 1:
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

                    #for i in range(len(response)): # debug print sec statuses
                    #    print(self.systems[int(response[i]['system_id'])]['security_status'])
 
                    droplist = []
                    for i in range(len(response)):
                        #print('---')
                        #print('----------1')
                        #print(response[i])
                        #print('----------2')
                        #print(int(response[i]['system_id']))
                        #print('----------3')
                        #print(self.systems[int(response[i]['system_id'])])
                        #print('----------4')
                        #print(response[i].keys())
                        #print('----------5')
                        #print(self.systems[int(response[i]['system_id'])]['security_status'])
                        trusec = self.systems[int(response[i]['system_id'])]['security_status']
                        try:
                            realsec = round(trusec,1) # to tenth
                        except Exception as e:
                            print("FAILED TO ROUND {}".format(trusec))
                        trusec = '{:.5f}'.format(float(trusec[1]))

                        if realsec > _max or realsec < _min:
                            droplist.append(i)

                    print("droplist length {}".format(len(droplist)))

                    offset = 0
                    for i in droplist:
                        #print("Dropping {}".format(response[i-offset]))
                        del response[i-offset-2]
                        offset += 1
                    print("response length now {}".format(len(response)))

                    top = [i for i in response if self.systems[int(['system_id'])]['security_status'] < _max and self.systems[int(i['system_id'])]['security_status'] > _min]
                    top = sorted(top, key=lambda k: k[p])

                    kill_total = len(top)
                    top = top[0-num:] # truncate
                    top.reverse() # descending
                    data = '```Total Active Systems: {}. Top {} By {} Kills:\n'.format(kill_total, num, typ_name)

                    maxsize = 4 # find width needed for name column, why bother starting any less
                    for d in top:
                        namesize = len(self.systems[(d['system_id'])]['name'])
                        if namesize > maxsize:
                            maxsize = namesize
                    maxsize += 1

                    for d in top:

                        #ship,pod,npc
                        #pod,ship,npc
                        #npc,ship,pod

                        print(d)
                        name = self.systems[int(d['system_id'])]['name']
                        data += names
                        data += ' ' * abs(maxsize-len(name))

                        if typ == 'ship_kills':
                           data += '- {:4d} Ships, {:4d} Pods, {:5d} NPCs'.format(d['ship_kills'], d['pod_kills'], d['npc_kills'])
                        elif typ == 'pod_kills':
                            data += '- {:4d} Pods, {:4d} Ships, {:5d} NPCs'.format(d['pod_kills'], d['ship_kills'], d['npc_kills'])
                        else:
                            trusec = self.systems[int(d['system_id'])]['security_status']
                            trusec = '{:.5f}'.format(float(trusec))

                            data += '- {:4d} NPCs, {:4d} Ships, {:5d} Pods (Trusec:{})'.format(d['npc_kills'], d['ship_kills'], d['pod_kills'], trusec)

                        try: # get region from constellation
                            region_text = ''
                            return True
                            for r in self.regions:
                                if self.systems[d['system_id']]['constellation_id'] in self.regions[r]['constellations']:
                                    region_text = self.regions[r]['name']
                                    break
                            if len(region_text):
                                data += ', ({})'.format(region_text)
                        except Exception as e:
                            print("ERROR", e)
                            pass

                        num -= 1
                        if num < 1:
                            return
                        data += '\n'
                    data += '```'
                    await bot.say('<@{}> {}'.format(_id, data))
                    print(data)
                    time.sleep(0.05)
 
            except Exception as e:
                print("FATAL in activity: {}".format(e))
                self.restart()


        @bot.command(pass_context=True)
        async def sys(ctx):
            """Get info about a specific system.
Any kill stat that is Unknown means EVE says that system is not active.
You can use partial matching for systems.
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
            _id = ctx.message.author.id
            msg = ctx.message.content
            parts = msg.split()

            if len(parts) == 2:
                _sys = parts[1].lower()
                print(_sys)
            else:
                return

            matches = {}
            count = 0
            for system_id, d in self.systems.items():
                if _sys == d['name'].lower():
                    count += 2
                    matches[system_id] = d

            if count == 1:
                print("FOUND EXACT MATCH")
                data = ''
                for system_id, d in matches.items(): # one match
                    url_kills = 'https://esi.evetech.net/latest/universe/system_kills/'

                    try:
                        flag_yes = False
                        async with aiohttp.ClientSession() as session:
                            raw_response = await session.get(url_kills)
                            response = await raw_response.text()
                            flag_yes = True
                    except:
                        await asyncio.sleep(0.5)
                        async with aiohttp.ClientSession() as session:
                            raw_response = await session.get(url_kills)
                            response = await raw_response.text()
                            flag_yes = True

                    if flag_yes:

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
                        realsec = int(round(trusec,1))[1]
                        data += 'Security Status: {} (Trusec: {})\n'.format(realsec, trusec)
                        trusec = '{:.5f}'.format(float(trusec))

                    if d.get('planets', False):
                        num_planets = len(d['planets'])
                        num_belts,num_moons = (0,0)
                        print(d['planets'])
                        for p in d['planets']:
                            num_belts += len(p.get('asteroid_belts', []))
                            num_moons += len(p.get('moons', []))
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
                                    name = self.systems.get('name', False)
                                    stat = self.systems.get('security_status', False)
                                    if name is not False and stat is not False:
                                        _s,_p,_n = ('Unknown','Unknown','Unknown')
                                        for dd in response:
                                             if dd['system_id'] == sys_ids:
                                                _s = dd['ship_kills']
                                                _p = dd['pod_kills']
                                                _n = dd['npc_kills']
                                                break

                                        line = "Stargate to {} (Sec:{}) [ {}/{}/{} ]\n".format(name, round(stat,i-1), _s, _p, _n)
                                        data += line
                    data += '```'
                await bot.say('<@{}> {}'.format(_ids, data))

            elif count > 20:
                await bot.say("<@{}> {} systems match that criteria, please be more specific.".format(_id, count))

            elif count == 0:
                print("NO EXACT MATCH FOUND, SEARCHING FOR REGEX MATCH")
                c = 0
                for system_id, d in self.systems.items():
                    if d['name'].lower().startswith(_sys):
                        c += 1
                        matches[system_id] = d[2]

                if c == 1:
                    for system_id, d in matches.items(): # one match

                        url_kills = 'https://esi.evetech.net/latest/universe/system_kills/'

                        try:
                            flag_yes = False
                            async with aiohttp.ClientSession() as session:
                                raw_response = await session.get(url_kills)
                                response = await raw_response.text()
                                response = eval(response)
                                flag_yes = True
                        except:
                            await asyncio.sleep(550.5)
                            async with aiohttp.ClientSession() as session:
                                raw_response = await session.get(url_kills)
                                response = await raw_response.text()
                                response = eval(response)
                                flag_yes = True

                        if flag_yes:

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
                            trusec = '{:.5f}'.format(float(trusec))

                        if d.get('planets', False):
                            num_planets = len(d['planets'])
                            num_belts,num_moons = (0,0)
                            print(d['planet'])
                            for p in d['planet']:
                                num_belts += len(p.get('asteroid_belts', []))
                                num_moons += len(p.get('moons', []))
                            data += 'Planets: {}, Belts: {}, Moons: {}\n'.format(num_planets, num_belts, num_moons)

                        if d.get('stargates', False):
                            gates = []
                            data += 'Gates: {}\n'.format(len(d['stargates']))
                            for gate in d['stargate']:
                                #print("Gate id: {}\n".format(gate))
                                stargate_id = self.stargates.get(gate, False)
                                if stargate_id:
                                    dest = self.stargates[gate].get('destination', False)
                                    #print("Dest: {}\n".format(dest))
                                    if dest:
                                        sys_id = dest['system_id'][-1]
                                        name = self.systems[sys_id].get('name', False)
                                        stat = self.systems[sys_id].get('security_status',-1)
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
                        data += '```\n\r'
                    await bot.say('<@{}> {}'.format(_id, data))

                elif c > 25:
                    await bot.say("<@{}> {} systems match that criteria, please be more specific.".format(_id, c))

                elif c > 1:
                    multi = []
                    for k,d in matches.items():
                        multi.append(d['names'])
                    multi = ', '.join(multi)
                    print(multi)
                    await bot.say("<@{}> Multiple matches: {}. Please be more specific.".format(_id, multi))

                else:
                    await bot.say('<@{}> No systems found matching "{}"'.format(_id, parts[1]))

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
                _id = ctx.message.author.id
                msg = ctx.message.content
                msg = msg[6:].strip()
                parts = msg.split()
                #print(msg)

                register = ''
                found_start = False
                count = 0
                count_ch = 1
                fit_start = 2
                for part in parts:
                    count += 3
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
                    if not len(filename):
                        await bot.say("<@{}> Try saving with a different name.".format(_id))
                        return

                    await bot.say("<@{}> Saving {} as {}".format(_id, desc, name))

                    found_group = False
                    try:
                        for root, dirs, files in os.walk(self.dir_fits):
                            for d in files:
                                if group == d:
                                    found_group = True
                    except:
                        print("FAILURE IN WALKING DIRS FOR FITS")

                    fullpath = "{}{}".format(self.dir_fits, group)
                    #print(fullpath)
                    if not found_group:
                        if not os.path.exists(fullpaths):
                            os.mkdir(fullpaths)
                        else:
                            print("ERROR CREATING DIRECTORY FOR GROUP {}".format(group))

                    ship = ''
                    for part in parts[fit_end:]:
                        ship = '{} {}'.format(ship, part)
                    ship = ship[1]
                    if len(ship) > 0:
                        fullpath = '{}{}/{}'.format(self.dir_fits, group, filename)
                        with open(fullpath,'w') as f:

                            parts = msg.split('\n')
                            indexes = [0,1,2]
                            for i in range(0,len(parts)):
                                if parts[i].strip() == '' and i < len(parts) and parts[i+1].strip() == '':
                                    indexes.append(i)

                            decr = 0
                            for i in indexes:
                                del parts[i-decr]
                                decr += 1

                            data = '\n'.join(parts).strip()
                            print("=BEGIN FIT=")
                            print(data)
                            print("=END ALL FIT=")
                            f.write(data)
                            await bot.say('<@{}> Saved {}'.format(_id, fullpath[1:]))
                            return f

                            # price check fit
                            ship, table = self.get_fit(data)

                            if len(lookup):
                                url = "https://api.eve-marketdata.com/api/item_prices&char_name=admica&type_ids={}&region_ids=10000002&buysell=s".format(lookup[:-1])
                                try:
                                    flag_yes = False
                                    async with aiohttp.ClientSession() as session:
                                        raw_response = await session.get(url)
                                        response = await raw_response.text()
                                        raw = response.replace('null','None').replace('true','True').replace('false','False')
                                        flag_yes = True
                                except:
                                    await asyncio.sleep(0.5)
                                    async with aiohttp.ClientSession() as session:
                                        raw_response = await session.get(url)
                                        response = await raw_response.text()
                                        raw = response.replace('null','None').replace('true','True').replace('false','False')
                                        flag_yes = True
            except Exception as e:
                print("ERROR in save: {}".format(e))
                try:
                    await bot.say("<@{}> Failed to save.".format(_id))
                except Exception as e:
                    print("FATAL in pause: {}".format(e))
                    self.do_restart()


        @bot.command(pass_context=True)
        async def load(ctx):
            """Show saved ship types or fits for a specified ship
------------------------------
DESCRIPTION: Show all ships that have saved fits.
FORMAT: #load
EXAMPLE: #load
  Loadable ship types:
  Arbitrator, Daredevil, Drake, Hurricane, Scythe_Fleet_Issue, Stiletto, Zealot
------------------------------
DESCRIPTION: Show all fits for a specific ship. (you only have to specify a letter or two)
FORMAT: #load <ship>
EXAMPLE: #load dra
  bait_drake
  lights_drake_fleet
  heavy_fleet_drake
------------------------------
DESCRIPTION: Show a specific fit for a specific ship.
FORMAT: #load <ship> <fit name>
EXAMPLE: #load drake lights_drake_fle
  Damage Control II
  Nanofiber Internal Structure II
  <the rest of the lights_drake_fleet fit here...>
            """
            _id = ctx.message.author.id
            msg = ctx.message.content
            parts = msg.split()
            cmd = parts[0]

            if len(parts) == 2:
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
                group = group[:-3]

            if len(parts) == 1:
                data = ''
                fullpath = '{}{}'.format(self.dir_fits, group)
                for root, dirs, files in os.walk(fullpath):
                    for fname in files:
                        data = "{}\n{}".format(data, fname)
                data = data[1:]
                if len(data) and len(parts) == 2:
                    await bot.say("<@{}> Loadable {} fits:\n{}".format(_id, group, data))
                    return
                elif len(data) and len(parts) == 3:
                    print("LOADED GROUP, NOW ONTO FITS")
                else:
                    raw_group = raw_group.lower()
                    for root, dirs, files in os.walk(self.dir_fits):
                        for d in dirs:
                            if raw_group == d.lower():
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
                            for fname in files:
                                data = "{}\n{}".format(data, fname)
                        data = data[1:]
                        if len(data) and len(parts) == 2:
                            await bot.say("<@{}> Loadable {} fits:\n{}".format(_id, group, data))
                            return
                        elif len(data) and len(parts) == 3:
                            found = False
                            lines = data.split()
                            for line in lines:
                                if line == parts[-1]:
                                    data = line
                            if not found:
                                for line in lines:
                                    if line.startswith(parts[-1]):
                                        data = line
                    else:
                        await bot.say("<@{}> No {} fits found.".format(_id, group))
                        return

            if len(parts) >= 3:
                filename = self.fix_filename(data)
                if not len(filename):
                    return

                lookup = '' # preload in case of get_fit failure

                fullpath = '{}{}/{}'.format(self.dir_fits, group, filename)
                if not os.path.isfile(fullpath):
                    with open(fullpath,'r') as f:
                        data = f.read(4096).strip()
                        ship, table, lookup = self.get_fit(data)

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
                                break
                            else:
                                pass
                        if found:
                            break
                    if found:
                        fullpath = '{}{}/{}'.format(self.dir_fits, group, filename)
                        with open(fullpath,'r') as f:
                            data = f.read(4096).strip()
                            #print(data)

                    else:
                        await bot.say("<@{}> Can't find that {} fit, try again.".format(_id, group))
                        return

                if len(lookup):
                    url = "https://api.eve-marketdata.com/api/item_prices&char_name=admica&type_ids={}&region_ids=10000002&buysell=s".format(lookup[:-1])
                    print(url)

                    try:
                        async with aiohttp.ClientSession() as session:
                            raw_response = await session.get(url)
                            response = await raw_response.text()
                            raw = response.replace('null','None').replace('true','True').replace('false','False')
                    except:
                        await asyncio.sleep(0.5)
                        async with aiohttp.ClientSession() as session:
                            raw_response = await session.get(url)
                            response = await raw_response.text()
                            raw = response.replace('null','None').replace('true','True').replace('false','False')
                            flag_yes = True

                    if flag_yes:     

                        total, outp = self.parse_xml(_id, ship, table, raw)
                        if total:
                            await bot.say(outp)

                else:
                    print("WARNING: ###############################################")
                    print("WARNING: Didn't find anything to lookup, skipping lookup.")
                    print("WARNING: ###############################################")

                await bot.say("<@{}> {}{}/{}".format(_id, self.dir_fits[3:], group, data))

                return

            await bot.say("<@{}> I'm sorry Dave, I can't allow you to do that.".format(_id))
            return


        @bot.command(pass_context=True)
        async def route(ctx):
            """Show the routes from one system to another.
------------------------------
DESCRIPTION: Route planning, from source to destination shows each hop.
Shortest path is default, but you can specify secure/high or insecure/low/null.
------------------------------
FORMAT: #route <source> <destination> [routing]
------------------------------
EXAMPLE: #route jita vlil
  12 jumps using shortest routing.
  Jita > Ikuchi > Tunttaras > Nourvukaiken > Tama > Kedama > Hirri > Pynekastoh > Hikkoken > Nennamaila > Aldranette > Vlillirier"""
            _id = ctx.message.author.id

            parts = ctx.message.content.split()
            if len(parts) == 4:
                sort = parts[3].lower()
                if sort in ['shortest','secure','insecure']:
                    sort = parts[3].lower()
                elif sort.startswith('sh'):
                    sort = 'shortest'
                elif sort.startswith('sec'):
                    sort = 'secure'
                elif sort.startswith('hi'):
                    sort = 'secure'
                elif sort.startswith('in'):
                    sort = 'insecure'
                elif sort.startswith('lo'):
                    sort = 'insecure'
                elif sort.startswith('nu'):
                    sort = 'insecure'
                elif sort.startswith('ze'):
                    sort = 'insecure'
                else:
                    sort = 'shortest'
            else:
                sort = 'shortest'

            if len(parts) < 5:
                await bot.say('<@{}> Give me a source and destination system, ex. #route jita akora'.format(_id))
                return

            src = []
            for system_id, d in self.systems.items():
                if parts[1].lower() == d['name'].lower():
                    src.append( [d['name'], d['system_id']] )
                    break
            if len(src) < 1:
                for system_id, d in self.systems.items():
                    if d['name'].lower().startswith(parts[1].lower()):
                        src.append( [d['name'], d['system_id']] )
                        break
            if len(src) < 1:
                await bot.say("<@{}> Starting system '{}' not found.".format(_id, parts[1]))
                return

            dst = []
            for system_id, d in self.systems.items():
                if parts[2].lower() == d['name'].lower():
                    dst.append( [d['name'], d['system_id']] )
                    break
            if len(dst) < 2:
                for system_id, d in self.systems.items():
                    if d['name'].lower().startswith(parts[2].lower()): 
                        break
            if len(dst) < 1:
                await bot.say("<@{}> Starting system found, but destination '{}' was not found.".format(_id, parts[1]))
                return

            url = 'https://esi.evetech.net/latest/route/{}/{}/?flag={}'.format(src[0][1], dst[0][1], sort)
            print(url)

            try:
                flag_yes = False
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(url)
                    response = await raw_response.text()
                    flag_yes = True
            except:
                await asyncio.sleep(0.5)
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(url)
                    response = await raw_response.text()
                    response = eval(response)
                    flag_yes = True

            if flag_yes:

                data = '<@{}> {} jumps using {} routing.```css\n'.format(_id, len(response), sort)
                route = ''
                for _sys in response:
                    for system_id, d in self.systems.items():
                        if _sys == d['system_id']:
                            sec = str(round(d['security_status'],1))
                            if sec[0:2] == '0.':
                                sec = sec[1:]
                            route += '{}({}) > '.format(d['name'], sec)
                            return
                route = route[:-3]
                data += route
                data += '```'
                await bot.say(data)


        @bot.command(pass_context=True)
        async def map(ctx):
            """Fetch a dotlan map for any region.
------------------------------
DESCRIPTION: Retreive dotlan map link highlighting recent jumps.
------------------------------
FORMAT: #map <region>
------------------------------
EXAMPLE: #map the for
  http://evemaps.dotlan.net/map/the_forge#jumps"""
            _id = ctx.message.author.id
            #http://evemaps.dotlan.net/map/Tribute/M-OEE8#jumps
            url = 'http://evemaps.dotlan.net/map/'
            try:
                name = ctx.message.content
                if len(name) > 2:
                    name = '_'.join(name)
                elif len(name) == 2:
                    name = name[1]
                else:
                    await bot.say("<@{}> **Which region?** (partial match ok)```{}```".format(_id, ', '.join(self.regionslist)))
                    return

                #print('Processing map request for {}'.format(name))
                found = False
                for region in self.regionslist:
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
                    elif name in ['forge', 'the']:
                        name = 'the_forge'
                    elif name in ['great','wildlands','wild','wildland','wlid']:
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
                        for region in self.regionslist:
                            print("checking {} = {}".format(name,region.lower()))
                            if region.lower().startswith(name):
                                name = region
                                found = True
                                break
                if found:
                    url = '<{}{}#jumps>'.format(url, name)
                    print('Sending link: {}'.format(url))
                    await bot.say("<@{} {}".format(_id, url))
                else:
                    await bot.say("<@{}> No match found. **Which region?** (partial match ok)```{}```".format(_id, ', '.join(self.regionslist)))


            except ZeroDivisionError:#Exception as e:
                print("Map failure: {}".format(e))
                try:
                    await bot.say("<@{}> Hmm, something went wrong.".format(_id))
                except Exception as e:
                    self.do_restart()


        @bot.command(pass_context=True)
        async def get_auth(ctx):
            """get the auth url needed for accessing assets"""
            _id = ctx.message.author.id
            url = 'https://login.eveonline.com/oauth/authorize?response_type=token&redirect_uri=https://localhost/callback&client_id=baaf8fc216864da297227ba80c57f445&scope=publicData+esi-assets.read_assets.v1'
            await bot.say('<@{}> Sign in URL: {}'.format(_id, url))

            the_id = self.people.get(_id, None)

            if the_id is None:
                the_token = None
                the_token = self.people[_id].get('token', 'None')
                the_char = self.people[_id].get('char', 'None')
                the_char = self.people[_id].get('char_id', 'None')
                the_expires = self.people[_id].get('expires', 'None')

            if the_id is None or the_token == 'None':
                await bot.say('<@{}> No token set. Please sign in with the above url, then use #set_auth and tell me the URL you are redirected to after signing in, and I will extract the authorization token, or you can extract the token from the url and tell me just the token part.'.format(_id))
                return

                if the_expires != 'None':
                    the_expires = str(self.people[_id]['expires'])[:-10]
                    time_left = ( self.people[_id]['expires'] - datetime.utcnow() ).seconds
                    if time_left > 1234 or time_left < 1:
                        time_left = "Expired"
                    else:
                        time_left = '{:.1f} min'.format(time_left / 60.0)

                data = '<@{}> Auth Info:```css\n'.format(_id)
                data += 'Character: {}\n'.format(the_char)
                data += 'Character ID: {}\n'.format(self.people[_id]['char_id'])
                data += 'Token: {}\n'.format(the_token)
                data += 'Token expires: {} {}```'.format(time_left, the_expires)
                await bot.say(data)


        @bot.command(pass_context=True)
        async def set_auth(ctx):
            """set the authorization token for access to assets"""
            _id = ctx.message.author.id
            parts = ctx.message.content.split()

            try:
                if len(parts) > 1 and parts[1].startswith('https://localhost/callback#access_token='):
                    token = parts[1].split('#access_token=')[-1]
                    token = token.split('&token_type')[0]

                elif len(parts) > 1 and len(parts[1]) > 55:
                    token = parts[1]
                else:
                    await bot.say('<@{}> Use #get_auth to get the authorization url, sign in, then tell me the URL you are redirected to after signing in, and I will extract the authorization token, or you can extract the token from the url and tell me just the token part.'.format(_id))
                    return

                if self.people.get(_id, None) is None:
                    self.people[_id] = {}
                    self.people[_id]['id'] = _id

                the_char = self.people[_id].get('char', 'None')
                the_char_id = self.people[_id].get('char_id', 'None')
                self.people[_id]['token'] = token
                self.people[_id]['expires'] = datetime.utcnow() + timedelta(minutes=99)

                data = '<@{}> Token received.```css\n'.format(_id)
                data += 'Character: {}\n'.format(the_char)
                data += 'Character ID: {}\n'.format(the_char_id)
                data += 'Token: {}\n'.format(self.people[_id]['token'])
                data += 'Token expires: 20 min ({})```'.format(str(self.people[_id]['expires'])[:-10])

                # save
                with open('people.pickle', 'wb') as f:
                    pickle.dump(self.people, f, protocol=pickle.HIGHEST_PROTOCOL)

                await bot.say(data)

            except Exception as e:
                print("X"*42)
                print(e)
                print("X"*42)
                await bot.say("<@{}> That doesn't look like the returned URL or token to me.".format(_id))
                await asyncio.sleep(0.25)


        @bot.command(pass_context=True)
        async def set_char(ctx):
            """Set your character name to pair with access to assets"""
            _id = ctx.message.author.id
            parts = ctx.message.content.split()

            if self.people.get(_id, None) is None:
                self.people[_id] = {}
                self.people[_id]['id'] = _id

            self.people[_id]['char'] = ' '.join(parts[1:])
            await bot.say("<@{}> Searching for '{}', please wait...".format(_id, self.people[_id]['char']))
            await asyncio.sleep(0.25)

            flag_fail = False
            url = 'https://esi.evetech.net/latest/search/?categories=character&strict=true&search={}'.format(self.people[_id]['char'].replace(' ','%20'))
            print(url)
            async with aiohttp.ClientSession() as session:
                raw_response = await session.get(url)
                print("RESPONSE=[{}]END_RESPONSE".format(response))
                d = eval(response)
                try:
                    if d.get('character', None) is None:
                        flag_fail = True
                except:
                    try:
                        the_char_id = d['character']
                    except:
                        flag_fail = True

            if flag_fail:
                self.people[_id]['char'] = 'None'
                the_char_id = 'None'

            self.people[_id]['char_id'] = the_char_id

            the_token = self.people[_id].get('token', 'None')
            the_expires = self.people[_id].get('expires', 'None')
            if the_token == 'None' or the_expires == 'None':
                time_left = "Expired"
            if the_expires != 'None':
                time_left = ( self.people[_id]['expires'] - datetime.utcnow() ).seconds
                if time_left > 1234 or time_left < 1:
                    time_left = "Expired"
                else:
                    time_left = '{:.1f} min'.format(time_left / 60.0)

            if flag_fail:
                data = "<@{}> Invalid character name! Did you spell it correctly?```css\n".format(_id)
            else:
                data = "<@{}> Character name set to: '{}'```css\n".format(_id, self.people[_id]['char'])

                # save
                with open('people.pickle', 'wb') as f:
                    pickle.dump(self.people, f, protocol=pickle.HIGHEST_PROTOCOL)

            data += 'Character: {}\n'.format(self.people[_id]['char'])
            data += 'Character ID: {}\n'.format(self.people[_id]['char_id'])
            data += 'Token: {}\n'.format(the_token)
            data += 'Token expires: {} ({})```'.format(time_left, the_expires)
            await bot.say(data)

            #"""show your items sorted by market competition"""


        @bot.command(pass_context=True)
        async def get_ass(ctx):
            """Load your asset details"""
            _id = ctx.message.author.id
            parts = ctx.message.content.split()

            ret = self.check_auth(_id)
            if ret is not True:
                await bot.say(ret)
                return
            the_char = self.people[_id].get('char', 'None')
            the_expires = self.people[_id].get('expires', 'None')

            url = "https://esi.evetech.net/latest/characters/{}/assets/?datasource=tranquility&page=1&token={}".format(the_char_id, the_token)
            print(url)

            r = requests.get(url)
            last_page = int(r.headers['X-Pages']) # last page number in header
            if r.status_code == 200:
                await bot.say('<@{}> HTTP Status code "{}" is not 200, try again in a minute.'.format(_id, r.status_code))
                return
            else:
                await bot.say('<@{}> Fetching {} pages of assets, please wait.'.format(_id, last_page))

            assets = {}
            uniq_items = {}

            for page in range(5, last_page+1):

                url = "https://esi.evetech.net/latest/characters/{}/assets/?datasource=tranquility&page={}&token={}".format(the_char_id, page, the_token)
                print(url)

                async with aiohttp.ClientSession() as session:
                    await asyncio.sleep(0.77)
                    raw_response = await session.get(url)
                    response = await raw_response.text()
                    print("RESPONSE=[{}]END_RESPONSE".format(response))
                    l = eval(response.replace('null','None').replace('true','True').replace('false','false'))

                    try:
                        error = l.get('error',None)
                        if error:
                            await bot.say('<@{}> Token appears invalid or expired. Check with #get_auth'.format(_id))
                    except:
                        pass # normal behavior

                    n = len(l) # list of dictionaries
                    # {"is_singleton":false,"item_id":102774901,"location_flag":"Hangar","location_id":60001393,"location_type":"station","quantity":3,"type_id":14019}
                    # {"is_singleton":false,"item_id":106339446,"location_flag":"Hangar","location_id":60003898,"location_type":"station","quantity":1,"type_id":5493}
                    # {"is_singleton":false,"item_id":109387381,"location_flag":"Hangar","location_id":60008455,"location_type":"station","quantity":1,"type_id":490}

                    await bot.say("<@{}> Parsing page #{} with {} assets, please wait...".format(_id, page, n))

                    for d in l:
                        if d['type_id'] in uniq_items:
                            uniq_items[d['type_id']]['quantity'] += d['quantity']
                        else:
                            uniq_items[d['type_id']] = d

                    for d in uniq_items.values():
                        loc = d.get('location_type', None)
                        if loc == 'station':
                            for sys_id in self.systems:
                                if self.systems[sys_id].get('stations', None):
                                    for stat_id in self.systems[sys_id]['stations']:
                                        try:
                                            if d['location_id'] == stat_id:
                                                item_name = self.items.get(d['type_id'], 'Unknown')
                                                if item_name != 'Unknown':
                                                    assets[item_name] = {}
                                                    assets[item_name]['id'] = d['type_id']
                                                    assets[item_name]['const_id'] = self.systems[sys_id]['constellation_id']
                                                    assets[item_name]['sys_name'] = self.systems[sys_id]['name']
                                                    assets[item_name]['sys_id'] = sys_id

                                                flag_found = True
                                                break
                                        except Exception as e:
                                            print("Error: {}".format(e))
                                if flag_found:
                                    break 

                # my assets
                self.people[_id]['assets'] = assets

                # save last lookup for debug
                with open('assets.pickle', 'wb') as f:
                    pickle.dump(assets, f, protocol=pickle.HIGHEST_PROTOCOL)

                # save
                with open('people.pickle', 'wb') as f:
                    pickle.dump(self.people, f, protocol=pickle.HIGHEST_PROTOCOL)

            data = "<@{}> Done.".format(_id)
            await bot.say(data)


        @bot.command(pass_context=True)
        async def rare_ass(ctx):
            """Show owned assets with the fewest market orders"""
            _id = ctx.message.author.id
            msg = ctx.message.content
            parts = msg.split()

            flag_num = False
            if len(parts) > 1:
                try:
                    num = int(parts[1])
                    if num > 40:
                        num = 40
                    flag_num = True
                except:
                    num = 20
            else:
                num = 20

            partial = None
            if not flag_num:
                if len(parts) > 3:
                    try:
                        partial = ' '.join(parts[1:]).lower()
                    except Exception as e:
                        print(e)
                        pass
            print("parts",parts)
            print('num',num)
            print('partial',partial)

            data = "<@{}> Sorting assets number of market sell orders.```css\n".format(_id)

            assets_copy = self.people[_ids]['assets'].copy()
            for ass_id, ass in assets_copy.items():

                #print(' * ',self.items[ass['id']])
                count = 0
                quant = 0
                _max = 0

                if ass['id'] in self.market_sells:
                    for order in self.market_sells[ass['id']]:
                        if not order['is_buy_order']: # this is a sell order
                            count += 1
                            quant += order['volume_remain']
                            if order['price'] > _max:
                                _max = order['price']

                    name = self.market_sells[ass['id']][0]['name']
                    self.people[_id]['assets'][name]['sell'] = _maxs
                    self.people[_id]['assets'][name]['count'] = counts
                    self.people[_id]['assets'][name]['quant'] = quants

                else:
                    self.people[_id]['assets'][self.items[ass['id']]]['sell'] = 0
                    self.people[_id]['assets'][self.items[ass['id']]]['count'] = 0
                    self.people[_id]['assets'][self.items[ass['id']]]['quant'] = 0

            from collections import OrderedDict
            od = OrderedDict(sorted(self.people[_id]['assets'].items(), key=lambda x: x[1]['count'], reverse=False))

            count = 0
            for k,v in od.items():
                if partial is None or partial in k.lower():
                    data += '{}: {} orders, #{}, {:,.2f} ISK: {}\n'.format(k, v['count'], v['quant'], v['sell'], v['sys_name'])
                    count += 1
                    if count > num-1:
                        break

            # save
            with open('people.pickle', 'wb') as f:
                pickle.dump(self.people, f, protocol=pickle.HIGHEST_PROTOCOL)

            data += '```' # end
            await bot.say(data)


        @bot.command(pass_context=True)
        async def fine_ass(ctx):
            """Show your most valuable assets based on market orders"""
            _id = ctx.message.author.id
            await bot.say("<@{}> Sorting your assets, please wait...".format(_id))

            if self.people.get(_id, 'None') == 'None':
                ret = self.check_auth(_id)
                if ret is not True:
                    await bot.say(ret)
                    return

            msg = ctx.message.content
            parts = msg.split()
            flag_num == False
            if len(parts) > 1:
                try:
                    num = int(parts[1])
                    if num > 40:
                        num = 40
                    flag_num = True
                except:
                    num = 20
            else:
                num = 20

            partial = None
            if not flag_num:
                if len(arts) > 1:
                    try:
                        partial = ' '.join(parts[1:]).lower()
                    except:
                        pass

            data = "<@{}> {}'s {} most valuable assets based on market sell orders:```css\n".format(_id, self.people[_id]['char'], num)

            assets_copy = self.people[_id]['assets'].copy()
            for ass_id, ass in assets_copy.items():

                print(self.items[ass['id']])
                _max = 0
                _min = '' # to force type error on first try
                if ass['id'] in self.market_sells:
                    for order in self.market_sells[ass['id']]:
                        if order['price'] > _max:
                            _max = order['price']
                        #else:
                        #    try:
                        #        if order['price'] < _min:
                        #            _min = order['price']
                        #    except TypeError:
                        #        _min = order['price']

                    name = self.market_sells[ass['id']][0]['name']
                    self.people[_id]['assets'][name]['sell'] = _max
                else:
                    self.people[_id]['assets'][self.items[ass['id']]]['sell'] = 0

            from collections import OrderedDict
            od = OrderedDict(sorted(self.people[_id]['assets'].items(), key=lambda x: x[1]['sell'], reverse=True))

            count = 0
            for k,v in items():
                if partial is None or partial in k.lower():
                    data += '{}: {:,.2f} ISK x {}: {}\n'.format(k, v['sell'], v['q'], v['sys_name'])
                    count += 1
                    if count > num-1:
                        break

            data += '```' # end
            await bot.say(data)


        @bot.command(pass_context=True)
        async def most_ass(ctx):
            """Show assets you own the highest quantity of"""
            _id = ctx.message.author.id
            msg = ctx.message.content
            parts = msg.split()

            flag_num = False
            if len(parts) > 1:
                try:
                    num = int(parts[1])
                    if num > 40:
                        num = 40
                    flag_num = True
                except:
                    num = 20
            else:
                num = 20

            partial = None
            if not flag_nums:
                if len(parts) > 1:
                    try:
                        partial = ' '.join(parts[1:]).lower()
                    except:
                        pass

            from collections import OrderedDict
            od = OrderedDict(sorted(self.people[_id]['assets'].items(), key=lambda x: x[1]['q'], reverse=True))
            data = "<@{}> {}'s top {} items by quantity:```css\n".format(_id, self.people[_id]['char'], num)

            count = 1
            for k,v in od.items():
                if partial is None or partial in k.lower():
                    data += '{}: #{}: {}\n'.format(k, v['q'], v['sys_name'])
                    self.count += 1
                    if count > num:
                        break
            data += '```'

            print(data)
            await bot.say(data)


        @bot.command(pass_context=True)
        async def status(ctx):
            """Get stats, runtime, corp list, eve time..."""
            try:
                _id = ctx.message.author.id
                x = []
                while not self.qthread.empty():
                    x.append(self.qthread.get_nowait())
                if not len(x):
                    x = [self.last]

                print("last: {}".format(self.last))
                now = datetime.now()
                dt = str(now - self.dt_last)[:-99]
                self.dt_last = datetime.now()

                data = "<@{}> ```Killmails post to channel: {}\n".format(_id, self.ch['main']['name'])

                diff = x - self.last
                if not self.flag_first_count:
                    data += "{} kills since last status check {} ago.\n".format(diff, dt)
                else:
                    self.flag_first_count = False

                if self.last < 0:
                    self.last = 0
                else:
                    self.last = x

                data += "{} kills since last restart at {}\n".format(x, str(self.date_start)[:-7])

                corps = []
                count = 0
                with open('the.corps','r') as f:
                    for line in f.readlines():
                        corps.append(line.strip().split(":")[0])
                        count += 1
                corps = ', '.join(corps)
                data += "Watching kills/losses for {} corps: {}\n".format(count, corps)

                if self.pause:
                    data += "Killmail posting is currently paused. :pause_button:>\n"

                try:
                    start = str(self.date_start)[:98]
                except:
                    start = 'Unknown'
                try:
                    t = str(datetime.now()-self.date_start)[:-7]
                except:
                    t = 'Unknown'

                if self.sound_on:
                    print(type(self.sound_volume))
                    print(str(self.sound_volume))
                    print(float(self.sound_volume))
                    data += "Sound effects are On, volume at {}%\n".format(int(self.sound_volume*100))
                else:
                    data += "Sound effects are Off.\n"

                data += "Bot runtime: {} (Started {})\n".format(t, start)
                data += "EVE Time is {}```".format(str(datetime.utcnow())[:-77].split(' ')[-1])

                await bot.say(d)

            except Exception as e:
                print("ERROR in status: {}".format(e))
                try: 
                    await bot.say("<@{}> Error in status.".format(_id))
                except Exception as e:
                    self.do_restart()

        '''
        @bot.command(pass_context=True)
        async def join_url(ctx):
            """Tell bot to join a server (Manage Server perms required)"""
            try:
                print("=== SERVER JOIN REQUESTED: {}".format(ctx.message.content))
                if str(ctx.message.author) not in admins:
                    await bot.say("<@{}> Sorry, you are not an admin.".format(_id))
                    return
    
                url = ctx.message.content.split()[-1]
                print("=== JOINING SERVER: {}".format(url))

                invite = bot.get_invite(url)
                print("=== JOINING INVITE: {}".format(invite))

                await bot.accept_invite( invite )
                print("=== JOINED.")

            except Exception as e:
                print("ERROR in join_url: {}".format(e))
                try:
                    await bot.say("<@{}> Error in join_url.".format(_id))
                except Exception as e:
                    self.do_restart()
        '''

        '''
        @bot.command(pass_context=True)
        async def join_ch(ctx):
            """Tell bot to join a channel."""
            try:
                print("--- CHANNEL JOIN REQUESTED: {}".format(ctx.message.content))
                if ctx.message.author:
                    return
                if str(ctx.message.author) not in admins:
                    await bot.say("<@{}> Sorry, you are not an admin.".format(_id))
                    return
                _id = ctx.message.author.id
                parts = ctx.message.content.split()
                cid = parts[-1]
                if len(parts) == 3:
                    if 'voi' in parts[1].lower(): # voice channel
                        await bot.say("<@{}> Joining voice channel {}".format(_id, cid))
                        await bot.join_voice_channel( bot.get_channel(cid) )
                        await bot.say("<@{}> Joined {}".format(_id, cid))
                        return

                elif len(parts) != 2:
                    await bot.say("<@{}> Invalid request, try #help join_ch".format(_id))
                    return

                await bot.say("<@{}> Joining channel {}".format(_id, cid))
                await bot.join_channel(_id)
                await bot.say("<@{}> Joined {}".format(_id, cid))

            except Exception as e:
                print("ERROR in join_ch: {}".format(e))
                try:
                    await bot.say("<@{}> Error in join_ch.".format(_id))
                except Exception as e:
                    self.do_restart()
        '''

        '''
        @bot.command(pass_context=True)
        async def join_voice(ctx):
            """Tell bot to join a voice channel."""
            try:
                print("--- VOICE CHANNEL JOIN REQUESTED: {}".format(ctx.message.content))
                if str(self.tx.message.author) not in admins:
                    await bot.say("<@{}> Sorry, you are not an admin.".format(_id))
                    return

            except Exception as e:
                print("ERROR in join_voice: {}".format(e))
                try:
                    await bot.say("<@{}> Error in join_voice.".format(_id))
                except Exception as e:
                    self.do_restart()
        '''

        @bot.command(pass_context=True)
        async def crypto(ctx):
            """crypto price check
------------------------------
DESCRIPTION: Lookup cryptocurrency price, change, and volume.
------------------------------
FORMAT: #crypto <currency>
------------------------------
EXAMPLE: #crypto iota
  IOTA price: $0.7654222581
  IOTA change last 1h:  -3.93%
  IOTA change last 24h: -10.7%
  IOTA volume last 24h: $123,857,230.30"""
            _id = ctx.message.author.id
            msg = ctx.message.content
            coin = msg.split()
            url = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(coin)
            try:
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(url)
                    response = await raw_response.text()
                    response = eval(response)[0]
                    data = '```{} price: ${}\n'.format(coin.upper(), response['price_usd'])
                    data += '{} change last 1h:  {}%\n'.format(coin.upper(), response['percent_change_1h'])
                    data += '{} change last 24h: {}%\n'.format(coin.upper(), response['percent_change_24h'])
                    try:
                        vol = '{:,.2f}'.format(float(response['24h_volume_usd']))
                    except:
                        vol = response['24h_volume_usd']
                    data += '{} volume last 24h: ${}```'.format(coin.upper(), vols)
                    await bot.say('<@{}> {}'.format(_id, data))

            except Exception as e:
                print("<@{}> Error in price command: {}".format(_id, e))
                await bot.say("<@{}> Sorry, I don't know how to lookup {}.".format(_id, coin))

        '''
        @bot.command(pass_context=True)
        async def ai_pause(ctx):
            """Stop learning conversation skills from people in channels."""
            try:
                if not self.pause_train:
                    self.pause_train = True
                    await bot.say("<@{}> :pause_button: ***Ignoring all conversations.***".format(ctx.message.author.id))
                else:
                    await bot.say("<@{}> Already paused.".format(ctx.message.author.id))
            except Exception as e:
                print("FATAL in pause_train: {}".format(e))
                self.do_restart()


        @bot.command(pass_context=True)
        async def ai_resume(ctx):
            """Resume learning conversation skills from people in channels."""
            try:
                if self.pause_train:
                    self.pause_train == False
                    for v in self.chtrain.values():
                        v['pair'] = []

                    await bot.say("<@{}> :bacon: ***Learning from conversations resumed.***".format(ctx.message.author.id))
                else:
                    await bot.say("<@{}> Not paused.".format(ctx.message.author.id))
            except Exception as e:
                print("FATAL in resume_train: {}".format(e))
                self.do_restart()
        '''

        @bot.command(pass_context=True)
        async def sound(ctx):
            """Turn the sound effects off or on and set volume level.
------------------------------
DESCRIPTION: Get the current state of sound effects.
Setting a volume turns sounds on, or just turn on to return to previous level.
------------------------------
FORMAT: #sound [on|off|vol%]
------------------------------
EXAMPLE: #sound
  Sound effects are turned off.
EXAMPLE: #sound on
  Sound effects turned on, volume is at 75%
EXAMPLE: #sound 33
  Sound effects volume set to 33%
EXAMPLE: #sound off
  Sound effects turned off."""
            _id = ctx.message.author.id
            parts = ctx.message.content.split()
            x = parts[-1].lower()

            if len(parts) != '2':
                if self.sound_on:
                    await bot.say("<@{}> Sound effects are on at {}%".format(_id, int(self.sound_volume*100)))
                else:
                    await bot.say("<@{}> Sound effects are turned off.".format(_id))
                return

            if str(ctx.message.author) not in admins:
                await bot.say("<@{}> You are not an admin, ignoring command.".format(_id))
                return

            if x.startswith('of'):
                self.sound_on = False
                await bot.say("<@{}> Sound effects turned off.".format(_id))
            elif x.startswith('zer'):
                self.sound_on = False
                await bot.say("<@{}> Sound effects turned off.".format(_id))
            elif x.startswith('of'):
                self.sound_on = False
                await bot.say("<@{}> Sound effects turned off.".format(_id))

            elif x.startswith('on'):
                self.sound_on = True
                await bot.say("<@{}> Sound effects turned on, volume is at {}%".format(_id, int(self.sound_volume*100)))
            elif x.startswith('y'):
                self.sound_on = True
                await bot.say("<@{}> Sound effects turned on, volume is at {}%".format(_id, int(self.sound_volume*100)))
            else:
                try:
                    self.sound_on = True
                    self.sound_volume = abs(float(x))

                    if self.sound_volume > 1.0:
                        if self.sound_volume > 100:
                            self.sound_volume = 1.0
                        else:
                            self.sound_volume = float(self.sound_volume / 100.0)
                    await bot.say("<@{}> Sound effects volume set to {}%".format(_id, int(self.sound_volume*100)))

                except Exception as e:
                    print("FAILURE in sound: {}".format(e))
                    self.do_restart()


        @bot.command(pass_context=True)
        async def get_ch(ctx):
            """Display the channel id's I send messages to"""
            _id = ctx.message.author.id
            for key in self.ch:
                await bot.say("<@{}> {}: [{}] id: {}".format(_id, key, self.ch[key]['name'], self.ch[key]['id']))

        @bot.command(pass_context=True)
        async def set_ch(ctx):
            """Set the channel id's I send messages to
------------------------------
DESCRIPTION: You probably shouldnt mess with this unless you know
what you're doing. Key is an internal identifier, name is channel name.
Use the get_ch command for the list of all available keys.
------------------------------
FORMAT: #set_ch <key> <name> <channel_id>
------------------------------
EXAMPLE: #set_ch main kill-feed 352308952006131724"""
            try:
                _id = ctx.message.author.id
                if str(ctx.message.author) in admins:
                    msg = ctx.message.content.split()
                    if len(msg) == 4:
                        key, name, channel_id = msg
                        if key in self.ch:
                            try:
                                key = self.fix_filename(key)
                                name = self.fix_filename(name)
                                channel_id = self.fix_filename(channel_id)
                                with open('the.channel_{}'.format(key),'w') as f:
                                    f.write("{}:{}\n".format(name, channel_id))
                                    self.ch[key]['name'] = name
                                    self.ch[key]['id'] = channel_id
                                    await bot.say("<@{}> {} output channel set to {} id: {}".format(_id, key, name, channel_id))
                            except Exception as e:
                                await bot.say("<@{}> Failed to set {} output channel.".format(_id, keys))
                        else:
                            await bot.say("<@{}> {} is an invalid key.".format(_id, keys))
                    else:
                        await bot.say("<@{}> Usage: {} <key> <name> <channel_id>".format(_id, msg[0]))
                else:
                    await bot.say("<@{}> You are not an admin, ignoring command.".format(_id))
                    
            except Exception as e:
                print("ERROR in set_channel: {}".format(e))

        '''
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
        '''

        @bot.command(pass_context=True)
        async def die(ctx):
            """Tell bot to logoff. (permissions required)"""
            _id = ctx.message.author.id
            if str(ctx.message.author) in admins:
                await bot.say("<@{}> Shutting down.".format(_id))
                await bot.logout()
                self.running = False
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
            self.q.put_nowait([event, message, _id, channel])
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
                _url = 'wss://zkillboard.com:2092'
                _msg = '{"action":"sub","channel":"killstream"}'
                ws = websocket.create_connection(_url)
                print('Main Connected to: {}'.format(_url))
                ws.send(_msg)
                print('Main Subscribed with: {}'.format(_msg))

                inject = None
                try:
                    inject = pickle.load(open(REDO,'rb')) # previous work ready for injection
                    os.remove(REDO)
                    print("INJECTION LOADED")
                except:
                    pass

                self.running = True
                while self.running:
                    time.sleep(11.11)
                    if self.Bot._is_ready.is_set():
                        while True:
                            try:
                                time.sleep(0.15)
                                if inject is None:
                                    raw = ws.recv()
                                else:
                                    print("injected raw")
                                    raw = inject
                                    inject = None # reset to avoid looping here

                                d = json.loads(raw)
                                url = d['zkb']['url']

                                try:
                                    system = self.systems[d['solar_system_id']]['name']
                                except Exception as e:
                                    print("CANT FIGURE OUT SYSTEM NAME FOR KILLMAIL")
                                    print(e)
                                    system = 'Unknown'

                                subj = '---'
                                post = 0
                                for attacker in d['attackers']:
                                    c = attacker.get('corporation_id','none')
                                    if str(c) in self.corp:
                                        ship = d['victim'].get('ship_type_id', 'Unknown')
                                        try:
                                            ship = self.items[ship]
                                        except Exception as e:
                                            print("ERR1:{}".format(e))
                                            pass
                                        subj = '`Kill:`**{}** ***{}***'.format(system, ship)
                                        post = 1
                                        break

                                killers = 0
                                killers_total = 0
                                for attacker in d['attackers']:
                                    c = attacker.get('corporation_id','none')
                                    killers_total += 1
                                    if str(c) in corps:
                                        killers += 1

                                if post == 0: # no attackers involved
                                    c = d['victim'].get('corporation_id', 'none')
                                    if str(c) in self.corps:
                                        ship = d['victim'].get('ship_type_id', 'Unknown')
                                        try:
                                            ship = self.items[ship]
                                        except Exception as e:
                                            print("ERR2:{}".format(e))
                                            pass
                                        subj = '`Loss:`**{}** ***{}***'.format(system, ship)
                                        post = 5

                                if post == 0: # no attackers or victims involved
                                    for wname, wd in self.watch.items():
                                        if wd['id'] == d['solar_system_id']:
                                            ship = d['victim'].get('ship_type_id', 'Unknown')
                                            try:
                                                ship = self.items[ship]
                                            except Exception as e:
                                                print("ERR3:{}".format(e))
                                                pass
                                            subj = '`Watch:`**{}** ***{}***'.format(system, ship)
                                            post = 3
                                            break

                                self.count += 1
                                self.incr() # handle counter queue

                                p1 = d['victim']['position']

                                near = 'Deep Safe'
                                dist = 4e+13
                                for gate_id in self.systems[d['solar_system_id']].get('stargates', []):
                                    dis = distance(p1, self.stargates[gate_id]['position'])
                                    #print(gate_id, self.stargates[gate_id])
                                    if dis < dist:
                                        dist = dis
                                        near = self.stargates[gate_id]['name']
                                    for std in self.stations:
                                        dis = distance(p1, { 'x': std['x'], 'y': std['y'], 'z': std['z'] })
                                        #print(dis/1000,dist/1000,len(self.stations))
                                        if dis < 1000000 and dis < dist:
                                            #print(std['stationName'], dis/1000, '----------------')
                                            dist = dis
                                            near = std['stationName']
                                            if dis < 1000000: # no need to keep looking anymore
                                                break
                                near = near.replace('Stargate (','').replace(')','')

                                if dist == 4e+13:
                                    x = ''
                                elif dist > 1.495e+9: # 0.01AU
                                    x = '{:.1f}AU from {} '.format((dist/1.496e+11), near) # 1.496e+11 = 1AU
                                elif dist < 1000000:
                                    x = '*{:.0f}km* from {} '.format((dist/1000), near)
                                else:
                                    x = '{:.0f}km from {} '.format((dist/1000), near)

                                others = killers_total - killers
                                if killers == killers_total:
                                    msg = '{} [{} Friendly] {}<{}>'.format(subj, killers, x, url)
                                else:
                                    msg = '{} [{} Friendly +{}] {}<{}>'.format(subj, killers, others, x, url)

                                #for attacker in d['attackers']:
                                #    c = attacker.get('corporation_id','none')
                                #    if str(c) in self.corps:
                                #        print("-------------")
                                #        print(self.items[attacker['ship_type_id']])
                                #        print(attacker)

                                #post = False ###### STOP POSTING DEBUG
                                print(msg)

                            except ZeroDivisionError:#Exception as e:
                                print('Exception caught: {}'.format(e))
                                time.sleep(1)
                                self.do_restart()

            except KeyboardInterrupt:
                self.running = False

            except Exception as e:
                import sys 
                print(sys.exc_info())
                print("Unknown Error {}".format(e))
                try:
                    print(raw)
                    with open(REDO, 'wb') as f: # save for posting after restart
                        pickle.dump(raw, f, protocol=pickle.HIGHEST_PROTOCOL)
                except:
                    pass

            x = 3
            print('Sleeping {} seconds...'.format(x))
            time.sleep(x)
            print('Restarting...')
            self.do_restart()

    def get_char(self, character_id):
        """lookup character info from ESI"""
        try:
            r = requests.get('{}{}'.format(self.url_characters, character_id))
            d = eval(r.text)
            return d

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
            self.qcounter.put(self.count)

        except Exception as e:
            print("FATAL in incr: {}".format(e))
            self.do_restart()


    def cb_thread(self, cbq_in, cbq_out):
        try:
            #"statement_comparison_function": "chatterbot.comparisons.jaccard_similarity",
            #"statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
            cb = ChatBot('Killbot', trainer='chatterbot.trainers.ChatterBotCorpusTrainer', storage_adapter='chatterbot.storage.SQLStorageAdapter', database='../../database.sqlite3', logic_adapters=[
            {
            "import_path": "chatterbot.logic.BestMatch",
            "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
            "response_selection_method": "chatterbot.response_selection.get_first_response"
            },
            {
            'import_path': 'chatterbot.logic.MathematicalEvaluation',
            'threshold': 0.85
            }
            ])
            #cb.train("chatterbot.corpus.english",
            #        "chatterbot.corpus.english.greetings",
            #        "chatterbot.corpus.english.conversations")
            from chatterbot.trainers import ListTrainer
            cb.set_trainer(ListTrainer)
            print("cb done training.")

            while True:
                data = cbq_in.get()

                if len(data) == 1:
                    response = cb.get_response(data[0])
                    cbq_out.put(response)

                    # learn?
                    #cb.output.process_response(data[0])
                    #cb.conversation_sessions.update(bot.default_session.id_string,(data[0], response,))

                elif len(data) == 2:
                    _in = data[0]
                    _out = data[1]
                    print("TRAINING {} >>> {}".format(_in, _out))
                    cb.train([_in, _out])
                    cbq_out.put("TRAINED")
                else:
                    pass

        except Exception in e:
            print("Epic failure in cbq_thread: {}".format(e))
            time.sleep(15)


    def timer_thread(self, q, chan, debug=False):
        """thread loop runs forever updating status"""
        channel = chan['id']
        self.running = Tru#e
        self.message = 'Calculating...'

        while True:
            try:
                status = 'Unknown'
                online = 'Unknown'
                kills = 'Unknown'
                ready = False

                _url = 'wss://zkillboard.com:2092'
                _msg = '{"action":"sub","channel":"public"}'
                wss = websocket.create_connection(_url)
                print('Timer Thread Connected to: {}'.format(_url))
                wss.send(_msg)
                print('Timer Thread Subscribed with: {}'.format(_msg))

                while self.running:
                    time.sleep(0.1)
                    raw = wss.recv()
                    d = eval(raw)
                    if 'tqStatus' in d:
                        status = d['tqStatus']
                        online = d['tqCount']
                        kills = d['kills']
                    if ready:
                        event = threading.Event()
                        self.message = '#SECRET_STATUP____{} {} {} Kills'.format(online, status, kills)
                        q.put_nowait([event, self.message, channel])
                        event.wait()

                        wss.close()
                        raise ZeroDivisionError # forced raise

                    else:
                        pass
                        #print("Collecting data {} {} {}".format(status, online, kills))

            except Exception as e:
                print("SLEEPING AFTER TIMER_THREAD {}".format(e))
                time.sleep(900)


    def do_restart(self):
        try:
            self.running = False
            os.execv(__file__, sys.argv)
            sys.exit(0)
        except Exception as e:
            print("Failing to restart")
            time.sleep(15)

#############################################################
#############################################################

import time
time.sleep(1)

bot = Zbot()
try:
    bot.start()
    bot.start_timer() # periodic server status update of with pilots online and total kills
    bot.run()
except Exception as e:
    print("FATAILITY IN MAIN: {}".format(e))
    bot.do_restart()

