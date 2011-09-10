import sqlite3
import urllib2
import re
import csv
from BeautifulSoup import BeautifulSoup

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
#                    index = name.find(' ', 8, -1)
#                    lastname = name[index + 1:].lower()
#                    # Clean last names one more time--we don't want middle 
#                    # names!
#                    if lastname.find(' ') is not -1:
#                        index = lastname.find(' ')
#                        lastname = lastname[index + 1:]
                    senators.setdefault(name, {})
                    senators[name].setdefault('lib', 0)

                elif u"Rep." in link.contents[0]:
                    name = link.contents[0].encode('utf-8')
                    name = name[name.find(' ') + 1:]
#                    index = name.find(' ', 5, -1)
#                     lastname = name[index + 1:].lower()
#                     # Same as above--drop all middle names.
#                     if lastname.find(' ') is not -1:
#                         index = lastname.find(' ')
#                         lastname = lastname[index + 1:]
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

    sql.execute("drop table reps")
    sql.execute("drop table senators")    
    try:
        sql.execute("create table reps (name text, libscore int)")
        sql.execute("create table senators (name text, libscore int)")
    except sqlite3.OperationalError:
        pass

    try:
        for name in reps:
            t = (name, reps[name]['lib'])
            sql.execute("insert into reps (name,libscore) values (?,?)", t)

        for name in senators:
            t = (name, senators[name]['lib'])
            sql.execute("insert into senators (name,libscore) values (?,?)", t)
    except sqlite3.InterfaceError:
        if name in reps:
            print name, reps[name]
        else:
            print name, senators[name]

def main():
    # Start SQLite connection.
    db = sqlite3.connect('./tweets')
    db.text_factory = str
    sql = db.cursor()

    # Add scores to db.
    senators, reps = get_liberal_scores()
    update_sql_db(senators, reps, sql)

    # Commit changes.
    db.commit()
