import discord, psutil, requests, subprocess, os, json
from discord.ext import tasks, commands
from CrowdSec.crowdsec import CrowdSec
from easteregg import easteregg

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='g!', intents=intents)
photo_raspi = "https://i.imgur.com/xnByQbA.png"
photo_guanaco = "https://i.imgur.com/tTFerrA.png"

try:
   response = requests.get('https://api.ipify.org/?format=json')
   public_ip = response.json()['ip']
except Exception as e:
   public_ip = 'N/A'

@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="g!cbum"))
    await bot.add_cog(CrowdSec(bot))
    await bot.add_cog(easteregg(bot))
    stats.start()

@bot.command()
async def aide(ctx):
    bedem = discord.Embed(title="Aide", description="Voici la liste des commandes disponibles :", color=0x318CE7)
    bedem.set_thumbnail(url=photo_guanaco)
    bedem.add_field(name="g!infos", value="Affiche l'état d'utilisation du CPU et de la RAM", inline=False)
    bedem.add_field(name="g!disk", value="Affiche l'espace disque utilisé", inline=False)
    bedem.add_field(name="g!cshelp", value="Affiche les commandes utilisable pour CrowdSec", inline=False)
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

@tasks.loop(hours=1)
async def stats():
    with open("credentials.json", "r") as f:
        credentials = json.load(f)
        discord_id = int(credentials["discord"]["id"])
    channel = bot.get_channel(discord_id)

    used_gb = psutil.virtual_memory().used / (1024**3)
    available_gb = psutil.virtual_memory().available / (1024**3)
    total_gb = psutil.virtual_memory().total / (1024**3)
    network_info = psutil.net_io_counters()
    network_message = f'Débit entrant : {network_info.bytes_recv / (1024**2):.2f} MB\nDébit sortant : {network_info.bytes_sent / (1024**2):.2f} MB'
    cpu_temperature = psutil.sensors_temperatures()
    if "cpu-thermal" in cpu_temperature:
        cpu_temp = cpu_temperature["cpu-thermal"][0].current
    else:
        cpu_temp = 'N/A'
    active_connections = psutil.net_connections()
    num_active_connections = len(active_connections)

    bedem = create_embed(used_gb, available_gb, total_gb, cpu_temp, network_message, num_active_connections)
    await channel.send(embed=bedem)

@bot.command()
async def infos(ctx):
    used_gb = psutil.virtual_memory().used / (1024**3)
    available_gb = psutil.virtual_memory().available / (1024**3)
    total_gb = psutil.virtual_memory().total / (1024**3)
    network_info = psutil.net_io_counters()
    network_message = f'Débit entrant : {network_info.bytes_recv / (1024**2):.2f} MB\nDébit sortant : {network_info.bytes_sent / (1024**2):.2f} MB'
    cpu_temperature = psutil.sensors_temperatures()
    if "cpu-thermal" in cpu_temperature:
        cpu_temp = cpu_temperature["cpu-thermal"][0].current
    else:
        cpu_temp = 'N/A'
    active_connections = psutil.net_connections()
    num_active_connections = len(active_connections)

    bedem = create_embed(used_gb, available_gb, total_gb, cpu_temp, network_message, num_active_connections)
    await ctx.send(embed=bedem)

def create_embed(used_gb, available_gb, total_gb, cpu_temp, network_message, num_active_connections):
    bedem = discord.Embed(title='Rasberry Pi 4 > Infra Maison', color=0x7289DA)
    bedem.set_thumbnail(url=photo_raspi)
    bedem.add_field(name='IPv4', value=public_ip, inline=False)
    bedem.add_field(name='Utilisation CPU', value=f'{psutil.cpu_percent()}%', inline=False)
    bedem.add_field(name='Température CPU', value=f'{cpu_temp} °C', inline=False)
    bedem.add_field(name='Débit Réseau', value=network_message, inline=False)
    bedem.add_field(name='Connexions Actives', value=num_active_connections, inline=False)
    bedem.add_field(name='Utilisation RAM', value=f'{used_gb:.1f} GB / {total_gb:.1f} GB', inline=False)
    bedem.add_field(name='RAM disponible', value=f'{available_gb:.1f} GB / {total_gb:.1f} GB', inline=False)
    return bedem

with open("credentials.json", "r") as f:
    credentials = json.load(f)
    discord_token = credentials["discord"]["token"]

bot.run(discord_token)
