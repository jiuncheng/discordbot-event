import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="?")

def is_owner(ctx):
    owners = [143012889865748480, 275540459068063753]
    for owner in owners:
        if ctx.author.id == owner:
            return True
    return False

#Bot Events
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Streaming(name="POGCHAMP", url="https://sss.com"))
    print("Bot is ready WOOOHOOOO!!!")


#Bot Commands
@bot.command()
@commands.check(is_owner)
async def load(ctx, extension):
    """Load extensions (Admin only)"""
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"```{extension} has been loaded.```")

@bot.command()
@commands.check(is_owner)
async def unload(ctx, extension):
    """Unload extensions (Admin only)"""
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"```{extension} has been unloaded.```")

@bot.command()
@commands.check(is_owner)
async def reload(ctx, extension):
    """Reload extensions (Admin only)"""
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"```{extension} has been reloaded.```")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')



TOKEN = os.environ.get("DISCORD_BOT_SECRET")
bot.run(TOKEN)
