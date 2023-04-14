from classes.Event import Event, Status
from classes.Events import Events
from discord.ext import commands
from dotenv import load_dotenv
from enum import Enum
from utils.events import load_events, save_events
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


@bot.command(brief='Join a CTF', description='This adds you to the private channel for the specified CTF event')
async def play(ctx, arg=None):
    event_list: Events = load_events()
    match arg:
        case arg if arg and arg.isalnum():
            e: Event = event_list.filter_event(arg)
            match e:
                case Event():
                    status: Enum = e.event_status()
                    match status:
                        case Status.READY | Status.STARTED:
                            role = discord.utils.get(ctx.message.guild.roles, id=e.role)
                            await ctx.message.author.add_roles(role)
                            await ctx.message.channel.send(f"You have been added to the channel for {e.name}.")
                        case Status.FINISHED:
                            await ctx.message.channel.send(f"{e.name} has finished.")
                        case _:
                            await ctx.message.channel.send(f"An error has occurred.")
                case _:
                    await ctx.message.channel.send(event_list.print_events())
        case _:
            await ctx.message.channel.send(event_list.print_events())


@bot.command(brief='Runs a bash command for debugging', description='This will run a bash command for debugging')
async def debug(ctx, arg):
    await ctx.message.channel.send(f"-bash: {arg}: command not found")


@bot.command(brief='Edit the current event', description='Options to edit: name, description, start, finish, url, role')
@commands.has_permissions(administrator=True)
async def edit(ctx, event_id, mode, value):
    if mode and value:
        event_list: Events = load_events()
        e: Event = event_list.filter_event(event_id)
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
        event_list.update_event(event_id, e)
        save_events(event_list)
        await ctx.message.channel.send(f"Event successfully updated ({event_id}: {mode}={value}).")


@bot.command(brief='Create a new CTF event', description='This will create a new event using the CTFTime ID provided')
@commands.has_permissions(administrator=True)
async def create(ctx, arg: str, arg2: str):
    if arg and arg.isnumeric() and arg2 and arg2.isalnum():
        r = requests.get(f"https://ctftime.org/api/v1/events/{arg}/",
                         headers={"User-Agent": None})
        data = json.loads(r.text)

        event_list: Events = load_events()
        e = Event(arg2, data['title'], data['description'], data['start'], data['finish'], data['url'])

        # Create new role for CTF
        role = await ctx.message.guild.create_role(name=e.name)

        # Update object to contain role
        e.set_role(role.id)

        event_list.add_event(e)

        # Save the event
        save_events(event_list)

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


@bot.command(brief='Displays the current event', description='Displays detailed information about the current event')
async def event(ctx, arg=None):
    event_list: Events = load_events()
    match arg:
        case arg if arg and arg.isalnum():
            e: Event = event_list.filter_event(arg)
            match e:
                case Event():
                    await ctx.message.channel.send(e.status())
                case _:
                    await ctx.message.channel.send(event_list.print_events())
        case _:
            await ctx.message.channel.send(event_list.print_events())


bot.run(TOKEN)
