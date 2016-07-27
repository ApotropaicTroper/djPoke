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
            id                serial PRIMARY KEY,   -- to preserve uniqueness. there are duplicate entries for netdex.
            name              CHAR(30),
            natdex            CHAR(5),
            hp                INT,                  -- baseline stats  |
            attack            INT,                  --                 |
            defense           INT,                  --                 |
            special_attack    INT,                  --                 |
            special_defense   INT,                  --                 |
            speed             INT,                  --                 |
            type              CHAR(20),
            category          CHAR(40),
            height            CHAR(20),             -- format: us (metric)
            weight            CHAR(20),             -- format: us (metric)
            abilities         CHAR(40),             -- space-delimited list
            dex_locales       TEXT,                 -- python dictionary of region : value
            name_japanese     CHAR(40),
            ev_yield          TEXT,
            catch_rate        TEXT,                 -- value, (aside)
            base_happiness    TEXT,                 -- value, (aside)
            base_xp           INT,
            leveling_rate     CHAR(30),
            egg_groups        CHAR(30),             -- space-delimited list
            gender_ratio      CHAR(30),             -- comma-delimited list
            hatch_rate        CHAR(25),             -- format: rate (min steps)
            type_defenses     TEXT,                 -- python diction of type : effectiveness
            version_dex_descs TEXT,                 -- python diction of (version) : entry
            form              INT,                  -- the alternate form identifier. ie, charizard is 1, mega charizard X is 2, Y is 3.
            mega              BOOL,                 -- is it a mega evolution? TRUE if yes.
            url               TEXT
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
    forms = []
    form = 1
    for result in results:
        num = result.contents[1]
        if len(dexnums) > 0 and num == dexnums[-1]:
            form += 1
        else:
            form = 1
        dexnums.append(num)
        forms.append(form)

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

    # get types
    results = soup.findAll("td", {"class":"cell-icon"})
    types = []
    for result in results:
        result = result.findAll("a")
        ptype = ""
        for res in result:
            ptype += res.contents[0] + " "
        types.append(ptype)

    # build a list of pokemon
    pokemon = []
    for i in range(len(dexnums)):
        mega = 0
        if names[i].startswith("Mega "):
            mega = 1
        pokemon.append((names[i], dexnums[i], hps[i], attacks[i], defenses[i], spattacks[i], spdefenses[i], speeds[i], types[i], urls[i], forms[i], mega))
    
    # write set to database
    for poke in pokemon:
        script = 'INSERT INTO pokemon(name, natdex, hp, attack, defense, special_attack, special_defense, speed, type, url, form, mega) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % poke
        try:
            cursor.execute(script)
            out = cursor.fetchone()
            if out:
                print out
            db.commit()
        except:
           db.rollback()
    return [names, urls]

def cullPokemonData(pokemon):
    '''Grabs data for a specific pokemon to append to the table.
    Accepts 2-tuple of a name and a page under the "pokemondb.net" domain.
    '''
    path = URL + pokemon[1]
    page = wget(path)
    soup = bs(page.read(), 'html.parser')

    category = soup.find("q")
    info = soup.findAll("table", {"class":"vitals-table"})
    print info[8]

    """
    For a standard (no alternate forms) page, the following holds:
        - info[0] contains natdex, type, category, height, weight, abilities, localdex, and japanese name
        - info[1] contains EV yield, catch rate, base friendship (happiness), base xp, and growth rate
        - info[2] contains egg groups, gender ratio, and hatch rate
        - info[3] contains stat total, hp, attack, defense, sp. attack, sp. defense, and speed
        - info[4] contains pokedex descriptions from various different games
        - info[5] contains locations the pokemon can be found
    For pokemon with more than one form on a page, the following holds:
        - info[0] to info[3] represent the first form
        - info[4] to info[7] represent the second form
        - info[8] to info[11] represent the third form
        - ...and so on
        - the last two elements of info contain pokedex descriptions from various different games and locations the pokemon can be found.

    """


# ------ BEGIN ROUTINE -------
sys.stdout.write("Initializing Database...")
initDB()

sys.stdout.write("done.\nGetting list of Pokemon (up to Gen6)...")
pokes = populateList()
# pokes = zip(*pokes)

print "done.\nInserting Pokemon data..."
# pokes = dedupe(pokes)
# for poke in pokes:
#     print ">>> processing", poke[0]
#     cullPokemonData(poke)
#     break
# cullPokemonData(["Charizard", "/pokedex/charizard"])

# viewTable(cursor, 'pokemon', 'id, natdex, name, form, mega')
# db.close()
# last = 'Routine complete in {0:.2f} seconds.'.format(time.time()-start)
# for i in range(len(last)):
#     sys.stdout.write("=")
# print "\n" + last