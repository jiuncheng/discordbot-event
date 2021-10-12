import discord
from discord.ext import commands
import asyncio
import sys, os, json
sys.path.append(os.getcwd())

from events import Events
from eventdate import EventDate

def is_owner(ctx):
    owners = [143012889865748480, 275540459068063753]
    for owner in owners:
        if ctx.author.id == owner:
            return True
    return False

class EventsBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Bot Events ( @commands.Cog.listener() )
    @commands.Cog.listener()
    async def on_ready(self):
        print("EventsBot Cog is ready.")


    #Bot Commands
    @commands.command()
    async def create(self, ctx, dt: str, *, title: str):
        """Create new event."""
        creator = {'fullid': ctx.message.author, 'id': ctx.message.author.id, 'name': ctx.message.author.name, 'image': ctx.author.avatar_url}
        events = Events()
        event = events.createEvent(title, dt, creator)
        if event is None:
            await ctx.send(f"```Event date must be later than current's date and time.```")
            return
        date = EventDate(dt)
        seconds = date.calcDiff()
        if int(seconds - 1800) <= 0:
            remindSeconds = int(seconds / 2)
        else:
            remindSeconds = int(seconds - 1800)
        print(event['id'])
        self.bot.loop.create_task(self.remindEvent(ctx, event['id'], remindSeconds))
        self.bot.loop.create_task(self.eventStarted(ctx, event['id'], seconds))
        # await ctx.send(f"""An event has beeen scheduled at _**{ date.displayTime() }**_ \n\nEvent: _**{title}**_ \n\nPeople going: \n 1. {ctx.author.mention} \n\n\n Type \"?go\" to go to Event\n\n ** **""")
        game = checkGames(event['title'].lower())
        if game is not None:
            name = game['name']
            thumbnail = game['thumbnail']
            image = game['image']
            embed = eventCreatedEmbed(event['creator']['name'], event['creator']['image'], thumbnail, title, date.displayTime(), name, ctx.author.mention, image)
        else:
            embed = eventCreatedEmbed(event['creator']['name'], event['creator']['image'], "", title, date.displayTime(), "No Games", ctx.author.mention, "")
        await ctx.send(embed=embed)
        
        print(ctx.message)

    @commands.command()
    async def view(self, ctx, id: int=None):
        """View ongoing events and specific events"""
        if id is None:
            data = Events().getEventsInfo()
            await ctx.send(f"```Event Planned: \n\n{data}\nType view command with id to view specific event. (e.g. ?view 2)```")
        else:
            events = Events().getEvents()
            id = id - 1
            if id < len(events) and id >= 0:
                eventDate = EventDate(jsonDate=events[id]['eventDate'])
                data = Events().displayGoingMembers(events[id]['going'])
                # await ctx.send(f"""Event: _**{events[id]['title']}**_ \n\nDate: _{eventDate.displayTime()}_\n\nPeople going: \n {data}\n\nType \"?go\" to go to Event\n\n ** **""")
                game = checkGames(events[id]['title'].lower())
                if game is not None:
                    name = game['name']
                    thumbnail = game['thumbnail']
                    image = game['image']
                    embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], thumbnail, events[id]['title'], eventDate.displayTime(), name, data, image)
                else:
                    embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], "", events[id]['title'], eventDate.displayTime(), "No Games", data, "")
                await ctx.send(embed=embed)
            else:
                await ctx.send("```No event with the id specified found.```")

    @commands.command()
    async def go(self, ctx, id: int=None):
        """Set Go status to event"""
        if id is None:
            print(id)
            data = Events().getEventsInfo()
            await ctx.send(f"```Please Choose an Event to GO: \n\n{data} \n\n Type the number of the Event to Go. (e.g. ?go 3) \n```")
        else:
            events = Events().getEvents()
            id = id - 1
            if id < len(events) and id >= 0:
                eventDate = EventDate(jsonDate=events[id]['eventDate'])

                for goingMembers in events[id]['going']:
                    if goingMembers['id'] == ctx.message.author.id:
                        await ctx.send("```You are already going to the event.```")
                        return
                
                if events[id]['going'] == []:
                    member = {'fullid': ctx.message.author, 'id': ctx.message.author.id, 'name': ctx.message.author.name}
                    events[id]['going'].append(member)
                    Events().saveEvents(events)
                    data = Events().displayGoingMembers(events[id]['going'])
                    # await ctx.send(f"""Event: _**{events[id]['title']}**_ \n\nDate: _{eventDate.displayTime()}_\n\nPeople going: \n {str}\n\nType \"?go\" to go to Event\n\n ** **""")
                    game = checkGames(events[id]['title'].lower())
                    if game is not None:
                        name = game['name']
                        thumbnail = game['thumbnail']
                        image = game['image']
                        embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], thumbnail, events[id]['title'], eventDate.displayTime(), name, data, image)
                    else:
                        embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], "", events[id]['title'], eventDate.displayTime(), "No Games", data, "")
                    await ctx.send(embed=embed)
                else:
                    member = {'fullid': ctx.message.author, 'id': ctx.message.author.id, 'name': ctx.message.author.name}
                    events[id]['going'].append(member)
                    Events().saveEvents(events)
                    data = Events().displayGoingMembers(events[id]['going'])
                    # await ctx.send(f"""Event: _**{events[id]['title']}**_ \n\nDate: _{eventDate.displayTime()}_\n\nPeople going: \n {str}\n\nType \"?go\" to go to Event\n\n ** **""")
                    game = checkGames(events[id]['title'].lower())
                    if game is not None:
                        name = game['name']
                        thumbnail = game['thumbnail']
                        image = game['image']
                        embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], thumbnail, events[id]['title'], eventDate.displayTime(), name, data, image)
                    else:
                        embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], "", events[id]['title'], eventDate.displayTime(), "No Games", data, "")
                    await ctx.send(embed=embed)
                    return
            else:
                await ctx.send("```Sorry, No id found in events.```")


    @commands.command()
    async def ungo(self, ctx, id: int=None):
        """Remove Go status from an event"""
        if id is None:
            data = Events().getEventsInfo()
            await ctx.send(f"```Please Choose an Event to UnGO: \n\n{data} \n\n Type the number of the Event to UnGo. (e.g. ?ungo 3) \n```")
        else:
            events = Events().getEvents()
            id = id - 1
            if id < len(events) and id >= 0:
                eventDate = EventDate(jsonDate=events[id]['eventDate'])

                if len(events[id]['going']) <= 0:
                    await ctx.send("```You have not registered to go yet. No ungo available.```")
                    return
                else:
                    for i in range(len(events[id]['going'])):
                        if events[id]['going'][i]['id'] == ctx.message.author.id:
                            del events[id]['going'][i]
                            Events().saveEvents(events)
                            data = Events().displayGoingMembers(events[id]['going'])
                            await ctx.send(f"""{ctx.author.mention} has decided to not to go to the event. You suck.""")
                            # await ctx.send(f"""Event: _**{events[id]['title']}**_ \n\nDate: _{eventDate.displayTime()}_\n\nPeople going: \n {data}\n\nType \"?go\" to go to Event\n\n ** **""")
                            game = checkGames(events[id]['title'].lower())
                            if game is not None:
                                name = game['name']
                                thumbnail = game['thumbnail']
                                image = game['image']
                                embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], thumbnail, events[id]['title'], eventDate.displayTime(), name, data, image)
                            else:
                                embed = eventGoEmbed(events[id]['creator']['name'], events[id]['creator']['image'], "", events[id]['title'], eventDate.displayTime(), "No Games", data, "")
                            await ctx.send(embed=embed)
                            return

                    await ctx.send("```You have not registered to go yet. No ungo available.```")
                    return
            else:
                await ctx.send("```Sorry, No id found in events.```")

    @commands.command()
    async def delete(self, ctx, id: int=None):
        """Delete an event"""
        if id is None:
            events = Events().getEventsInfo()
            await ctx.send(f"```Please Choose an Event to Delete: \n\n{events} \n\n Type the number of the Event to Delete. (e.g. ?delete 3) \n```")
            return
        else:
            id = id - 1
            events = Events().getEvents()
            if id < len(events) and id >= 0:
                event = events[id]
                if not event['creator']['id'] == ctx.author.id:
                    await ctx.send(f"```You don't have permissions to delete this event. Only {event['creator']['name']} or Administrator can delete this event.```")
                    return
                else:
                    del events[id]
                    Events().saveEvents(events)
                    eventDate = EventDate(jsonDate=event['eventDate'])
                    await ctx.send(f"""```Event titled **{event['title']}** at {eventDate.displayTime()} has been deleted.```""")
                    return
            else:
                await ctx.send("```Sorry, No id found in events.```")

    @commands.command()
    @commands.check(is_owner)
    async def deleteperm(self, ctx, id: int=None):
        """Admin permission to delete any event. *Admin only."""
        if id is None:
            events = Events().getEventsInfo()
            await ctx.send(f"```Please Choose an Event to Delete: \n\n{events} \n\n Type the number of the Event to Delete. (e.g. ?delete 3) \n```")
            return
        else:
            id = id - 1
            events = Events().getEvents()
            if id < len(events) and id >= 0:
                event = events[id]
                del events[id]
                Events().saveEvents(events)
                eventDate = EventDate(jsonDate=event['eventDate'])
                await ctx.send(f"""```Event titled **{event['title']}** at {eventDate.displayTime()} has been deleted.```""")
                return
            else:
                await ctx.send("```Sorry, No id found in events.```")


    @commands.command()
    async def remind(self, ctx, id: int=None):
        """Remind all members of an event"""
        if id is None:
            events = Events().getEventsInfo()
            await ctx.send(f"```Please Choose an Event to Remind: \n\n{events} \n\n Type the number of the Event to Remind. (e.g. ?remind 3) \n```")
            return
        else:
            events = Events().getEvents()
            id = id - 1
            if id < len(events) and id >= 0:
                eventDate = EventDate(jsonDate=events[id]['eventDate'])
                data = Events().displayGoingMembers(events[id]['going'])
                # await ctx.send(f"""
                #     :calendar_spiral: :calendar_spiral: :calendar_spiral:      **REMINDER**      :calendar_spiral: :calendar_spiral: :calendar_spiral:\n
                # TIME LEFT: **{eventDate.displayDuration()}**\n\nEvent: _**{events[id]['title']}**_ \nDate: _{eventDate.displayTime()}_\n\nPeople going: \n {data}\n\nType \"?go\" to go to Event\n\n ** **""")
                game = checkGames(events[id]['title'].lower())
                if game is not None:
                    name = game['name']
                    thumbnail = game['thumbnail']
                    image = game['image']
                    embed = eventRemindEmbed(eventDate.displayDuration(), events[id]['creator']['name'], events[id]['creator']['image'], thumbnail, events[id]['title'], eventDate.displayTime(), name, data, image)
                else:
                    embed = eventRemindEmbed(eventDate.displayDuration(), events[id]['creator']['name'], events[id]['creator']['image'], "", events[id]['title'], eventDate.displayTime(), "No Games", data, "")
                await ctx.send(embed=embed)
            else:
                await ctx.send("```No event with the id specified found.```")

    async def remindEvent(self, ctx, id: int, duration: int):
        await asyncio.sleep(duration)
        print("reminding event")
        event = Events().getSingleEvent(id)
        if event is not None:
            eventDate = EventDate(jsonDate=event['eventDate'])
            data = Events().displayGoingMembers(event['going'])
            # await ctx.send(f"""
            #     :calendar_spiral: :calendar_spiral: :calendar_spiral:      **REMINDER**      :calendar_spiral: :calendar_spiral: :calendar_spiral:\n
            # TIME LEFT: **{eventDate.displayDuration()}**\n\nEvent: _**{event['title']}**_ \nDate: _{eventDate.displayTime()}_\n\nPeople going: \n {data}\n\nType \"?go\" to go to Event\n\n ** **""")
            game = checkGames(event['title'].lower())
            if game is not None:
                name = game['name']
                thumbnail = game['thumbnail']
                image = game['image']
                embed = eventRemindEmbed(eventDate.displayDuration(), event['creator']['name'], event['creator']['image'], thumbnail, event['title'], eventDate.displayTime(), name, data, image)
            else:
                embed =eventRemindEmbed(eventDate.displayDuration(), event['creator']['name'], event['creator']['image'], "", event['title'], eventDate.displayTime(), "No Games", data, "")
            await ctx.send(embed=embed)

    async def eventStarted(self, ctx, id:int, duration: int):
        await asyncio.sleep(duration)
        print("starting event")
        event = Events().getSingleEvent(id)
        if event is not None:
            eventDate = EventDate(jsonDate=event['eventDate'])
            data = Events().displayGoingMembers(event['going'])
            # await ctx.send(f"""
            #     <:pogu:476023083514200064>       :loudspeaker: :loudspeaker: :loudspeaker:      **ANNOUNCEMENT**      :loudspeaker: :loudspeaker: :loudspeaker:       <:pogu:476023083514200064>\n
            # _**AN EVENT HAS STARTED NOW!!!!**_\n\nEvent: _**{event['title']}**_ \nDate: _{eventDate.displayTime()}_\n\nWelcome, \n {data}\n\n<:pepelmao:487990267568193536>  <:pepelmao:487990267568193536>  <:pepelmao:487990267568193536>  <:pepelmao:487990267568193536>  <:pepelmao:487990267568193536>  <:pepelmao:487990267568193536>  <:pepelmao:487990267568193536>  <:pepelmao:487990267568193536>\n\n** **""")

            game = checkGames(event['title'].lower())
            if game is not None:
                name = game['name']
                thumbnail = game['thumbnail']
                image = game['image']
                embed = eventStartedEmbed(event['creator']['name'], event['creator']['image'], thumbnail, event['title'], eventDate.displayTime(), name, data, image)
            else:
                embed = eventStartedEmbed(event['creator']['name'], event['creator']['image'], "", event['title'], eventDate.displayTime(), "No Games", data, "")
            await ctx.send(embed=embed)
            Events().deleteEvent(id)

