import discord
from discord.ext import commands
from discord import app_commands
import requests
from datetime import datetime
import os

BOT_TOKEN   = os.environ.get('MTQ4NDk5NzM0NDcyMTEwOTE5Mg.GWsvU3.9iTL15gw6qa2mlIhW76I1g7vUdxKnTOk0C5PKg')
CLIENT_ID   = '1484997344721109192'
GUILD_ID    = 1475393525087731756
RESULTS_CH  = 1475396582139625626
JSONBIN_URL = 'https://api.jsonbin.io/v3/b/69b1a75fb7ec241ddc5e061c'
JSONBIN_KEY = '$2a$10$RvxtXiqPMhp6dWy3dgRLrOW6hJHGFIFnbrnB56SSR8nrOKXNpgDtS'

def load_delta():
    try:
        r = requests.get(JSONBIN_URL+'/latest', headers={'X-Master-Key':JSONBIN_KEY})
        d = r.json().get('record', {})
        if d and d.get('savedAt'): return d
    except: pass
    return {'added':[],'deleted':[],'edited':[],'gmAdded':[],'gmDeleted':[],'tierPairs':[],'manualOrder':[],'savedAt':None}

def save_delta(delta):
    delta['savedAt'] = datetime.utcnow().isoformat()
    requests.put(JSONBIN_URL, json=delta, headers={
        'Content-Type':'application/json',
        'X-Master-Key':JSONBIN_KEY,
        'X-Bin-Versioning':'false'
    })

def add_player(ign, region, gm, tier):
    delta = load_delta()
    delta.setdefault('added', [])
    delta.setdefault('deleted', [])
    idx = next((i for i,p in enumerate(delta['added']) if p['name'].lower()==ign.lower()), -1)
    if idx >= 0:
        delta['added'][idx]['gm'][gm] = tier
        delta['added'][idx]['region'] = region
    else:
        delta['added'].append({'name':ign,'region':region,'gm':{gm:tier},'pts':0})
    delta['deleted'] = [n for n in delta['deleted'] if n.lower()!=ign.lower()]
    save_delta(delta)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot online as {bot.user}')
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print('✅ /ctlresults registered')
    except Exception as e:
        print(f'❌ {e}')

@bot.tree.command(name='ctlresults', description='Add a player result to CTLtiers website')
@app_commands.guild_only()
@app_commands.choices(
    gamemode=[
        app_commands.Choice(name='Vanilla',       value='vanilla'),
        app_commands.Choice(name='UHC',           value='uhc'),
        app_commands.Choice(name='Crystal/Pot',   value='pot'),
        app_commands.Choice(name='NethOP',        value='nethop'),
        app_commands.Choice(name='SMP',           value='smp'),
        app_commands.Choice(name='Sword',         value='sword'),
        app_commands.Choice(name='Axe',           value='axe'),
        app_commands.Choice(name='Mace',          value='mace'),
    ],
    tier=[
        app_commands.Choice(name='HT1',value='HT1'), app_commands.Choice(name='HT2',value='HT2'),
        app_commands.Choice(name='HT3',value='HT3'), app_commands.Choice(name='HT4',value='HT4'),
        app_commands.Choice(name='HT5',value='HT5'), app_commands.Choice(name='LT1',value='LT1'),
        app_commands.Choice(name='LT2',value='LT2'), app_commands.Choice(name='LT3',value='LT3'),
        app_commands.Choice(name='LT4',value='LT4'), app_commands.Choice(name='LT5',value='LT5'),
    ],
    region=[
        app_commands.Choice(name='NA',value='NA'), app_commands.Choice(name='EU',value='EU'),
        app_commands.Choice(name='AS',value='AS'), app_commands.Choice(name='OC',value='OC'),
    ]
)
async def ctlresults(
    interaction: discord.Interaction,
    ign: str,
    gamemode: str,
    tier: str,
    tester: str = 'Staff',
    region: str = 'NA'
):
    await interaction.response.defer()
    try:
        add_player(ign, region, gamemode, tier)
        gm_label = {
            'vanilla':'Vanilla','uhc':'UHC','pot':'Crystal/Pot',
            'nethop':'NethOP','smp':'SMP','sword':'Sword','axe':'Axe','mace':'Mace'
        }.get(gamemode, gamemode)

        embed = discord.Embed(
            title=f'{ign} added to CTLtiers',
            color=0x3b82f6
        )
        embed.add_field(name='IGN',      value=ign,      inline=True)
        embed.add_field(name='Gamemode', value=gm_label, inline=True)
        embed.add_field(name='Tier',     value=tier,     inline=True)
        embed.add_field(name='Region',   value=region,   inline=True)
        embed.add_field(name='Tester',   value=tester,   inline=True)
        embed.set_thumbnail(url=f'https://visage.surgeplay.com/bust/{ign}.png')
        embed.set_footer(text='CTLtiers • trpvp.club')

        await interaction.followup.send(embed=embed)
        print(f'✅ {ign} → {gamemode} {tier} (tester: {tester})')
    except Exception as e:
        await interaction.followup.send(f'❌ Error: {e}')

bot.run(BOT_TOKEN)
