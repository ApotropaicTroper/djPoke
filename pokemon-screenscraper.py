from bs4 import BeautifulSoup as bs
from urllib2 import urlopen as wget

URL = "http://bulbapedia.bulbagarden.net"

def initDB():
    import sqlite3
    sqlite_file = 'pokebase.sqlite3'    # name of the sqlite database file
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    scripts = [
        "CREATE TABLE IF NOT EXISTS pokemon( id TEXT PRIMARY KEY, name TEXT, category TEXT, natdex INTEGER, type TEXT, region TEXT);",
        "SELECT name FROM sqlite_master WHERE type='table';",
    ]
    # Creating a new SQLite table with 1 column
    for script in scripts:
        c.execute(script)
    print(c.fetchall())
    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

def populateList():
    '''first, we get the whole list of pokemon, sorted by national dex number.
    there is also a regional dex number, which i will preserve later.
    returns a tuple in the form (name, url_suffix).
    '''
    path = "http://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
    soup = bs(wget(path).read(), 'lxml')
    tables = soup.findAll('table', {'align':'center'})

    # - tables[0] is the list of kanto (kdex) pokemon.
    # - tables[1] is the list of jhoto (jdex) pokemon.
    # - tables[2] is the list of hoenn (hdex) pokemon.
    # - tables[3] is the list of sinnoh (sdex) pokemon.
    # - tables[4] is the list of unova (udex) pokemon.
    # - tables[5] is the list of kalos pokemon. kalos is special because the region is 
    #   split into 3 sub regions, central (cekdex), coastal (cokdex), and mountain (mokdex).
    # - tables[6] is the list of alola (adex) pokemon. it is not populated, as the region 
    #   is part of the gen VII game release (not released yet).

    # get a list of pokemon
    pokemon = []
    for table in tables[:6]:    # ignoring alola region for now
        entries = bs(table.__str__(), 'lxml').findAll('tr')
        for entry in entries[1:]:   # entries[0] defines column headers.
            entry = bs(entry.__str__(), 'lxml')
            info = entry.findAll('td')[3]
            poke = (info.a.contents[0], info.a['href'])
            if poke not in pokemon:     # there are duplicate entries. some pokemon have different "states".
                pokemon.append(poke)    # using a dictionary reorders, lets stay in order for debugging's sake.

    # for item in pokemon:
    #     print item
    # print 'length:', len(pokemon)
    return pokemon

def cullPokemonData(id):
    path = URL + id[1]
    soup = bs(wget(path).read(), 'lxml')

pokedex = populateList()
#cullPokemonData(pokedex[0])
initDB()


# for pokemon in pokedex:
#     cullPokemonData(pokemon)
#     break