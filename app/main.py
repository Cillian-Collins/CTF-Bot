from classes.Event import Event
from discord.ext import commands
from dotenv import load_dotenv
import base64
import discord
import json
import os
import pickle
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents, activity=discord.Game(name="a CTF? Type !event"))


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )


@bot.command()
async def play(ctx):
    await ctx.message.channel.send("You are playing.")


@bot.command()
async def debug(ctx, arg):
    await ctx.message.channel.send(f"-bash: {arg}: command not found")


@bot.command()
@commands.has_permissions(administrator=True)
async def create(ctx, arg):
    if ctx.message.author.guild_permissions.administrator and arg and arg.isnumeric():
        r = requests.get(f"https://ctftime.org/api/v1/events/{arg}/",
                         headers={"User-Agent": None})
        data = json.loads(r.text)

        e = Event(data['title'], data['description'], data['start'], data['finish'], data['url'])
        os.environ['EVENT'] = base64.b64encode(pickle.dumps(e)).decode('ascii')


@bot.command()
async def event(ctx):
    if os.getenv("EVENT"):
        e: Event = pickle.loads(base64.b64decode(os.getenv("EVENT")))
        await ctx.message.channel.send(e.status())


bot.run(TOKEN)
