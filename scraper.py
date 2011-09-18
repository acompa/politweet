import tweepy
import sqlite3
from D import D
from R import R
from creds import C_KEY, C_SECRET, A_TOKEN, A_SECRET
from time import sleep
from sys import exit

def access_sql_db():
    """ Instantiate SQLite db and table for tweets. """
    db = sqlite3.connect('data/tweets')
    db.text_factory = str
    sql = db.cursor()
    return db, sql

def twitter_oauth():
    """ Authenticate w/ Twitter using Tweepy. """
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_SECRET)
    return tweepy.API(auth)

def approaching_rate_limit(API):
    """ Throttle access before hitting rate limit. """
    if API.rate_limit_status()['remaining_hits'] < 20:
        return True
    return False

def check_error_type(e):
    """ 
    Check TweepError string for info, respond accordingly.

    If e in {500, 502, 503} then sleep 2min.
    If e == 404 then break outer loop.
    If e == 400 then continue (user doesn't exist).
    Otherwise exit and show error message.

    Break/continue may not work in a function.
    """

    if len(filter(e.find() > -1, ['500', '502', '503'])) > 0:
        print e + "\nSleeping for 2 min..."
        sleep(120)
        return "s"
    elif e.find('404') > -1:
        return "b"
    elif e.find('400') > -1:
        return "c"

    # Exit if error doesn't fall into one of the above.
    else:
        exit(e)

# Grab tweets from each politician, insert them in SQL db.
def main():
    #db, sql = access_sql_db('data/tweets')
    db, sql = access_sql_db('data/tmp')

    p = 1
    party = ""
    congress = D + R

    for politician in congress:
        # Dem or GOP?
        if politician in D:
            party = "D"
        else:
            party = "R"

        while approaching_rate_limit(API):
            print """
        !! Approaching rate limit--%i requests left! Waiting a bit...
            """ % requests_left
            sleep(600)

        print """
        ** Now scraping %s's (%s) timeline...
        """ % (politician, party)

    # Scrape tweets for politician until there are no more tweets.
        while True:
            try:
                tweets = API.user_timeline(screen_name=politician, count=100,
                                           page=p)
                if len(tweets) < 1:
                    break

                for tweet in tweets:
                    data = (politician, tweet.text, party,)
                    sql.execute("""insert into tweets (name, party, tweet) values
                                (?, ?, ?)""", data)
                p += 1
                sleep(2)

            except tweepy.error.TweepError:
                e = tweepy.error.TweepError.__str__()
                action = check_error_type(e)
                if action is "b":
                    break
                elif action is "c":
                    continue
        p = 1

# Commit changes...done.
db.commit()

if __name__ == "__main__":
    main()
