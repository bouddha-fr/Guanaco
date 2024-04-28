import discord, subprocess, os, requests, json
from discord.ext import commands

photo_crowdsec = "https://i.imgur.com/BHv5Ho5.png"

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
    async def cshelp(self, ctx):
            bedem = discord.Embed(title="CrowdSec Aide", description="Voici la liste des commandes disponibles :", color=0xF8AB17)
            bedem.set_thumbnail(url=photo_crowdsec)
            bedem.add_field(name="g!csrestart", value="Redémarre CrowdSec", inline=False)
            bedem.add_field(name="g!csalerts", value="Affiche les alertes", inline=False)
            bedem.add_field(name="g!csdécisions", value="Affiche les décisions", inline=False)
            bedem.add_field(name="g!csinstall_collection", value="Permet l'installation d'une collection", inline=False)
            bedem.add_field(name="g!cscti", value="Affiche les informations concernant une @ip", inline=False)
            await ctx.send(embed=bedem)

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
    async def cscti(self, ctx):
        await ctx.send("Veuillez fournir une adresse IP à vérifier.")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            message = await self.bot.wait_for('message', timeout=60, check=check)
            ip_address = message.content.strip()
        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé. Veuillez réessayer.")

        credentials_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
        try:
            with open(credentials_path, "r") as f:
                credentials = json.load(f)
                api_key = credentials["crowdsec"]["api_key"]
            url = f"https://cti.api.crowdsec.net/v2/smoke/{ip_address}"
            headers = {
                "x-api-key": api_key
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                ip_info = response.json()
                country = ip_info.get('location', {}).get('country', 'N/A')
                city = ip_info.get('location', {}).get('city', 'N/A')
                isp = ip_info.get('as_name', 'N/A')
                hostname = ip_info.get('hostname', 'N/A')
                behaviors = [behavior['name'] for behavior in ip_info.get('behaviors', [])]
                formatted_behaviors = "\n".join(behaviors) if behaviors else "Aucun comportement d'attaque trouvé."
                attack_details = [attack_details['name'] for attack_details in ip_info.get('attack_details', [])]
                formatted_attack_details = "\n".join(attack_details) if attack_details else "Aucun détails d'attaque trouvé."
                mitre_techniques = [mitre_techniques['label'] for mitre_techniques in ip_info.get('mitre_techniques', [])]
                formatted_mitre_techniques = "\n".join(mitre_techniques) if mitre_techniques else "Aucune techniques trouvé."

                bedem = discord.Embed(title="Informations sur l'adresse IP", color=0x4D4A9A)
                bedem.set_thumbnail(url=photo_crowdsec)
                bedem.add_field(name="Pays", value=country, inline=False)
                bedem.add_field(name="Ville", value=city, inline=False)
                bedem.add_field(name="Fournisseur de services Internet", value=isp, inline=False)
                bedem.add_field(name="Nom d'hôte", value=hostname, inline=False)
                bedem.add_field(name="Comportements d'attaque", value=formatted_behaviors, inline=False)
                bedem.add_field(name="Détails d'attaque", value=formatted_attack_details, inline=False)
                bedem.add_field(name="Mitre techniques", value=formatted_mitre_techniques, inline=False)
                await ctx.send(embed=bedem)
            else:
                await ctx.send(f"Erreur lors de la récupération des informations pour {ip_address}.")
        except Exception as e:
            await ctx.send(f"Une erreur s'est produite : {e}")

def setup(bot):
    bot.add_cog(CrowdSec(bot))
