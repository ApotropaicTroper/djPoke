# -*- coding: utf-8 -*-

import time
start = time.time()

from bs4 import BeautifulSoup as bs
from urllib2 import urlopen as wget
import MySQLdb as sql
import sys, re
from pprint import pprint
from utils import dedupe, viewTable

# setup
URL = "http://pokemondb.net"
db = sql.connect("localhost","root","Metroid","pokedb" )
cursor = db.cursor()


def initDB():
    """Initializes a fresh pokemon table in pokedb."""
    scripts = [
        "DROP TABLE IF EXISTS pokemon;",
        """CREATE TABLE pokemon(
            id                serial PRIMARY KEY,   # to preserve uniqueness. there are duplicate entries for netdex.
            name              CHAR(30),
            natdex            CHAR(5),
            hp                INT,        # baseline stats ---
            attack            INT,        #                 |
            defense           INT,        #                 |
            special_attack    INT,        #                 |
            special_defense   INT,        #                 |
            speed             INT,        #                ---
            url               TEXT,
            type              CHAR(20),
            category          CHAR(40),
            height            CHAR(20),   # format: us (metric)
            weight            CHAR(20),   # format: us (metric)
            abilities         CHAR(40),   # space-delimited list
            dex_locales       TEXT,       # python dictionary of region : value
            name_japanese     CHAR(40),
            ev_yield          TEXT,
            catch_rate        TEXT,       # value, (aside)
            base_happiness    TEXT,       # value, (aside)
            base_xp           INT,
            leveling_rate     CHAR(30),
            egg_groups        CHAR(30),   # space-delimited list
            gender_ratio      CHAR(30),   # comma-delimited list
            hatch_rate        CHAR(25),   # format: rate (min steps)
            type_defenses     TEXT,       # python diction of type : effectiveness
            version_dex_descs TEXT        # python diction of (version) : entry
        );""",
    ]
    
    for script in scripts:
        cursor.execute(script)
        out = cursor.fetchone()
        if out:
            print out


def populateList():
    '''first, we get the whole list of pokemon, including national pokedex numbers, baseline stats, and
    the associated URLs. inserts those values into the database.
    '''
    path = URL + "/pokedex/all"
    page = wget(path)
    soup = bs(page.read(), 'html.parser')
    table = soup.find("table", {"id" : "pokedex"})
    
    # gets pokedex numbers and if mega evolution
    results = table.findAll("td", {"class" : "num cell-icon-string"})
    dexnums = []
    for result in results:
        dexnums.append(result.contents[1])

    
    # gets names and associated entry URLs
    results = table.findAll("a", {"class" : "ent-name"})
    names = []
    urls = []
    for result in results:
        if result.parent.small:
            if "Mega" in result.parent.small.contents[0]:
                names.append(result.parent.small.contents[0])
            else:
                names.append(result.contents[0] + " " + result.parent.small.contents[0])
        else:
            names.append(re.sub(u'\u2642', ' (Male)', re.sub(u'\u2640', ' (Female)', result.contents[0])))
        urls.append(result['href'])

    # gets stat-lines
    results = table.findAll("td", {"class" : "num"})
    hps        = [] #0
    attacks    = [] #1
    defenses   = [] #2
    spattacks  = [] #3
    spdefenses = [] #4
    speeds     = [] #5
    counter = 0
    for result in results:
        if not result.i:
            if counter == 0:
                hps.append(result.contents[0])
            elif counter == 1:
                attacks.append(result.contents[0])
            elif counter == 2:
                defenses.append(result.contents[0])
            elif counter == 3:
                spattacks.append(result.contents[0])
            elif counter == 4:
                spdefenses.append(result.contents[0])
            elif counter == 5:
                speeds.append(result.contents[0])
            counter += 1
            if counter == 6:
                counter = 0
    # for i in range(len(hps)):
    #     print hps[i], attacks[i], defenses[i], spattacks[i], spdefenses[i], speeds[i]

    # build a list of pokemon
    pokemon = []
    for i in range(len(dexnums)):
        pokemon.append((names[i], dexnums[i], hps[i], attacks[i], defenses[i], spattacks[i], spdefenses[i], speeds[i], urls[i]))
    
    # write set to database
    for poke in pokemon:
        script = 'INSERT INTO pokemon(name, natdex, hp, attack, defense, special_attack, special_defense, speed, url) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % poke
        try:
            cursor.execute(script)
            out = cursor.fetchone()
            if out:
                print out
            db.commit()
        except:
           db.rollback()
    return urls

def cullPokemonData(url):
    '''Grabs data for a specific pokemon to append to the table.'''
    path = URL + url
    page = wget(path)
    soup = bs(page.read(), 'html.parser')

# ------ BEGIN ROUTINE -------
sys.stdout.write("Initializing Database...")
initDB()
sys.stdout.write("done.\nGetting list of Pokemon (up to Gen6)...")
urls = populateList()
print "done.\nGetting the rest of the Pokemon data..."
urls = dedupe(urls)
for url in urls:
    print ">>> processing", url[9:]
    cullPokemonData(url)
    break
# viewTable(cursor, 'pokemon')
db.close()

last = 'Routine complete in {0:.2f} seconds.'.format(time.time()-start)
for i in range(len(last)):
    sys.stdout.write("=")
print "\n" + last