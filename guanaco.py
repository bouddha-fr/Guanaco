import discord, psutil, requests, subprocess, os
from discord.ext import tasks, commands
from easteregg import easteregg
from crowdsec import CrowdSec

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='g!', intents=intents)
photo_raspi = "https://i.imgur.com/xnByQbA.png"

try:
   response = requests.get('https://api.ipify.org/?format=json')
   public_ip = response.json()['ip']
except Exception as e:
   public_ip = 'N/A'

@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="g!cbum"))
    await bot.add_cog(CBumCommand(bot))
    await bot.add_cog(CrowdSec(bot))
    stats.start()

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
    with open("channel.txt", "r") as file:
    CHANNEL = file.read().strip()

    channel = bot.get_channel(CHANNEL)
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
