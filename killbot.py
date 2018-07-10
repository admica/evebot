#!/usr/bin/python3
#killbot by admica

import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import aiohttp
import threading

with open('killbot.key','r') as f:
    private_key = f.readline().strip()
print(private_key)

admins = ['admica#1560']

bot = commands.Bot(command_prefix='#')

@bot.event
async def on_ready():
    print("Ready to serve.")


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
    except:
        await bot.say("Sorry, I don't know how to lookup {}".format(coin))


@bot.command(pass_context=True)
async def info(ctx, user: discord.Member):
    """get info on a specified username"""
    await bot.say("username is {}".format(user.name))
    await bot.say("users ID is {}".format(user.id))
    await bot.say("users status: {}".format(user.status))
    await bot.say("users highest role: {}".format(user.top_role))

def _on_message(msg=None):
    print(msg)
    #await bot.say("got message: {}".format(msg))

def _on_error(msg=None):
    print(msg)
    #await bot.say("got error: {}".format(msg))

def t_ws():
    print("Thread starting.")
    import websocket
    ws = websocket.WebSocketApp("wss://zkillboard.com:2096",on_message=_on_message, on_error=_on_error, on_open=_on_open)

    print("Thread running...")

    ws.run_forever()

def _on_open():
    #msg = '{"action":"sub","channel":"killstream"}'
    msg = '{"action":"sub","channel":"public"}'
    print("Subscribing: {}".format(msg))
    ws.send(msg)    

new_loop = asyncio.new_event_loop()
t = threading.Thread(target=t_ws, args=(new_loop,))
t.start()

bot.run(private_key)

