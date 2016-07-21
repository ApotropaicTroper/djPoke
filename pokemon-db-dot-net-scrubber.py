# -*- coding: utf-8 -*-

import time
start = time.time()

from bs4 import BeautifulSoup as bs
from urllib2 import urlopen as wget
import MySQLdb as sql
import sys, re
from pprint import pprint

# setup
URL = "http://pokemondb.net/pokedex"
db = sql.connect("localhost","root","Metroid","pokedb" )
cursor = db.cursor()


def initDB():
    """Initializes a fresh pokemon table in pokedb."""
    scripts = [
        "DROP TABLE IF EXISTS pokemon;",
        """CREATE TABLE pokemon(
            id              serial PRIMARY KEY,
            name            CHAR(30),
            natdex          CHAR(5),
            hp              INT,
            attack          INT,
            defense         INT,
            special_attack  INT,
            special_defense INT,
            speed           INT,
            url             TEXT
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
    path = URL + "/all"
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

def viewTable(table):
    '''Prints the data currently in the database.'''
    dbstart = time.time()
    cursor.execute("SELECT * FROM %s;" % table) 
    print "Table '%s':" % table
    results = cursor.fetchall()
    if not results:
        print "Empty set ({0:.2f} sec)".format(time.time()-dbstart)
        return
    widths = []
    columns = []
    tavnit = '|'
    separator = '+' 
    for cd in cursor.description:
        widths.append(max(cd[2], len(cd[0])))
        columns.append(cd[0])
    for w in widths:
        tavnit += " %-"+"%ss |" % (w,)
        separator += '-'*w + '--+'
    print(separator)
    print(tavnit % tuple(columns))
    print(separator)
    for row in results:
        print(tavnit % row)
    print(separator)
    print str(len(results)) + " rows in set ({0:.2f} sec)".format(time.time()-dbstart)


# ------ BEGIN ROUTINE -------
# sys.stdout.write("Initializing Database...")
initDB()
# sys.stdout.write("done.\nGetting list of Pokemon (up to Gen6)...")
populateList()
viewTable('pokemon')
db.close()
last = 'Routine complete in {0:.2f} seconds.'.format(time.time()-start)
for i in range(len(last)):
    sys.stdout.write("=")
print "\n" + last