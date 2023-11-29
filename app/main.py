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
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    activity=discord.Game(name="a CTF? Type !event"),
)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f"{bot.user} is connected to the following guild:\n"
        f"{guild.name} (id: {guild.id})"
    )


@bot.command(
    brief="Join a CTF",
    description="This adds you to the private channel for the specified CTF event",
)
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
                            await ctx.message.channel.send(
                                f"You have been added to the channel for {e.name}."
                            )
                        case Status.FINISHED:
                            await ctx.message.channel.send(f"{e.name} has finished.")
                        case _:
                            await ctx.message.channel.send(f"An error has occurred.")
                case _:
                    await ctx.message.channel.send(event_list.print_events())
        case _:
            await ctx.message.channel.send(event_list.print_events())


@bot.command(
    brief="Archives an event",
    description="This will archive an event channel",
)
@commands.has_permissions(administrator=True)
async def archive(ctx, slug):
    event_list: Events = load_events()
    match slug:
        case slug if slug and slug.isalnum():
            e: Event = event_list.filter_event(slug)
            match e:
                case e if e.event_status != Status.FINISHED:
                    await ctx.message.channel.send(
                        "This event is not finished yet, so it cannot be archived."
                    )
                case _:
                    archive_category = 1030170219160813638
                    ctx.message.channel.edit(category=archive_category)
                    await ctx.message.channel.send("Channel successfully archived.")
        case _:
            await ctx.message.channel.send(
                "There is no event associated with this identifier."
            )


@bot.command(
    brief="Edit the current event",
    description="Options to edit: name, description, start, finish, url, role",
)
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
        await ctx.message.channel.send(
            f"Event successfully updated ({event_id}: {mode}={value})."
        )


@bot.command(
    brief="Create a new CTF event",
    description="This will create a new event using the CTFTime ID provided",
)
@commands.has_permissions(administrator=True)
async def create(ctx, ctftime_id: str, slug: str):
    if ctftime_id and ctftime_id.isnumeric() and slug and slug.isalnum():
        r = requests.get(
            f"https://ctftime.org/api/v1/events/{ctftime_id}/",
            headers={"User-Agent": None},
        )
        data = json.loads(r.text)

        event_list: Events = load_events()
        e = Event(
            slug,
            data["title"],
            data["description"],
            data["start"],
            data["finish"],
            data["url"],
        )

        # Create new role for CTF
        role = await ctx.message.guild.create_role(name=e.name)

        # Update object to contain role
        e.set_role(role.id)

        event_list.add_event(e)

        # Save the event
        save_events(event_list)

        # Create overwrites for new channel
        overwrites = {
            ctx.message.guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            role: discord.PermissionOverwrite(read_messages=True),
        }

        # Fetch the category we want
        category = ctx.message.guild.get_channel(1025881356057714748)

        # Create new channel for CTF
        channel = await ctx.message.guild.create_text_channel(
            e.name, category=category, overwrites=overwrites
        )

        embed = discord.Embed(
            title=e.name, description=e.running_time(), color=0x00FF00, url=e.url
        )

        await channel.send(embed=embed)

        # Send message to announcements
        announcements = ctx.message.guild.get_channel(1025878150086930497)
        start_timestamp = round(e.start.timestamp())
        await announcements.send(f"{e.name} has been added. Start time: <t:{start_timestamp}:R>. Type `!play {slug}` to play.")

        await ctx.message.channel.send("Event successfully created.")


@bot.command(
    aliases=["events"],
    brief="Displays the current event",
    description="Displays detailed information about the current event",
)
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

@bot.command(
    brief="Top 10 CTFTime events",
    description="Displays team's top 10 CTFTime events by CTFTime points",
)
async def top10(ctx, arg=None):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'}
    r = requests.get("https://ctftime.org/team/179144", headers=headers).text
    results = []
    for line in r.split('\n'):
        if 'place_ico' in line:
            place = line.split('<td class="place">')[1].split('<')[0]
            event = line.split('</td><td><a href="')[1].split('>')[1].split('<')[0]
            ctftime_points = line.split('<td>')[-1].split('<')[0]
            results.append({'place':place,'points':float(ctftime_points),'event':event})
    results = sorted(results,key=lambda x: x['points'], reverse=True)
    output = f"place\t| points\t| event\n{'-'*31}\n"
    for x in results[:10]:
        if len(x['place'])==1:
            output+=f" {x['place']}\t| {x['points']:.3f}\t| {x['event']}\n"
        else:
            output+=f"{x['place']}\t| {x['points']:.3f}\t| {x['event']}\n"
    await ctx.message.channel.send(f"```{output}```")

bot.run(TOKEN)
