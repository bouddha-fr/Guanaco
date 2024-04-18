import discord, subprocess, os
from discord.ext import commands

def install_crowdsec_collection(collection_name):
    try:
        subprocess.run(['sudo', 'cscli', 'collections', 'install', collection_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def restart_crowdsec():
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'crowdsec'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

class CrowdSec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def csrestart(self, ctx):
        restart_success = restart_crowdsec()
        if restart_success:
            await ctx.send("Service CrowdSec redémarré avec succès !")
            print("Service CrowdSec redémarré avec succès !")
        else:
            await ctx.send("Erreur lors du redémarrage du service CrowdSec.")

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

    @commands.command()
    async def csinstall_collection(self, ctx):
        await ctx.send("Quel collection CrowdSec souhaitez-vous installer ?")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            message = await self.bot.wait_for('message', timeout=60, check=check)
            collection_name = message.content.strip()
            success = install_crowdsec_collection(collection_name)
            if success:
                await ctx.send(f"La collection '{collection_name}' a été installé avec succès !")
                restart_success = restart_crowdsec()
                if restart_success:
                    await ctx.send("Service CrowdSec redémarré avec succès !")
                else:
                    await ctx.send("Erreur lors du redémarrage du service CrowdSec.")
            else:
                await ctx.send(f"Erreur lors de l'installation de la collection '{collection_name}'.")
        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé. Veuillez réessayer.")

    @commands.command()
    async def ipinfo(self, ctx,):
        await ctx.send("Veuillez fournir une adresse IP à vérifier.")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            message = await self.bot.wait_for('message', timeout=60, check=check)
            ip_address = message.content.strip()
        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé. Veuillez réessayer.")

        try:
            api_key = "60386a77a30e5e"
            url = f"https://ipinfo.io/{ip_address}/json?token={api_key}"
            response = requests.get(url)
            data = response.json()

            country = data.get('country', 'N/A')
            city = data.get('city', 'N/A')
            isp = data.get('org', 'N/A')
            hostname = data.get('hostname', 'N/A')

            embed = discord.Embed(title="Informations sur l'adresse IP", color=0x7289DA)
            embed.add_field(name="Pays", value=country, inline=False)
            embed.add_field(name="Ville", value=city, inline=False)
            embed.add_field(name="Fournisseur de services Internet", value=isp, inline=False)
            embed.add_field(name="Nom d'hôte", value=hostname, inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Une erreur s'est produite : {e}")

def setup(bot):
    bot.add_cog(CrowdSec(bot))
