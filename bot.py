#!/usr/bin/python3
#Discord eve bot by admica

import asyncio, discord, time, threading, websocket, json
from discord.ext import commands
from discord.ext.commands import Bot
import aiohttp
import re
from queue import Queue

class Zbot:
    def __init__(self):
        self.pause = False
        self.count = 0 # global kill counter
        self.qcounter = Queue(maxsize=1) # share counter between main and thread
        self.regions = 'Aridia Black_Rise The_Bleak_Lands Branch Cache Catch The_Citadel Cloud_Ring Cobalt_Edge Curse Deklein Delve Derelik Detorid Devoid Domain Esoteria Essence Etherium_Reach Everyshore Fade Feythabolis The_Forge Fountain Geminate Genesis Great_Wildlands Heimatar Immensea Impass Insmother Kador The_Kalevala_Expanse Khanid Kor-Azor Lonetrek Malpais Metropolis Molden_Heath Oasa Omist Outer_Passage Outer_Ring Paragon_Soul Period_Basis Perrigen_Falls Placid Providence Pure_Blind Querious Scalding_Pass Sinq_Laison Solitude The_Spire Stain Syndicate Tash-Murkon Tenal Tenerifis Tribute Vale_of_the_Silent Venal Verge Vendor Wicked_Creek'.split(' ')

        self.corps = []
        with open('the.corps','r') as f:
            for line in f.readlines():
                self.corps.append(line.strip().split(":")[-1])

        self.ch = {}
        with open('the.channel','r') as f:
            self.ch['main'] = f.readline().strip().split(":")[-1]
            try:
                self.ch['debug'] = f.readline().strip().split(":")[-1]
            except:
                pass

        with open('the.key','r') as f:
            self.private_key = f.readline().strip()

        self.admins = []
        with open('the.admins','r') as f:
            for line in f.readlines():
                self.admins.append(line.strip())

        self.loop = asyncio.new_event_loop()
        self.Bot = commands.Bot(command_prefix='#')
        self.q = asyncio.Queue()

    def start(self):
        self.thread = threading.Thread(target=self.bot_thread, args=(self.loop,self.Bot,self.ch['main'],self.admins,self.private_key,self.qcounter))
        self.thread.daemon = True
        self.thread.start()

    def bot_thread(self, loop, bot, channel, admins, private_key, qcounter):
        asyncio.set_event_loop(loop)
        self.qthread = qcounter

        @bot.event
        async def on_ready():
            while True:
                data = await self.q.get()
                event = data[0]
                message = data[1]
                channel = data[2]

                try:
                    await bot.send_message(bot.get_channel(channel), message)
                except:
                    pass

                event.set()

        @bot.command(pass_context=True)
        async def ping(ctx):
            """Check to see if bot is alive"""
            await bot.say(":ping_pong:")

        @bot.command(pass_context=True)
        async def status(ctx):
            """Get some statistics."""
            corps = []
            count = 0
            with open('the.corps','r') as f:
                for line in f.readlines():
                    corps.append(line.strip().split(":")[0])
                    count += 1
            corps = ', '.join(corps)
            await bot.say("Watching kills/losses for {} corps: {}".format(count, corps))

            if self.pause:
                await bot.say("But I am currently paused.")
            else:
                await bot.say("I will post any mails I see as soon as I see them.")

        @bot.command(pass_context=True)
        async def pause(ctx):
            """Tell bot to stop posting killmails until it's asked to resume"""
            self.pause = True
            await bot.say(":pause_button: ***Automatic killmail posting paused.***")

        @bot.command(pass_context=True)
        async def resume(ctx):
            """Tell bot to resume posting killmails"""
            self.pause = False
            await bot.say(":bacon: ***Automatic killmail posting resumed.***")

        @bot.command(pass_context=True)
        async def count(ctx):
            """Show how many killmails i've seen since last start."""
            if str(ctx.message.author) in admins:
                x = []
                while not self.qthread.empty():
                    x.append(self.qthread.get_nowait())
                if not len(x):
                    x = [0]
                await bot.say("I've seen a total of {} kills since my last restart.".format(x[-1]))

        @bot.command(pass_context=True)
        async def map(ctx):
            """Fetch a link to dotlan for any region, example: #map forge"""
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

        @bot.command(pass_context=True)
        async def price(ctx):
            """crypto price check, example: #price bitcoin, #price iota"""
            msg = ctx.message.content
            coin = msg.split()[1]
            url = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(coin)
            try:
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(url)
                    response = await raw_response.text()
                    response = eval(response)[0]
                    await bot.say("{} price: ${}".format(coin.upper(), response['price_usd']))
                    await bot.say("{} % change last 1h:  {}%".format(coin.upper(), response['percent_change_1h']))
                    await bot.say("{} % change last 24h: {}%".format(coin.upper(), response['percent_change_24h']))
                    await bot.say("{} volume last 24h: ${}".format(coin.upper(), response['24h_volume_usd']))
            except Exception as e:
                print("Error in price command: {}".format(e))
                await bot.say("Sorry, I don't know how to lookup {}".format(coin))

        '''@bot.command(pass_context=True)
        async def friends(ctx):
            """Ask bot about his friends"""
            # ctx.command == 'friends'
            # ctx.invoked_with == 'friends'
            channel = self.ch.get('debug',None)
            if channel:
                await ctx.bot.send_typing(bot.get_channel(channel))
        '''

        @bot.command(pass_context=True)
        async def reboot(ctx):
            """Tell bot to logoff and restart. (permissions required)"""
            if str(ctx.message.author) in admins:
                await bot.say("Rebooting, please wait.")
                await bot.logout()
                running = False
                import os,sys
                os.execv(__file__, sys.argv)
                sys.exit(0)

        @bot.command(pass_context=True)
        async def die(ctx):
            """Tell bot to logoff. (permissions required)"""
            if str(ctx.message.author) in admins:
                await bot.say("Shutting down.")
                await bot.logout()
                running = False
                import sys
                sys.exit(0)
            else:
                await bot.say("{} is not an admin, ignoring.".format(ctx.message.author))

        bot.run(private_key)

    def send(self, channel, message):
        event = threading.Event()
        self.q.put_nowait([event, message, channel])
        event.wait()

    def run(self, debug=False):
        """main loop runs forever"""
        if debug:
            channel = self.ch['debug']
        else:
            channel = self.ch['main']

        while True:
            try:
                _url = 'wss://zkillboard.com:2096'
                _msg = '{"action":"sub","channel":"killstream"}'
                ws = websocket.create_connection(_url)
                print('Connected to: {}'.format(_url))
                ws.send(_msg)
                print('Subscribed with: {}'.format(_msg))

                running = True
                while running:
                    time.sleep(0.1)
                    if self.Bot._is_ready.is_set(): # wait until the ready event

                        while True:
                            try:
                                time.sleep(0.1)
                                raw = ws.recv()
                                d = json.loads(raw)
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
                                    c = d['victim'].get('corporation_id','none')
                                    if str(c) in self.corps:
                                        subj = 'Lose'
                                        post = True

                                self.count += 1
                                self.incr() # handle counter queue

                                msg = '`{}` {}'.format(subj, url)
                                if not self.pause:
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
                                break

            except KeyboardInterrupt:
                running = False

            except Exception as e:
                print("Unknown Error {}".format(e))

            if running:
                x = 3
                print('Sleeping {} seconds...'.format(x))
                time.sleep(x)
                print('Restarting...')
            else:
                import sys
                sys.exit(0)

    def incr(self):
        """queue the details from the last mails"""
        if self.qcounter.full():
            junk = self.qcounter.get()
        self.qcounter.put(self.count)


if __name__ == '__main__':

    bot = Zbot()
    bot.start()
    bot.run()

