# -*- coding: utf-8 -*-

# time it!
import time
start = time.time()

from bs4 import BeautifulSoup as bs
from urllib2 import urlopen as wget
import MySQLdb as sql
import sys, re
from pprint import pprint

# setup
URL = "http://bulbapedia.bulbagarden.net"
db = sql.connect("localhost","root","Metroid","pokedb" )
cursor = db.cursor()


def initDB():
    """Initializes a fresh pokemon table in pokedb."""
    scripts = [
        "DROP TABLE pokemon;",
        "CREATE TABLE pokemon(id serial, name CHAR(30), category CHAR(50), natdex CHAR(5) PRIMARY KEY, type CHAR(30));",
    ]
    
    for script in scripts:
        cursor.execute(script)
        out = cursor.fetchone()
        if out:
            print out


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
    '''Grabs data for a single pokemon.'''
    path  = URL + pokeTuple[1]
    page  = wget(path)
    sys.stdout.write(".")
    soup  = bs(page.read(), 'html.parser')
    table = soup.find('table', {'class':'roundy'})
    
    # at this point, I have the right table. need to parse out the following values.
    element  = table.find("td", {"width" : "50%"})
    name     = element.big.big.b.contents[0]
    if "Nidoran" in name:
        name = name[:-1]
    # print "name >>>", name # debug

    # to account for inline explain spans
    if len(element.a.span.contents) > 1:
        category = element.a.span.span.contents[0] + element.a.span.contents[1]
    else:
        category = element.a.span.contents[0]
    category = re.sub("\xe9", "e", category)
    # print "cat >>>", category # debug
    
    sys.stdout.write(".")
    
    element = table.find("th", {"width" : "25%", "class" : "roundy", "style" : "background:#FFF;"})
    natdex  = element.big.big.a.span.contents[0]
    # print "natdex >>>", natdex # debug
    
    _type = ""
    element = table.find("td", {"class" : "roundy", "colspan" : "4"})
    types = element.findAll("td")
    if types[0].a.span.b is None:
        element = table.find("td", {"class" : "roundy", "colspan" : "2"})
    element = element.table.tr.td.table.tr
    types = element.findAll("td")
    for t in types:
        if t.a.span.b.contents[0] != "Unknown":
            _type += t.a.span.b.contents[0] + " "    
    # print "type >>>", _type # debug
    
    sys.stdout.write(".")
    script = 'INSERT INTO pokemon(name, category, natdex, type) VALUES ("%s", "%s", "%s", "%s")' % (name, category, natdex, _type)
    try:
        cursor.execute(script)
        out = cursor.fetchone()
        if out:
            print out
        db.commit()
    except:
       db.rollback()


def viewDatabase():
    '''Prints the data currently in the database.'''
    dbstart = time.time()
    cursor.execute("SELECT * FROM pokemon;")
    print "Table 'pokemon':"
    results = cursor.fetchall()
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
sys.stdout.write("Initializing Database...")
initDB()
sys.stdout.write("done.\nGetting list of Pokemon (up to Gen6)...")
pokedex = populateList()
print "done.\nStarting Database Insertions."
sys.stdout.write("Processing " + pokedex[0][0]) # separate the first one for console output's sake
cullPokemonData(pokedex[0])
for pokemon in pokedex[1:]:
    sys.stdout.write("done.\nProcessing " + re.sub(u'\u2642', ' (Male)', re.sub(u'\u2640', ' (Female)', pokemon[0])))
    cullPokemonData(pokemon)
print "done.\nDatabase construction complete."
viewDatabase()
# cleanup
db.close()
last = 'Routine complete in {0:.2f} seconds.'.format(time.time()-start)
for i in range(len(last)):
    sys.stdout.write("=")
print "\n" + last

# maybe do this for a percentage completion updater in the console:
"""
from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

from time import sleep

def hello(name):
    print "Hello %s!" % name

print "starting..."
rt = RepeatedTimer(1, hello, "World") # it auto-starts, no need of rt.start()
try:
    sleep(5) # your long-running job goes here...
finally:
    rt.stop() # better in a try/finally block to make sure the program ends!
"""

# data to grab next:
#     abilities
#     gender ratio
#     catch rate
#     egg groups
#     hatch time
#     height (us customary)
#     height (metric)
#     weight (us customary)
#     weight (metric)
#     regional pokedex numbers
#     base experience yeild
#     levelling rate
#     ev yield
#     body style
#     foot print
#     image
#     pokedex color
#     base friendship
