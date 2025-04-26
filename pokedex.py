import os
import requests
import logging
from dotenv import load_dotenv
from discord import Intents, Interaction, Object, app_commands
from discord.ext.commands import Bot
from discord.abc import Snowflake
from discord.app_commands import Choice

logger = logging.getLogger()
handler = logging.FileHandler(filename='pokedex.log', mode='w', encoding='utf-8')
logger.addHandler(handler)

intents: Intents = Intents.default()
intents.message_content = True

bot: Bot = Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} is now running!')
    
    try:
        for guild in bot.guilds:
            await bot.tree.sync(guild=guild)
            logger.info(f'Synced to {guild.name} (ID: {guild.id})')   
    except Exception as e:
        logger.error(e)

load_dotenv()

guilds_id: list[Snowflake] = list(map(lambda guild_id: Object(id=guild_id), os.getenv('GUILDS_ID').split(',')))

async def pokemon_autocomplete(interaction: Interaction, current: str) -> list[Choice[str]]:
    pokemons = ['pikachu', 'bulbasaur', 'squirtle', 'charmander']
    return [Choice(name=pokemon, value=pokemon) for pokemon in pokemons if current.lower() in pokemon.lower()]

# @commands.command(name='pokedex')
@bot.tree.command(name='pokedex', description='get information about a pokemon', guilds=guilds_id)
@app_commands.describe(pokemon='name of the pokemon you wish to search')
@app_commands.autocomplete(pokemon=pokemon_autocomplete)
# @app_commands.choices(pokemon=[Choice(name='pikachu', value=1), Choice(name='bulbasaur', value=2), Choice(name='squirtle', value=3)])
async def search_pokemon(interaction: Interaction, pokemon: str):  
    info: dict[any] | None = get_pokemon_info(pokemon)
    
    if info:
        msg: str = format_pokemon_info(info)
    else:
        msg: str = "Pokemon not Found"
    
    try:
        await interaction.response.send_message(content=msg, delete_after=300.0)
        logger.info(f'{interaction.guild.name} {interaction.user} {pokemon}')
    except Exception as e:
        logger.error(e)  
    

# async def handle_response(response: InteractionResponse, msg: str):
#     response.send_message(msg)
#     response.edit_message(delete_after=5.0)

def get_pokemon_info(name: str) -> dict | None:
    base_url: str = 'https://pokeapi.co/api/v2/'
    url: str = f'{base_url}/pokemon/{name}'
    response = requests.get(url)

    if response.status_code == 200:
        logger.info(f'Data retrieved')
        pokemon_data: dict = response.json()
        return pokemon_data
    else:
        logger.debug(f'Failed to retrieve data {response.status_code}')

def format_pokemon_info(info: dict[any]) -> str:
        
    name: str = info['name']
    height: int = info['height']
    weight: int = info['weight']
    types: list = info['types']
    
    # print(f"{type} {len(types)}")
    
    output: str = f'Name:    {name.capitalize()}\n'
    
    for index, type in enumerate(types):
        type: dict = type['type']
        type: str = type['name']
        if len(types) <= 1:
            output += f'Type:    {type.capitalize()}\n'
            break
        else:
            output += f'Type {index + 1}:    {type.capitalize()}\n'
    
    output += f'Height:    {height / 10}m\n'
    output += f'Weight:    {weight / 10}kg'
    
    return output

# @bot.event
# async def on_app_command_completion(interaction: Interaction, _command: Command):
#     try:
#         print(interaction.message)
#     except Exception as e:
#         print(e)

TOKEN = os.getenv('DISCORD_TOKEN')

def init():
    bot.run(token=TOKEN, root_logger=True, log_handler= handler)