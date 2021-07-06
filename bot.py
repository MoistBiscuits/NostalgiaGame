from discord.enums import MessageType
import requests
from asyncio.windows_events import NULL
import os
import discord
import re
import random
from datetime import datetime
from discord.message import PartialMessage
from itertools import islice
import collections

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

class message_chain:
    users = []
    messages = []

    # constructor
    def __init__(self,users,messages):
        self.users=users
        self.messages=messages

bot = commands.Bot(command_prefix = "/", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True) # Declares slash commands through the client.
guild_ids = [564558686832295937]

#The message chain of all messages in the server
history_chain=[]

@slash.slash(name="load",
    description="Load chat history into the bot",
    options=[
    create_option(
        name="length",
        description="The length that the bot will use to create message chains",
        option_type=4,
        required=False
    )
])
async def _load_messages(ctx,*, chain_length=5):
    loading_message = await ctx.send("Loading chat history...")

    global history_chain
    history_chain = []

    if (isinstance(chain_length, str)) and (chain_length.isdecimal()):
        chain_length = int(chain_length)

    messages = await ctx.channel.history(limit=None).flatten()

    messages_iter = iter(range(0,len(messages) - chain_length + 1))
    for i in messages_iter:
        currentMessage = messages[i]
        messageChain = message_chain([currentMessage.author],[currentMessage])
        chainFound = True
        for j in range(1,chain_length):
            if (_is_date_diff_secs(currentMessage.created_at,messages[i+j].created_at,300)):
                messageChain.messages.append(messages[i+j])
                messageChain.users.append(messages[i+j].author)
            else:
                chainFound = False
                break
            currentMessage = messages[i+j]
        if(chainFound):
            history_chain.append(messageChain)
        else:
            consume(messages_iter,4)
    
    """
    for messageChain in history_chain:
        print_messages(messageChain.messages)
    """
    await loading_message.edit(content="Chat history loaded")
    

def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)

#Caculate if 2 datetimes are a given amount of seconds apart
def _is_date_diff_secs(start: datetime, end: datetime, diff: int):
    return (end - start).total_seconds() < diff

def print_messages(messages):
    text = '['
    for message in messages:
        text += str(message.content) + ","
    text += ']'
    print(text)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Run the bot
bot.run(TOKEN)