#!/usr/bin/python3
#Discord eve bot by admica

import asyncio, discord, time, threading, websocket, json
from discord.ext import commands
from discord.ext.commands import Bot
import aiohttp

class Zbot:
    def __init__(self):

        self.corps = []
        with open('the.corps','r') as f:
            for line in f.readlines():
                self.corps.append(line.strip().split(":")[-1])

        self.ch = {}
        with open('the.channel','r') as f:
            self.ch['main'] = f.readline().strip()
            try:
                self.ch['verbose'] = f.readline().strip()
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
        self.thread = threading.Thread(target=self.bot_thread, args=(self.loop,self.Bot,self.ch['main'],self.admins,self.private_key))
        self.thread.daemon = True
        self.thread.start()

    def bot_thread(self, loop, bot, channel, admins, private_key):
        asyncio.set_event_loop(loop)

        @bot.event
        async def on_ready():
            while True:
                data = await self.q.get()
                event = data[0]
                message = data[1]
                channel = data[2]

                try:
                    await bot.send_message(bot.get_channel(channel), message)
                    #print("Bot said: {}".format(message))
                except:
                    pass

                event.set()

        @bot.command(pass_context=True)
        async def ping(ctx):
            """check to see if bot is alive"""
            await bot.say(":ping_pong:")

        @bot.command(pass_context=True)
        async def price(ctx):
            """cryptocurrency price check, example: price bitcoin, or price iota"""
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

        @bot.command(pass_context=True)
        async def friends(ctx):
            """Ask bot about his friends"""
            # ctx.command == 'friends'
            # ctx.invoked_with == 'friends'
            channel = self.ch.get('verbose',None)
            if channel:
                await ctx.bot.send_typing(bot.get_channel(channel))

        @bot.command(pass_context=True)
        async def die(ctx):
            """Tell bot to logoff. (requires persmission)"""
            if str(ctx.message.author) in admins:
                await bot.say("Shutting down...")
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
            channel = self.ch['verbose']
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

                                msg = '`{}` {}'.format(subj, url)
                                if post:
                                    print('Sending: {}'.format(msg))
                                    send(channel, msg)
                                    time.sleep(0.01)
                                else:
                                    print('{} is not interesting'.format(msg))

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

if __name__ == '__main__':

    bot = Zbot()
    bot.start()
    bot.run()

