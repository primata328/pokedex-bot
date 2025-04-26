import os
import requests
import pickle
from dotenv import load_dotenv, set_key
from discord import Intents, Interaction, Object, Embed, Guild, app_commands
from discord.ext.commands import Bot
from discord.app_commands import Choice

intents: Intents = Intents.default()
intents.message_content = True

bot: Bot = Bot(command_prefix='/', intents=intents)

def get_guilds_id() -> list[str]:
    load_dotenv(override=True)
    return os.getenv('GUILDS_ID').split(',')

def add_guild_id(guild_id: str) -> None:
    print(f'Registing a new guild ID ({guild_id})')
    set_key('.env', 'GUILDS_ID', os.getenv('GUILDS_ID') + f',{guild_id}')

def remove_guild_id(guild_id: str) -> None:
    print(f'Removing a guild ID register ({guild_id})')
    edited_guilds_id = get_guilds_id()
    edited_guilds_id.remove(guild_id)
    set_key('.env', 'GUILDS_ID', ','.join(edited_guilds_id))

def update_guilds_id() -> None:
    registed_guilds_id = get_guilds_id()
    non_registed_guilds_id = list(str(guild.id) for guild in bot.guilds)
    
    for guild_id in non_registed_guilds_id:
        if guild_id not in registed_guilds_id:
            add_guild_id(guild_id)
    
    for guild_id in registed_guilds_id:
        if guild_id not in non_registed_guilds_id:
            remove_guild_id(guild_id)   
    
@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    try:
        for guild in bot.guilds:
            await bot.tree.sync(guild=guild)
            print(f'Synced to {guild.name} (ID: {guild.id})')
            update_guilds_id()
    except Exception as e:
        print(e)

@bot.event
async def on_guild_join(guild: Guild):
    add_guild_id(str(guild.id))
    print(f'Joined to {guild.name}')
    
    try:    
        await bot.tree.sync(guild=guild)
        print(f'Synced to {guild.name} (ID: {guild.id})')
    except Exception as e:
        print(e)

@bot.event
async def on_guild_remove(guild: Guild):
    remove_guild_id(str(guild.id))
    print(f'Existed {guild.name}')

with open('pokenames.data', 'rb') as file:
    pokemons = pickle.load(file)

async def pokemon_autocomplete(interaction: Interaction, current: str) -> list[Choice[str]]:
    return [Choice(name=pokemon, value=pokemon) for pokemon in pokemons if current.lower() in pokemon.lower()][:8]

@bot.tree.command(name='pokedex', description='get information about a pokemon', guilds=list(map(lambda guild_id: Object(id=guild_id), get_guilds_id())))
@app_commands.describe(pokemon='name of the pokemon you wish to search')
@app_commands.autocomplete(pokemon=pokemon_autocomplete)
# @app_commands.choices(pokemon=[Choice(name='pikachu', value=1), Choice(name='bulbasaur', value=2), Choice(name='squirtle', value=3)])
async def search_pokemon(interaction: Interaction, pokemon: str):  
    info1, info2 = get_pokemon_info(pokemon)
    
    if info1 or info2:
        output = format_pokemon_info(info1, info2)
    else:
        output = Embed(title='Pokemon Not Found')
    try:
        await interaction.response.send_message(embed=output, delete_after=60.0)
        print(f'{interaction.guild.name} {interaction.user} {pokemon}')
    except Exception as e:
        print(e)  

def get_pokemon_info(name: str) -> dict | None:
    base_url: str = 'https://pokeapi.co/api/v2/'
    url: str = f'{base_url}/pokemon/{name}'
    response = requests.get(url)

    if response.status_code == 200:
        data1 = response.json()
    else:
        print(f'Failed to retrieve data {response.status_code}')
        data1 = None
    
    pokemon_id = data1['id']
    url: str = f'{base_url}/type/{pokemon_id}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data2 = response.json()
    else:
        print(f'Failed to retrieve data {response.status_code}')
        data2 = None
    
    return data1, data2

def add_emoji(string: str) -> str:
    match string:
        case 'normal':
            string = string.capitalize() + ':bust_in_silhouette:'
        case 'flying':
            string = string.capitalize() + ':wing:'
        case 'fighting':
            string = string.capitalize() + ':punch:'
        case 'fire':
            string = string.capitalize() + ':fire::flame:'
        case 'water':
            string = string.capitalize() + ':droplet:'
        case 'ice':
            string = string.capitalize() + ':ice_cube:'
        case 'grass':
            string = string.capitalize() + ':leaves:'
        case 'electric':
            string = string.capitalize() + ':zap:'
        case 'rock':
            string = string.capitalize() + ':rock:'
        case 'ground':
            string = string.capitalize() + ':mountain:'
        case 'poison':
            string = string.capitalize() + ':scorpion:'
        case 'bug':
            string = string.capitalize() + ':lady_beetle:'
        case 'fairy':
            string = string.capitalize() + ':fairy:'
        case 'ghost':
            string = string.capitalize() + ':ghost:'
        case 'dark':
            string = string.capitalize() + ':dark_sunglasses:'
        case 'psychic':
            string = string.capitalize() + ':clown:'
        case 'dragon':
            string = string.capitalize() + ':dragon:'
        case _:
            string = string.capitalize()
        
    return string

def format_pokemon_info(info1: dict, info2: dict) -> Embed:
    
    if info1:
        sprite: str = info1['sprites']['front_default']    
        name: str = info1['name']
        height: int = info1['height']
        weight: int = info1['weight']
        types: list[str] = []
    
        for type in info1['types']:
            type: str = type['type']['name']
            type = add_emoji(type)
            types.append(type)
    
    
        output = Embed(title=name.upper())
        output.set_thumbnail(url=sprite)
        output.add_field(name='Height', value=f'{height / 10}m', inline=True)
        output.add_field(name='Weight', value=f'{weight / 10}kg', inline=True)
        output.add_field(name='Types', value='/'.join(types), inline=False)
    
    if info2:
        weaknesses: list[str] = []
        
        for weakness in info2['damage_relations']['double_damage_from']:
            weakness = weakness['name']
            weakness = add_emoji(weakness)
            weaknesses.append(weakness)
        
        output.add_field(name='Weaknesses', value='/'.join(weaknesses), inline=True)
    else:
        output.add_field(name='Weaknesses', value='Not Found', inline=True)
    
    return output

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def main():
    bot.run(token=TOKEN)

if __name__ == '__main__':
    main()