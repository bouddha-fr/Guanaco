import discord, psutil, requests, subprocess, os
from discord.ext import tasks, commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='g!', intents=intents)
photo_raspi = "https://i.imgur.com/xnByQbA.png"

#Permet d'aller chercher l'@publique
try:
   response = requests.get('https://api.ipify.org/?format=json')
   public_ip = response.json()['ip']
except Exception as e:
   public_ip = 'N/A'

@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="g!cbum"))
    stats.start()

@bot.command()
async def cbum(ctx):
    photo_cbum = "https://pbs.twimg.com/media/FkCfB1AXwAAO1ae.jpg"
    bedem = discord.Embed(title='Chris Bumstead', description='Tema la moustache #moustache #idolemoustache', color=0xff4c4c)
    bedem.set_image(url=photo_cbum)
    await ctx.send(embed=bedem)

@bot.command()
async def disk(ctx):
    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        partition_info = psutil.disk_usage(partition.mountpoint)
        bedem = discord.Embed(title='Disque', description=f'Espace disque utilisé pour {partition.mountpoint}', color=0xffad31)
        bedem.set_thumbnail(url=photo_raspi)
        bedem.add_field(name='Total', value=f'{partition_info.total / (1024*1024*1024):.2f} GB', inline=False)
        bedem.add_field(name='Utilisé', value=f'{partition_info.used / (1024*1024*1024):.2f} GB', inline=False)
        bedem.add_field(name='Free', value=f'{partition_info.free / (1024*1024*1024):.2f} GB', inline=False)
        await ctx.send(embed=bedem)

@bot.command()
async def csalerts(ctx):
    try:
        with open("alerts_output.txt", "w") as file:
            subprocess.run(['sudo', 'cscli', 'alerts', 'list'], stdout=file, text=True, check=True)
        with open("alerts_output.txt", "rb") as file:
            await ctx.send(file=discord.File(file, filename="alerts_output.txt"))
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Erreur lors de l'exécution de cscli alerts list : {e}")
    finally:
        os.remove("alerts_output.txt")

@tasks.loop(hours=1)
async def stats():
    channel = bot.get_channel(1220667939619864578)
    used_gb = psutil.virtual_memory().used / (1024**3)
    available_gb = psutil.virtual_memory().available / (1024**3)
    total_gb = psutil.virtual_memory().total / (1024**3)
    bedem = discord.Embed(title='Rasberry Pi 4 > Infra Maison', color=0x7289DA)
    bedem.set_thumbnail(url=photo_raspi)
    bedem.add_field(name='IPv4', value=public_ip, inline=False)
    bedem.add_field(name='Utilisation CPU', value=f'{psutil.cpu_percent()}%', inline=False)
    bedem.add_field(name='Utilisation RAM', value=f'{used_gb:.1f} GB / {total_gb:.1f} GB', inline=False)
    bedem.add_field(name='RAM disponible', value=f'{available_gb:.1f} GB / {total_gb:.1f} GB', inline=False)
    await channel.send(embed=bedem)

with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

bot.run(TOKEN)
