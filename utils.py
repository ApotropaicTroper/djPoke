"""
Script containing useful functions I use frequently.
Project independent.

Leland Sperl
21 July 2016
"""

import time # imported here so that the execution time measurements don't include the import execution

def viewTable(cursor, table, cols):
    '''Prints data currently in the local database instance, given a cursor.
    Output looks exactly like the mysql function "select * from table;".
    http://stackoverflow.com/questions/10865483/print-results-in-mysql-format-with-python
    '''
    dbstart = time.time()
    cursor.execute("SELECT %s FROM %s;" % (cols, table))
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


def dedupe(seq):
    '''Unique-ifies a list. Fastest transaction as per benchmark tests.
    http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order#
    '''
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]