import discord
from discord.ext import commands
import subprocess
import os

class CrowdSec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def csalerts(self, ctx):
        try:
            with open("alerts_output.txt", "w") as file:
                subprocess.run(['sudo', 'cscli', 'alerts', 'list'], stdout=file, text=True, check=True)
            with open("alerts_output.txt", "rb") as file:
                await ctx.send(file=discord.File(file, filename="alerts_output.txt"))
        except subprocess.CalledProcessError as e:
            await ctx.send(f"Erreur lors de l'exécution de cscli alerts list : {e}")
        finally:
            os.remove("alerts_output.txt")

    @commands.command()
    async def csdecisions(self, ctx):
        try:
            with open("decisions_output.txt", "w") as file:
                subprocess.run(['sudo', 'cscli', 'decisions', 'list'], stdout=file, text=True, check=True)
            with open("decisions_output.txt", "rb") as file:
                await ctx.send(file=discord.File(file, filename="decisions_output.txt"))
        except subprocess.CalledProcessError as e:
            await ctx.send(f"Erreur lors de l'exécution de sudo cscli decisions list : {e}")
        finally:
            os.remove("decisions_output.txt")

def setup(bot):
    bot.add_cog(CrowdSec(bot))
