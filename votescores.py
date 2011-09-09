import sqlite3
import urllib2
import re
import csv
from BeautifulSoup import BeautifulSoup

# Start SQLite connection.
db = sqlite3.connect('./tweets')
sql = db.cursor()

FILES = ["conscores-sen.csv", "conscores-house.csv"]
URLs = ["http://thatsmycongress.com/senate/index.html",
        "http://thatsmycongress.com/house/index.html"]

# Scraping liberal-biased scores from That's My Congress.
# May only use these scores, depending on merge difficulty.
senators = {}
reps = {}
for url in URLs:
    scrapingReps = False
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html)

    for tag in soup.findAll('tr'):
        for link in tag.findAll('a'):
            if u"Senator" in link.contents[0]:
                name = link.contents[0].encode('utf-8')
                index = name.find(' ', 8, -1)
                lastname = name[index + 1:].lower()
                senators.setdefault(lastname, {})
                senators[lastname].setdefault('lib', 0)

            elif u"Rep." in link.contents[0]:
                name = link.contents[0].encode('utf-8')
                index = name.find(' ', 5, -1)
                lastname = name[index + 1:].lower()
                reps.setdefault(lastname, {})
                reps[lastname].setdefault('lib', 0)
                scrapingReps = True

        for score in tag.findAll('td'):
            try:
                if u"Net" in score.contents[0] and scrapingReps:
                    reps[lastname]['lib'] = int(re.sub(r'[a-zA-Z:]', '', 
                                                score.contents[0]))
                elif u"Net" in score.contents[0]:
                    senators[lastname]['lib'] = int(re.sub(r'[a-zA-Z:]', '', 
                                                    score.contents[0]))
            except IndexError:
                continue

print senators, reps

# Scraping conservative-biased scores from conservative.org.
# Data was copied, pasted, modified into nice CSVs.
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

# Adding data to SQLite db.
#sql.execute("create table reps (name text, conscore int, libscore int)")
#for name in reps:
#    t = (name, reps[name])
#    sql.execute("insert into tweets (name,conscore,libscore) values (?,?,?)", t)

#sql.execute("create table senators (name text, conscore int, libscore int)")
#for name in senators:
#    t = (name, senators[name])
#    sql.execute("insert into tweets (name,conscore,libscore) values (?,?,?)", t)
