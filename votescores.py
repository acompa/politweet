import sqlite3
import urllib2
import re
import csv

from BeautifulSoup import BeautifulSoup
from scraper import access_sql_db

def get_liberal_scores():
    """
    Scraping liberal-biased scores from That's My Congress.
    May only use these scores, depending on merge difficulty.
    """

    URLs = ["http://thatsmycongress.com/senate/index.html",
            "http://thatsmycongress.com/house/index.html"]
    senators = {}
    reps = {}
    scrapingReps = False

    # Open URLs and save HTML via Beautiful Soup.
    for url in URLs:
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html)

        # Start scraping names.
        for tag in soup.findAll('tr'):
            for link in tag.findAll('a'):
                if u"Senator" in link.contents[0]:
                    name = link.contents[0].encode('utf-8')
                    name = name[name.find(' ') + 1:]
                    senators.setdefault(name, {})
                    senators[name].setdefault('lib', 0)

                elif u"Rep." in link.contents[0]:
                    name = link.contents[0].encode('utf-8')
                    name = name[name.find(' ') + 1:]
                    reps.setdefault(name, {})
                    reps[name].setdefault('lib', 0)
                    scrapingReps = True

            # Scrape scores for each legislator.
            for score in tag.findAll('td'):
                try:
                    if u"Net" in score.contents[0] and scrapingReps:
                        reps[name]['lib'] = int(re.sub(r'[a-zA-Z:]', '', 
                                                score.contents[0]))
                    elif u"Net" in score.contents[0]:
                        senators[name]['lib'] = int(re.sub(r'[a-zA-Z:]', '', 
                                                    score.contents[0]))
                except IndexError:
                    continue

    return senators, reps


def get_conservative_scores():
    """
    Scraping conservative-biased scores from conservative.org.
    Data was copied, pasted, modified into nice CSVs.
    """
    scrapingReps = False
    for file in FILES:

        # Bool for reps (and not senators).
        if file is "conscores-house.csv":
            scrapingReps = True

        with open(file, 'r') as f:
            data = csv.reader(f)

            # Skip rows without names. Otherwise, save the last name, strip
            # any non-alphanum chars.
            for row in data:
                if len(str(row[0])) > 2:
                    continue
                else:
                    name = row[1]
                    if name.find(',') is not -1:
                        name = name[:name.find(',')]
                    name = re.sub(r'\W', '', name).lower().encode('utf-8')
                
                    # Does the name match something in the senator/rep dict
                    # already? Update the dict. If not, print the name for manual 
                    # debug.
                    with open('missing.txt', 'w') as out:
                        if scrapingReps:
                            if name in reps:
                                reps[name].setdefault('con', float(row[2]))
                            else:
                                print "MISSING: Rep. %s" % name
                                out.write("Rep. %s\n" % name)
                        else:
                            if name in senators:
                                senators[name].setdefault('con', float(row[2]))
                            else:
                                print "MISSING: Sen. %s" % name
                                out.write("Sen. %s\n" % name)

def update_sql_db(senators, reps, sql):
    """ Adding data to SQLite db. """

    # Recreating table with each run. Not efficient, but this is shortcut
    # code while I alter table structure to facilitate merge.
    sql.execute("drop table reps")
    sql.execute("drop table senators")    
    sql.execute("""create table reps (firstname text, lastname text, 
                libscore int)""")
    sql.execute("""create table senators (firstname text, lastname text, 
                libscore int)""")

    # Take names, split them into first/last names, then add all to SQLite.
    try:
        for name in reps:
            fname, lname = split_full_name(name)
            t = (fname, lname, reps[name]['lib'])
            sql.execute("""insert into reps (firstname,lastname,libscore) 
                        values (?,?,?)""", t)

        for name in senators:
            fname, lname = split_full_name(name)
            t = (fname, lname, senators[name]['lib'])
            sql.execute("""insert into senators (firstname,lastname,libscore)
                        values (?,?,?)""", t)
    except sqlite3.InterfaceError:
        if name in reps:
            print name, reps[name]
        else:
            print name, senators[name]

# Utility functions for formatting text.
def split_full_name(name):
    """ Splits full names into first and last names. """
    index = name.find(' ')
    fname = name[:index]
    lname = name[index + 1:]
    return fname, lname

# Final script.
def main():
    # Start SQLite connection.
    sql = access_sql_db()

    # Add scores to db.
    senators, reps = get_liberal_scores()
    update_sql_db(senators, reps, sql)

    # Commit changes.
    db.commit()
