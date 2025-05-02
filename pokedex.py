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
    load_dotenv(dotenv_path='C:\\Users\\Marcos Felipe\\Documents\\Projects\\python\\pokedex\\.env', override=True)
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

with open('C:\\Users\\Marcos Felipe\\Documents\\Projects\\python\\pokedex\\pokenames.data', 'rb') as file:
    pokemons = pickle.load(file)

async def pokemon_autocomplete(interaction: Interaction, current: str) -> list[Choice[str]]:
    return [Choice(name=pokemon, value=pokemon) for pokemon in pokemons if current.lower() in pokemon.lower()][:8]

@bot.tree.command(name='pokedex', description='get information about a pokemon', guilds=list(map(lambda guild_id: Object(id=guild_id), get_guilds_id())))
@app_commands.describe(pokemon='name of the pokemon you wish to search')
@app_commands.autocomplete(pokemon=pokemon_autocomplete)
# @app_commands.choices(pokemon=[Choice(name='pikachu', value=1), Choice(name='bulbasaur', value=2), Choice(name='squirtle', value=3)])
async def search_pokemon(interaction: Interaction, pokemon: str):  
    info = get_pokemon_info(pokemon)
    
    if info:
        output = format_pokemon_info(info)
    else:
        output = Embed(title='Pokemon Not Found')
    try:
        await interaction.response.send_message(embed=output, delete_after=180.0)
        print(f'{interaction.guild.name} {interaction.user} {pokemon}')
    except Exception as e:
        print(e)  

def get_pokemon_info(name: str) -> dict | None:
    base_url: str = 'https://pokeapi.co/api/v2/'
    url: str = f'{base_url}/pokemon/{name}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        print(f'Failed to retrieve data {response.status_code}')
        data = None
    
    return data

def add_emoji(string: str) -> str:
    prefix = False
    if string.startswith('2x'):
        prefix = True
        string = string.removeprefix('2x')
    
    match string:
        case 'normal':
            string = string.capitalize() + ':bust_in_silhouette:'
        case 'flying':
            string = string.capitalize() + ':wing:'
        case 'fighting':
            string = string.capitalize() + ':punch:'
        case 'fire':
            string = string.capitalize() + ':fire:'
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
        case 'steel':
            string = string.capitalize() + ':gear:'
        case _:
            string = string.capitalize()
        
    if prefix:
        return '2x' + string
    else:
        return string

def format_pokemon_info(info: dict) -> Embed:
    
    if info:
        sprite: str = info['sprites']['front_default']    
        name: str = info['name']
        height: int = info['height']
        weight: int = info['weight']
        types: list[str] = []
    
        for type in info['types']:
            type: str = type['type']['name']
            types.append(type)
            
        types.sort()
    
        output = Embed(title=name.upper().replace('-', ' '))
        output.set_thumbnail(url=sprite)
        output.add_field(name='Height', value=f'{height / 10}m', inline=True)
        output.add_field(name='Weight', value=f'{weight / 10}kg', inline=True)
        output.add_field(name='Types', value='/'.join([add_emoji(type) for type in types]), inline=False)
    
    
        weaknesses: list[str] = calc_weakness(types)
        
        for weakness in weaknesses:
            if weaknesses.count(weakness) > 1:
                # weaknesses = list(dict.fromkeys(weaknesses))
                weaknesses.remove(weakness)
                weaknesses[weaknesses.index(weakness)] = '2x' + weakness
                
        weaknesses.sort()
        
        output.add_field(name='Weaknesses', value=f'{'/'.join(list(add_emoji(weakness) for weakness in weaknesses))}', inline=True)
    
    return output

def calc_weakness(types: list[str]) -> list[str]:
    weaknesses: list[str] = []
    resistances: list[str] = []
    immunities: list[str] = []
    
    for type in types:
        match type:
            case 'normal':
                weaknesses.extend(['fighting'])
                resistances.extend([])
                immunities.extend(['ghost'])
            case 'fire':
                weaknesses.extend(['water', 'ground', 'rock'])
                resistances.extend(['fire', 'grass', 'ice', 'bug', 'steel', 'fairy'])
                immunities.extend([])
            case 'water':
                weaknesses.extend(['electric', 'grass'])
                resistances.extend(['fire', 'water', 'ice', 'steel'])
                immunities.extend([])
            case 'electric':
                weaknesses.extend(['ground'])
                resistances.extend(['electric', 'flying', 'steel'])
                immunities.extend([])
            case 'grass':
                weaknesses.extend(['fire', 'ice', 'poison', 'flying', 'bug'])
                resistances.extend(['water', 'electric', 'grass', 'ground'])
                immunities.extend([])
            case 'ice':
                weaknesses.extend(['fire', 'fighting', 'rock', 'steel'])
                resistances.extend(['ice'])
                immunities.extend([])
            case 'fighting':
                weaknesses.extend(['flying', 'psychic', 'fairy'])
                resistances.extend(['bug', 'rock', 'dark'])
                immunities.extend([])
            case 'poison':
                weaknesses.extend(['ground', 'psychic'])
                resistances.extend(['grass', 'fighting', 'poison', 'bug', 'fairy'])
                immunities.extend([])
            case 'ground':
                weaknesses.extend(['water', 'grass', 'ice'])
                resistances.extend(['poison', 'rock'])
                immunities.extend(['electric'])
            case 'flying':
                weaknesses.extend(['electric', 'ice', 'rock'])
                resistances.extend(['grass', 'fighting', 'bug'])
                immunities.extend(['ground'])
            case 'psychic':
                weaknesses.extend(['bug', 'ghost', 'dark'])
                resistances.extend(['fighting', 'psychic'])
                immunities.extend([])
            case 'bug':
                weaknesses.extend(['fire', 'flying', 'rock'])
                resistances.extend(['grass', 'fighting', 'ground'])
                immunities.extend([])
            case 'rock':
                weaknesses.extend(['water', 'grass', 'fighting', 'ground', 'steel'])
                resistances.extend(['normal', 'fire', 'poison', 'flying'])
                immunities.extend([])
            case 'ghost':
                weaknesses.extend(['ghost', 'dark'])
                resistances.extend(['poison', 'bug'])
                immunities.extend(['normal', 'fighting'])
            case 'dragon':
                weaknesses.extend(['ice', 'dragon', 'fairy'])
                resistances.extend(['fire', 'water', 'electric', 'grass'])
                immunities.extend([])
            case 'dark':
                weaknesses.extend(['fighting', 'bug', 'fairy'])
                resistances.extend(['ghost', 'dark'])
                immunities.extend(['psychic'])
            case 'steel':
                weaknesses.extend(['fire', 'fighting', 'ground'])
                resistances.extend(['normal', 'grass', 'ice', 'flying', 'psychic', 'bug', 'rock', 'dragon', 'steel', 'fairy'])
                immunities.extend(['poison'])
            case 'fairy':
                weaknesses.extend(['poison', 'steel'])
                resistances.extend(['fighting', 'bug', 'dark'])
                immunities.extend(['dragon'])
            case _:
                weaknesses.extend(['error'])  

    for resistance in resistances:
        if weaknesses.count(resistance) > 0:
            weaknesses.remove(resistance)
    
    for immunity in immunities:
        if weaknesses.count(immunity) > 0:
            weaknesses.remove(immunity)
    
    return weaknesses

load_dotenv(dotenv_path='C:\\Users\\Marcos Felipe\\Documents\\Projects\\python\\pokedex\\.env')
TOKEN = os.getenv('DISCORD_TOKEN')

def main():
    bot.run(token=TOKEN)

if __name__ == '__main__':
    main()