import discord
from discord.ext import commands
import asyncio
import json
import requests
import datetime

class Games(commands.Cog):

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'})

    def __init__(self, bot):
        self.bot = bot

    async def getTodayGames(self, duration: int):
        await asyncio.sleep(duration)
        now = datetime.datetime.utcnow()
        date = now.strftime("%Y-%m-%d")
        channel = self.bot.get_channel(493304164869341206)
        url = f"https://api.rawg.io/api/games?dates={date},{date}&platforms=18,1,4"
        response = self.session.get(url)
        res = json.loads(response.text)
        results = res['results']
        await channel.send(f"""```Total {res['count']} games released today.```""")
        await self.showGames(results, channel)
        next = res['next']
        
        async def fetchUrl(url: str):
            response = self.session.get(url)
            res = json.loads(response.text)
            results = res['results']
            await self.showGames(results, channel)
            return res['next']
            print(res['next'])

        while(next is not None):
            await asyncio.sleep(10)
            link = await fetchUrl(next)
            print(link)
            next = link
        
        self.bot.loop.create_task(self.getTodayGames(86400))

    async def showGames(self, results: list, channel):
        for result in results:
            platforms = ""
            genres = ""
            thumbnail = ""
            for platform in result['platforms']:
                platforms += platform['platform']['name'] + ", "

            for genre in result['genres']:
                genres += genre['name'] + ", "

            thumbnail = result['short_screenshots'][1]['image']
            platforms = platforms[:-2]
            genres = genres[:-2]
            embed = discord.Embed(
                title = f"""{result['name']}""",
                color = 0xec03fc,
                url = f"""https://www.rawg.io/games/{result['slug']}"""
            )
            embed.set_author(name="𝚁𝙰𝚆𝙶", icon_url="https://res-5.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_256,w_256,f_auto,q_auto:eco/diazvotweqf08s7mpmfs", url="https://rawg.io")
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name='Release Date', value=f"""Today, {result['released']}""", inline=True)
            # embed.add_field(name='\u200B', value='\u200B', inline=False)
            embed.add_field(name='Platform', value=f"""_{platforms}_""", inline=True)
            embed.add_field(name="Genres", value=f"""_{genres}_""", inline=False)
            # embed.add_field(name="Ratings", value=f"""{result['rating']} / {result['rating_top']}""", inline=False)
            # embed.add_field(name='\u200B', value='\u200B')
            embed.set_image(url=result['background_image'])
            embed.set_footer(text="Data obtained from RAWG.")
            await channel.send(embed=embed)

    # Bot Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Games Cog is ready.")
        self.bot.loop.create_task(self.getTodayGames(0))

    # Bot Commands
    @commands.command()
    async def search(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Games(bot))