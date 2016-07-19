from bs4 import BeautifulSoup as bs
from urllib2 import urlopen as wget
import MySQLdb as sql
import sys

URL = "http://bulbapedia.bulbagarden.net"
db = sql.connect("localhost","root","Metroid","pokedb" )
cursor = db.cursor()

def initDB():    
    scripts = [
        "DROP TABLE pokemon;",
        "CREATE TABLE pokemon( id serial, name CHAR(30) PRIMARY KEY, category CHAR(50), natdex INTEGER, type CHAR(30), region CHAR(30));",
    ]
    
    for script in scripts:
        cursor.execute(script)
        out = cursor.fetchone()
        if out:
            print out

    return cursor

def populateList():
    '''first, we get the whole list of pokemon, sorted by national dex number.
    there is also a regional dex number, which i will preserve later.
    returns a tuple in the form (name, url_suffix).
    '''
    path = URL + "/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
    page = wget(path)
    soup = bs(page.read(), 'html.parser')
    tables = soup.findAll('table')

    # - tables[1] is the list of kanto (kdex) pokemon.
    # - tables[2] is the list of jhoto (jdex) pokemon.
    # - tables[3] is the list of hoenn (hdex) pokemon.
    # - tables[4] is the list of sinnoh (sdex) pokemon.
    # - tables[5] is the list of unova (udex) pokemon.
    # - tables[6] is the list of kalos pokemon. kalos is special because the region is 
    #     split into 3 sub regions, central (cekdex), coastal (cokdex), and mountain (mokdex).
    # - tables[7] is the list of alola (adex) pokemon. it is not populated, as the region 
    #     is part of the gen VII game release (not released yet).

    # get a list of pokemon
    pokemon = []
    for table in tables[:7]:    # ignoring alola region for now
        entries = bs(table.__str__(), 'html.parser').findAll('tr')
        for entry in entries[1:]:   # entries[0] defines column headers.
            entry = bs(entry.__str__(), 'html.parser')
            info = entry.findAll('td')[3]
            poke = (info.a.contents[0], info.a['href'])
            if poke not in pokemon:     # there are duplicate entries. some pokemon have different "states".
                pokemon.append(poke)    # using a dictionary reorders, lets stay in order for debugging's sake.

    return pokemon

def cullPokemonData(pokeTuple):
    path = URL + pokeTuple[1]
    page = wget(path)
    soup = bs(page.read(), 'html.parser')
    table = soup.find('table', {'class':'roundy', 'style': 'float:right; text-align:center; width:33%; max-width:420px; min-width:360px; background: #78C850; border: 2px solid #682A68; padding:2px;'})

    name     = ""
    category = ""
    natdex   = ""
    _type    = ""
    region   = ""

    # script = "INSERT INTO pokemon(name, category, natdex, type, region) VALUES ()"
    # try:
    #     cursor.execute(script)
    #     out = cursor.fetchone()
    #     if out:
    #         print out
    #     db.commit()
    # except:
    #     db.rollback()


# ------ BEGIN ROUTINE -------
sys.stdout.write("Initializing Database...")
cursor = initDB()

sys.stdout.write("done.\nGetting list of Pokemon (up to Gen6)...")
pokedex = populateList()

print "done.\nStarting Database Insertions."

sys.stdout.write("Processing " + pokedex[0][0] + "...") # separate the first one for console output's sake
cullPokemonData(pokedex[0])
# for pokemon in pokedex[1:]:
#     sys.stdout.write("done.\nProcessing " + pokemon[0] + "...")
#     cullPokemonData(pokemon)

print "done.\nDatabase construction complete."
# cleanup
db.close()