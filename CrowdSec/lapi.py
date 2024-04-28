import discord
from discord.ext import commands

class lapi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()

def setup(bot):
    bot.add_cog(lapi(bot))
