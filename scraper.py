import tweepy
import sqlite3
import csv
from creds import C_KEY, C_SECRET, A_TOKEN, A_SECRET
from time import sleep
from sys import exit


def twitter_auth():
    """ Authenticate with Twitter. """
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_SECRET)
    return tweepy.API(auth)

def access_sql_db():
    """ Instantiate SQLite db and table for tweets. """
    db = sqlite3.connect('data/tweets')
    db.text_factory = str
    sql = db.cursor()
    return db, sql

def scrape_timeline(row, API, sql):
    """ Scrape legislator's timeline. """

    PAGE = 1
    party = row[3]
    id = row[4]

    print """
    *******
    ** Now scraping %s's (%s) timeline...
    *******""" % (id, party)

    requests_left = API.rate_limit_status()['remaining_hits']
    while requests_left < 20:
        print """
    !!!!!!!
    !! Approaching rate limit--%i requests left! Waiting a bit...
    !!!!!!!""" % requests_left
        sleep(600)
        requests_left = API.rate_limit_status()['remaining_hits']
        
    # Scrape tweets for politician until there are no more tweets.
    while True:
        try:
            print "    Page: %i" % PAGE
            tweets = API.user_timeline(screen_name=id, count=100, page=PAGE)
            if len(tweets) < 1:
                break
            for tweet in tweets:
                data = (row[1], row[2], tweet.text, party,)
                sql.execute("""insert into tweets (fname, lname, party, tweet) values
                            (?, ?, ?, ?)""", data)
            PAGE += 1
            sleep(2)
        except tweepy.error.TweepError:
            with open('./err.txt', 'w') as f:
                f.write("%s\n" % id)
            print "Error..."

def main():
    """ 
    Main script. Open CSV with legislator info. Loop over rows, pull 
    timelines out to SQLite. 
    """
    API = twitter_auth()
    db, sql = access_sql_db()

    with open('legislators.csv', 'r') as f:
        legislators = csv.reader(f)
        for row in legislators:
            scrape_timeline(row, API, sql)

        # Commit changes...done.
        db.commit()
