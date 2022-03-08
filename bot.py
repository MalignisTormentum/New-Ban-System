from aiohttp import request
from datetime import datetime

import discord
import requests
import traceback
import re
import json

client = discord.Client(intents = discord.Intents.all())
lionEmoji = discord.PartialEmoji(name='🦁')
prefix, link, access_keys = ">", "", {}

class Bans:
    def get_all(access_key):
        p = {'database' : 'bans', 'method': 'get_all', 'access_key' : access_key}
        return requests.get(link, headers={"User-Agent": "XY"}, params=p).json()


    def get_ban(access_key, user_id):
        p = {'database' : 'bans', 'method': 'get_ban', 'access_key' : access_key, 'user_id' : user_id}
        return requests.get(link, headers={"User-Agent": "XY"}, params=p).json()


    def set_ban(access_key, user_id, days, reason):
        d = {'database' : 'bans', 'method': 'set_ban', 
        'access_key' : access_key, 'user_id' : user_id,
        'days' : days, 'reason' : reason}

        res = requests.post(link, headers={"User-Agent": "XY"}, data=d)
        print("SET_BAN RESPONSE: " + res.reason)


    def remove_ban(access_key, user_id, should_delete):
        d = {'database' : 'bans', 'method': 'remove_ban', 'access_key' : access_key, 'user_id' : user_id}
        res = requests.post(link, headers={"User-Agent": "XY"}, data=d)
        print("REMOVE_BAN RESPONSE: " + res.reason)
        if not should_delete:
            Bans.set_ban(access_key, user_id, 0, "BANNED REMOVED")


class Settings:
    def remove_key(guild_id):
        d = {'database' : 'guild_settings', 'method': 'remove_key', 'guild_id' : guild_id}
        res = requests.post(link, headers={"User-Agent": "XY"}, data=d)
        print("REMOVE_KEY RESPONSE: " + res.reason)


    def get_key(guild_id): # This command utilizes a cache when the bot is running to reduce database calls.
        if guild_id in access_keys:
            return access_keys[guild_id]
        p = {'database' : 'guild_settings', 'method': 'get_key', 'guild_id' : guild_id}
        res = requests.get(link, headers={"User-Agent": "XY"}, params=p).json()
        if len(res) == 0:
            return []
        access_keys[guild_id] = res[0]['access_key']
        return access_keys[guild_id]


    async def set_key(message: discord.message): # Sets cache key as well.
        if message.guild.owner == message.author or message.author.id == 881283880085237790:
            args = message.content.split()
            if len(args) > 1:
                key = get_string(1, args)
                d = {'database' : 'guild_settings', 'method': 'set_key', 'access_key' : key, 'guild_id' : message.guild.id}
                Settings.remove_key(message.guild.id)
                res = requests.post(link, headers={"User-Agent": "XY"}, data=d)
                print("SET_KEY RESPONSE: " + res.reason)
                await message.author.send(
                    "Your key for ``" + message.guild.name + " (" + str(message.guild.id) + ")`` " +
                    "has been set to ||" + key +  "||. " +
                    "**Treat it like your password and remember to add it to your game's script.**"
                )
                access_keys[message.guild.name] = key
                await message.channel.send("The server's access key has been set.")
            await message.delete()


def has_access(member: discord.Member):
    if member.id == 881283880085237790:
        return True
    for role in member.roles:
        if role.name == "Lion Access":
            return True
    return False


def role_exists(guild: discord.guild, role_name):
    for role in guild.roles:
        if role.name == role_name:
            return True
    return False


def get_string(num_deletions, args):
    for i in range(0, num_deletions):
        del args[0]
    return ' '.join(args)


async def is_key_set(message: discord.message):
    if Settings.get_key(message.guild.id):
        return True
    await message.channel.send("The server owner must set my key with ``" + prefix + "setkey`` first!")
    return False


