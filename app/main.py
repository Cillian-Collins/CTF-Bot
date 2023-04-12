from classes.Event import Event, Status
from discord.ext import commands
from dotenv import load_dotenv
from utils.events import load_event, save_event
import discord
import json
import os
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
    e: Event = load_event()
    status = e.event_status()
    match status:
        case Status.READY | Status.STARTED:
            role = discord.utils.get(ctx.message.guild.roles, id=e.role)
            await ctx.message.author.add_roles(role)
            await ctx.message.channel.send(f"You have been added to the channel for {e.name}.")
        case Status.FINISHED:
            await ctx.message.channel.send(f"{e.name} has finished.")
        case _:
            await ctx.message.channel.send(f"An error has occurred.")


@bot.command()
async def debug(ctx, arg):
    await ctx.message.channel.send(f"-bash: {arg}: command not found")


@bot.command()
@commands.has_permissions(administrator=True)
async def edit(ctx, mode, value):
    if mode and value:
        e: Event = load_event()
        match mode:
            case "name":
                e.set_name(value)
            case "description":
                e.set_description(value)
            case "start":
                e.set_start(value)
            case "finish":
                e.set_finish(value)
            case "url":
                e.set_url(value)
            case "role":
                e.set_role(value)
        save_event(e)
        await ctx.message.channel.send(f"Event successfully updated ({mode}={value}).")


@bot.command()
@commands.has_permissions(administrator=True)
async def create(ctx, arg):
    if arg and arg.isnumeric():
        r = requests.get(f"https://ctftime.org/api/v1/events/{arg}/",
                         headers={"User-Agent": None})
        data = json.loads(r.text)

        e = Event(data['title'], data['description'], data['start'], data['finish'], data['url'])

        # Create new role for CTF
        role = await ctx.message.guild.create_role(name=e.name)

        # Update object to contain role
        e.set_role(role.id)

        # Save the event
        save_event(e)

        # Create overwrites for new channel
        overwrites = {
            ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
        }

        # Fetch the category we want
        category = ctx.message.guild.get_channel(1025881356057714748)

        # Create new channel for CTF
        channel = await ctx.message.guild.create_text_channel(e.name, category=category, overwrites=overwrites)

        embed = discord.Embed(title=e.name, description=e.running_time(), color=0x00ff00, url=e.url)

        await channel.send(embed=embed)
        await ctx.message.channel.send("Event successfully created.")


@bot.command()
async def event(ctx):
    e: Event = load_event()
    if e:
        await ctx.message.channel.send(e.status())


bot.run(TOKEN)
