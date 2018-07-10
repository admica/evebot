#!/usr/bin/python3
#bot by admica

import asyncio, discord, time, threading, websocket, json

corps = []
f = open('the.corps','r')
for line in f.readlines():
    corps.append(line.strip().split(":")[-1])

f = open('the.channel','r')
channel = f.readline().strip()

f = open('the.key','r')
private_key = f.readline().strip()

admins = []
f = open('the.admins','r')
for line in f.readlines():
    admins.append(line.strip())

loop = asyncio.new_event_loop()
bot = discord.Client()
bot_token = True
message_queue = asyncio.Queue()

def bot_thread(loop, bot, bot_token, message_queue, channel, admins):
    asyncio.set_event_loop(loop)

    @bot.event
    async def on_ready():
        while True:
            data = await message_queue.get()
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
    async def die(ctx):
        """Tell bot to logoff. (requires persmission)"""
        if str(ctx.message.author) in admins:
            await bot.say("Shutting down...")
            await bot.logout()
            import sys
            sys.exit(0)
        else:
            await bot.say("{} is not an admin, ignoring.".format(ctx.message.author))

    bot.run(private_key, bot=bot_token)

thread = threading.Thread(target=bot_thread, args=(loop,bot,bot_token,message_queue,channel,admins))
thread.daemon = True
thread.start()

def send(channel, message):
    event = threading.Event()
    message_queue.put_nowait([event, message, channel])
    event.wait()


#def go(bot):

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
            if bot._is_ready.is_set(): # wait until the ready event

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
                            if c in corps:
                                subj = 'Win'
                                post = True
                                break

                        if not post:
                            c = d['victim'].get('corporation_id','none')
                            if c in corps:
                                subj = 'Lose'
                                post = True
                                break

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

#t = threading.Thread(target=go, args=(bot,))
#t.daemon = True
#t.start()
#while True:
#    t.join(0.1)