async def get_user_from_id(message, args):
    if len(args) < 2:
        await message.channel.send("Missing arguments!")
        return None
    data = requests.get('https://users.roblox.com/v1/users/' + args[1])
    if data.status_code != 200:
        await message.channel.send("Something happened when trying to ban or unban that user. Are they Roblox terminated?")
        return None
    res = {}
    res['name'] = data.json().get('name', None)
    res['id'] = data.json().get('id', None)
    return res
    

async def get_user_from_name(message, args):
    if len(args) < 2:
        await message.channel.send("Missing arguments!")
        return None
    data = requests.get('https://api.roblox.com/users/get-by-username?username=' + args[1])
    if data.status_code != 200:
        await message.channel.send("Something happened when trying to ban or unban that user. Are they Roblox terminated?")
        return None
    res = {}
    res['name'] = data.json().get('Username', None)
    res['id'] = data.json().get('Id', None)
    return res


async def is_ban_sanitized(message, args):
    if len(args) < 4:
        await message.channel.send("An argument was missing. Usage: ``" + prefix + "ban <user> <days> <reason>``")
        return False
    if not args[2].isnumeric():
        await message.channel.send("The days must be a number!")
        return False
    return True


async def is_unban_sanitized(message, args):
    if len(args) < 2:
        await message.channel.send("A username or user ID must be supplied!")
        return False
    if len(args) > 2:
        await message.channel.send("You must supply only a username or user ID!")
        return False
    return True


async def ban(message: discord.Message):
    args = message.content.split()
    if await is_ban_sanitized(message, args):
        data, user_id, user_name = None, None, None

        if args[1].isnumeric():
            data = await get_user_from_id(message, args)
        else:
            data = await get_user_from_name(message, args)

        user_id = data['id']
        user_name = data['name']

        if user_id and user_name:
            days, reason = args[2], get_string(3, args)
            Bans.remove_ban(Settings.get_key(message.guild.id), user_id, True)
            Bans.set_ban(Settings.get_key(message.guild.id), user_id, days, reason)
            await message.channel.send(user_name + " has been banned.")


async def unban(message: discord.Message):
    args = message.content.split()
    if await is_unban_sanitized(message, args):
        data, user_id, user_name = None, None, None

        if args[1].isnumeric():
            data = await get_user_from_id(message, args)
        else:
            data = await get_user_from_name(message, args)

        user_id = data['id']
        user_name = data['name']

        if user_id and user_name:
            Bans.remove_ban(Settings.get_key(message.guild.id), user_id, False)
            await message.channel.send(user_name + " has been unbanned.")


async def create_role(message: discord.Message):
    if not message.guild.owner == message.author or not message.author.id == 881283880085237790:
        return

    if not role_exists(message.channel.guild, "Lion Access"):
        await message.guild.create_role(name="Lion Access")
        await message.channel.send("Access role created. Administrators may give this role to users who may have access to me.")
        return
    await message.channel.send("My access role already exists!")
    

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.emoji == lionEmoji:
        msg = client.get_channel(payload.channel_id).get_partial_message(payload.message_id)
        await msg.add_reaction(lionEmoji)


@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.emoji == lionEmoji:
        msg = client.get_channel(payload.channel_id).get_partial_message(payload.message_id)
        await msg.remove_reaction(lionEmoji, client.get_guild(929066364071727114).get_member(946984225733759017))


@client.event
async def on_message(message):
   if not message.guild == None: # We're not interested in listening to DMChannel events for guild applications.
        if len(message.content) > 0 and message.content[0] == prefix:
            content = message.content.lower()

            if content.startswith(prefix + "createrole"): # Must be set by server owner.
                await create_role(message)
                return

            if content.startswith(prefix + "setkey"): # Must be set by server owner. 
                await Settings.set_key(message)
                return

            if has_access(message.guild.get_member(message.author.id)): # Staff-only commands.
                if not await is_key_set(message): # Each server must set a key before they can use most the bot's commands.
                    return

                if content.startswith(prefix + "ban"):
                    await ban(message)
                    return

                if content.startswith(prefix + "unban"):
                    await unban(message)
                    return

client.run('')