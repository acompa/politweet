import D
import R
import I
import tweepy
from creds import C_KEY, C_SECRET, A_TOKEN, A_SECRET

AUTH = tweepy.OAuthHandler(C_KEY, C_SECRET)
AUTH.set_access_token(A_TOKEN, A_SECRET)
API = tweepy.API(auth)

# Next: access each politician's tweets, save...how many?
# Anyway, save them to SQLite and clean the tweets (like maps.NBA).