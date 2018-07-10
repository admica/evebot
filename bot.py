#!/usr/bin/python3
#bot by admica

import asyncio, discord, time, threading, websocket

channel_id = '465176579144941593'

f = open('the.key','r')
private_key = f.readline().strip()

loop = asyncio.new_event_loop()
bot = discord.Client()
bot_token = True
message_queue = asyncio.Queue()

def bot_thread(loop, bot, bot_token, message_queue, channel_id):
    asyncio.set_event_loop(loop)

    @bot.event
    async def on_ready():
        while True:
            data = await message_queue.get()
            event = data[0]
            message = data[1]
            channel_id = data[2]

            try:
                await bot.send_message(bot.get_channel(channel_id), message)
                print("Bot said: {}".format(message))
            except:
                pass

            event.set()

    bot.run(private_key, bot = bot_token)

thread = threading.Thread(target = bot_thread, args = (loop, bot, bot_token, message_queue, channel_id), daemon = True)
thread.start()

def send(channel_id, message):
    event = threading.Event()
    message_queue.put_nowait([event, message, channel_id])
    event.wait()

try:
    url = 'wss://zkillboard.com:2096'
    #msg = '{"action":"sub","channel":"public"}'
    msg = '{"action":"sub","channel":"killstream"}'

    ws = websocket.create_connection(url)
    print('Connected to: {}'.format(url))

    ws.send(msg)
    print('Subscribed with: {}'.format(msg))

    kek = False
    while not kek:
        time.sleep(0.1)
        if bot._is_ready.is_set(): # wait until the ready event
            while True:
                try:
                    raw = ws.recv()

                    data = b

                    msg = raw
                except:
                    break
                else:
                    print('Sending [{}]'.format(msg))
                    send(channel_id, msg)

            kek = True
except KeyboardInterrupt:
    pass
