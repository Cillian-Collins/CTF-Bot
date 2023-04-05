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
    e: Event = pickle.loads(base64.b64decode(os.getenv("EVENT")))
    role = discord.utils.get(ctx.message.guild.roles, id=e.role)
    await ctx.message.author.add_roles(role)
    await ctx.message.channel.send(f"You have been added to the channel for {e.name}.")


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

        # Create new role for CTF
        role = await ctx.message.guild.create_role(name=e.name)

        # Update object to contain role
        e.set_role(role.id)

        # Serialize event and save to environment variable
        os.environ['EVENT'] = base64.b64encode(pickle.dumps(e)).decode('ascii')

        # Create overwrites for new channel
        overwrites = {
            ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
        }

        # Fetch the category we want
        category = ctx.message.guild.get_channel(1025881356057714748)

        # Create new channel for CTF
        await ctx.message.guild.create_text_channel(e.name, category=category, overwrites=overwrites)

        await ctx.message.channel.send("Event successfully updated.")


@bot.command()
async def event(ctx):
    if os.getenv("EVENT"):
        e: Event = pickle.loads(base64.b64decode(os.getenv("EVENT")))
        await ctx.message.channel.send(e.status())


bot.run(TOKEN)
