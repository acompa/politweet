import tweepy
import sqlite3
from D import D
from R import R
from creds import C_KEY, C_SECRET, A_TOKEN, A_SECRET
from time import sleep
from sys import exit

# Fix Twitter authentication. -AC, 9/3/11
auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_SECRET)
API = tweepy.API(auth)

# Instantiate SQLite db and table for tweets.
db = sqlite3.connect('./tweets')
sql = db.cursor()
# sql.execute("""delete from tweets""")
# sql.execute("""create table tweets
#             (id integer primary key asc autoincrement, name text, party text,
#             tweet text)""")
 
# Grab tweets from each politician, insert them in SQL db.
p = 1
party = ""
congress = D + R
with open("./err.txt", "r") as f:
    last_name = str(f.readline().strip())
    print last_name
    if last_name == '':
        congress = D + R
    elif last_name in D:
        congress = D[D.index(last_name):] + R
    elif last_name in R:
        congress = R[R.index(last_name):]

for politician in congress:
    # Dem or GOP?
    if politician in D:
        party = "D"
    else:
        party = "R"
    print """
    *******
    ** Now scraping %s's (%s) timeline...
    *******""" % (politician, party)

    requests_left = API.rate_limit_status()['remaining_hits']
    print requests_left
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
            print "    Page: %i" % p
            tweets = API.user_timeline(screen_name=politician, count=100, page=p)
            if len(tweets) < 1:
                break
            for tweet in tweets:
                data = (politician, tweet.text, party,)
                sql.execute("""insert into tweets (name, party, tweet) values
                            (?, ?, ?)""", data)
            p += 1
            sleep(2)
        except tweepy.error.TweepError:
            with open('./err.txt', 'w') as f:
                f.write("%s\n" % (politician))
            exit("Twitter error...")
            break
            
    p = 1

# Commit changes...done.
db.commit()