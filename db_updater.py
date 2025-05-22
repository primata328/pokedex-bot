import requests
import json
import pickle

def update(url, count):
    url = f'{url}/?offset=0&limit={count}'
    response = requests.get(url)

    data = json.loads(response.content)

    pokemons = data['results']
    pokemon_names = []

    for pokemon in pokemons:
        name = pokemon['name']
        pokemon_names.append(name)
        
    pickle.dump(pokemon_names, 'pokenames.data')

def main():
    url = 'https://pokeapi.co/api/v2/pokemon'
    response = requests.get(url)

    data = json.loads(response.content)
    count = data['count']

    with open('pokenames.data', 'rb') as file:
        db = pickle.load(file)

    db_count = len(db)

    if db_count < count:
        update(url, count)
        
if __name__ == '__main__':
    main()
    