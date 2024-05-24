import discord, psutil, requests, subprocess, os, json, asyncio
from discord.ext import tasks, commands
from datetime import datetime
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
    bot.loop.create_task(monitor_system())

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
        guanaco_id = int(credentials["discord"]["guanaco"])
    channel_guanaco = bot.get_channel(guanaco_id)

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
    await channel_guanaco.send(embed=bedem)

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

@bot.command(name='git')
async def git(ctx):
    await ctx.send('https://github.com/bouddha-fr/Guanaco')

async def monitor_system():
    await bot.wait_until_ready()
    with open("credentials.json", "r") as f:
        credentials = json.load(f)
        guanaco_alerts = int(credentials["discord"]["alerts"])
    guanaco_alerts = bot.get_channel(guanaco_alerts)
    if guanaco_alerts is None:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return

    while not bot.is_closed():
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if cpu_usage > 50:
            await guanaco_alerts.send(f"**Alerte** : Utilisation de `system.cpu` élevée : *{cpu_usage}%*")
            bedem = discord.Embed(title='Central Proccessing Unit', color=0xe74c3c)
            bedem.set_thumbnail(url='https://i.imgur.com/PjKUyLV.png')
            bedem.add_field(name='', value=f'`system.cpu`', inline=False)
            bedem.add_field(name='', value=f'*{cpu_usage}%*', inline=False)
            bedem.add_field(name='', value=current_time, inline=False)
            await guanaco_alerts.send(embed=bedem)

        if ram_usage > 50:
            await guanaco_alerts.send(f"**Alerte** : Utilisation de `system.ram` élevée : *{ram_usage}%*")
            bedem = discord.Embed(title='Random Access Memory', color=0xe74c3c)
            bedem.set_thumbnail(url='https://i.imgur.com/PjKUyLV.png')
            bedem.add_field(name='', value=f'`system.ram`', inline=False)
            bedem.add_field(name='', value=f'*{ram_usage}%*', inline=False)
            bedem.add_field(name='', value=current_time, inline=False)
            await guanaco_alerts.send(embed=bedem)

        await asyncio.sleep(60)


with open("credentials.json", "r") as f:
    credentials = json.load(f)
    discord_token = credentials["discord"]["token"]

bot.run(discord_token)