def eventCreatedEmbed(authorName, authorImg, thumbnail, eventTitle, eventDate, gameTitle, members, image):
    embed = discord.Embed(
        title = f"""An event has beeen scheduled at _**{ eventDate }**_""",
        color = 0x4287f5
    )
    embed.set_author(name=authorName, icon_url=authorImg)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Event', value=f"""**{eventTitle}**""", inline=False)
    embed.add_field(name='Time', value=f"""_**{eventDate}**_""", inline=False)
    embed.add_field(name='Game', value=f"""**{gameTitle}**""", inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.add_field(name="Going:", value="1. " + members, inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.set_image(url=image)
    embed.set_footer(text=f"""Type \"?go\" to go to Event.""")
    return embed

def eventGoEmbed(authorName, authorImg, thumbnail, eventTitle, eventDate, gameTitle, members, image):
    embed = discord.Embed(
        title = f"""_**{ eventDate }**_""",
        color = 0x4287f5
    )
    embed.set_author(name=authorName, icon_url=authorImg)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Event', value=f"""**{eventTitle}**""", inline=False)
    embed.add_field(name='Time', value=f"""_**{eventDate}**_""", inline=False)
    embed.add_field(name='Game', value=f"""**{gameTitle}**""", inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.add_field(name="Going:", value=members, inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.set_image(url=image)
    embed.set_footer(text=f"""Type \"?go\" to go to Event.""")
    return embed

def eventRemindEmbed(duration, authorName, authorImg, thumbnail, eventTitle, eventDate, gameTitle, members, image):
    embed = discord.Embed(
        title = f""":calendar_spiral:  Reminder: _**{ duration } Left**_""",
        color = 0xffc940
    )
    embed.set_author(name=authorName, icon_url=authorImg)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Event', value=f"""**{eventTitle}**""", inline=False)
    embed.add_field(name='Time', value=f"""_**{eventDate}**_""", inline=False)
    embed.add_field(name='Game', value=f"""**{gameTitle}**""", inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.add_field(name="Going:", value=members, inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.set_image(url=image)
    embed.set_footer(text=f"""Type \"?go\" to go to Event.""")
    return embed

def eventStartedEmbed(authorName, authorImg, thumbnail, eventTitle, eventDate, gameTitle, members, image):
    embed = discord.Embed(
        title = f"""_AN EVENT HAS STARTED NOW!!!_""",
        color = 0x42f584
    )
    embed.set_author(name=authorName, icon_url=authorImg)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Event', value=eventTitle, inline=False)
    embed.add_field(name='Time', value=eventDate, inline=False)
    embed.add_field(name='Game', value=gameTitle, inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.add_field(name="Welcome,", value=members, inline=False)
    embed.add_field(name='\u200B', value='\u200B')
    embed.set_image(url=image)
    return embed

def checkGames(title: str):
    with open("GameList.json", "r") as f:
        games = json.load(f)

        for game in games:
            if game['title'] in title:
                data = {'name': game['name'], 'thumbnail': game['thumbnail'], 'image': game['image']}
                return data
        return None

def setup(bot):
    bot.add_cog(EventsBot(bot))

print(os.getcwd())