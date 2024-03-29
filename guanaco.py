import discord, psutil, requests
from discord.ext import tasks, commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='g!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté.')
    stats.start()

#Permet d'aller chercher l'@publique
try:
   response = requests.get('https://api.ipify.org/?format=json')
   public_ip = response.json()['ip']
except Exception as e:
   print(f"Erreur lors de la récupération de l'adresse IP publique : {e}")
   public_ip = 'N/A'

@bot.command()
async def disk(ctx):
    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        partition_info = psutil.disk_usage(partition.mountpoint)
        bedem = discord.Embed(title='Disque', description=f'Espace disque utilisé pour {partition.mountpoint}', color=0xffad31)
        bedem.add_field(name='Total', value=f'{partition_info.total / (1024*1024*1024):.2f} GB', inline=False)
        bedem.add_field(name='Used', value=f'{partition_info.used / (1024*1024*1024):.2f} GB', inline=False)
        bedem.add_field(name='Free', value=f'{partition_info.free / (1024*1024*1024):.2f} GB', inline=False)
        await ctx.send(embed=bedem)

@tasks.loop(minutes=1)
async def stats():
    channel = bot.get_channel(1220667939619864578)
    bedem = discord.Embed(title='Rasberry Pi 4 > Infra Maison', color=0x7289DA)
    bedem.add_field(name='IPv4', value=public_ip, inline=False)
    bedem.add_field(name='Utilisation CPU', value=f'{psutil.cpu_percent()}%', inline=False)
    bedem.add_field(name='Utilisation RAM', value=f'{psutil.virtual_memory().percent}%', inline=False)
    bedem.add_field(name='RAM disponible', value=f'{psutil.virtual_memory().available * 100 / psutil.virtual_memory().total}%', inline=False)
    await channel.send(embed=bedem)

with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

bot.run(TOKEN)
