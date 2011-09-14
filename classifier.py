import sqlite3
import re

class TweetClassifier():
    def __init__(self):
        self.tweet_class_count = {}
        self.tweet_class_count.setdefault('D', 0)
        self.tweet_class_count.setdefault('R', 0)

        # Will track three types of features initially:
        # 1. Words found in tweets.
        # 2. Tweets at other users ("@").
        # 3. Hashtags.
        # 
        # Potential future features: images, links.

        # Will track four counts for each feature:
        # 1. A weighted count for Dems based on the legislator's voting score.
        # 2. Same as #1, but for GOP.
        # 3. The number of times the feature appears in a Dem tweet.
        # 4. Same as #3, but for GOP.
        self.features = {}

        # Track tweets at other users independently of words.
        self.features.setdefault('*tweet_at*', {})
        self.features['*tweet_at*'].setdefault('D', {})
        self.features['*tweet_at*'].setdefault('R', {})
        self.features['*tweet_at*']['D'].setdefault('count', 0)
        self.features['*tweet_at*']['D'].setdefault('weight', 0)
        self.features['*tweet_at*']['R'].setdefault('count', 0)
        self.features['*tweet_at*']['R'].setdefault('weight', 0)

        # Same for hashtags.
        self.features.setdefault('*hashtag*', {})
        self.features['*hashtag*'].setdefault('D', {})
        self.features['*hashtag*'].setdefault('R', {})
        self.features['*hashtag*']['D'].setdefault('count', 0)
        self.features['*hashtag*']['D'].setdefault('weight', 0)
        self.features['*hashtag*']['R'].setdefault('count', 0)
        self.features['*hashtag*']['R'].setdefault('weight', 0)

    #######
    ## These methods help tally tweet counts for a class.
    #######
    def inc_tweet_class_count(self, row):
        """ Increase tweet class count by one. """
        party = row[1]
        score = row[3]
        tweet_class = self.identify_voter_party(score, party)
        self.tweet_class_count[tweet_class] += 1

    def get_tweet_class_count(self, tweet_class):
        """ Return the number of tweets in a given class. """
        return self.tweet_class_count[tweet_class]

    def get_total_count(self):
        """ Return total number of observations in training set. """
        total = 0
        for c in self.tweet_class_count:
            total += tweet_class_count[c]
        return c

    def get_prob(self, word, tweet_class):
        """ 
        Returns P(feature | class): probability that a feature appears in a tweet 
        given the tweet's class.
        
        P(feature | class) = P(features appear in class) / P(class)
        
        We have no prior reason to assume P("Dem") != P("GOP"), so let's assume
        P("Dem") = P("GOP") = 0.5 for now. I might change this to the proportion
        of legislators for a given party later on.
        """
        prior = 0.5
        features_per_class = self.get_feature_count(word, tweet_class)
        return features_per_class / prior

    #######
    ## The next set of methods deal with features within tweets.
    #######
    def split_words(self, row):
        """ Splits tweets into a list of words. """
        tweet = row[2]
        # I should just split on blank spaces...
        r = re.compile(r'[^a-zA-z0-9_@#]')
        return r.split(r, tweet)

    def inc_word_count(self, word, score, tweet_class):
        """ Increment weighted count and count for a given word. """
        self.features[word][tweet_class]['weight'] += abs(score)/100 
        self.features[word][tweet_class]['count'] += 1

    def inc_tweet_at(self, score, tweet_class):
        """ 
        Increase tweet_at by legislator's vote score, and increase tally
        by one.
        """
        self.features['*tweet_at*'][tweet_class]['weight'] += abs(score)/100
        self.features['*tweet_at*'][tweet_class]['count'] += 1

    def inc_hashtag(self, score, tweet_class):
        """ 
        Increment the effect of a hashtag by 'votescore'. Also tally
        number of total hashtags that appear.
        """
        self.features['*hashtag*'][tweet_class]['weight'] += abs(score)/100
        self.features['*hashtag*'][tweet_class]['count'] += 1

    def id_voter_party(self, score, party):
        """ 
        Identifies voter party based on score. Score < 0 --> GOP. 
        Score > 0 --> Dem. Obvious problems with this at the moderate end--some
        voters may identify one way and vote another. 

        NOTE: Consider two classifications: one by legislator's 
        self-identification, another by legislator's vote record.
        """

        # Comment first four lines out, depending on how I treat moderates.
        if score < 0:
            return 'R'
        elif score > 0:
            return 'D'
        return party

    def train(self, row):
        """ Trains classifier using a row from the training set. """
        party = row[1]
        score = row[3]
        tweet_class = self.id_voter_party(score, party)
        words = self.split_words(row)

        for word in words:

            # Hashtag or @? Inc and move on.
            if word.find('@') > -1:
                self.inc_tweet_at(score, tweet_class)
                continue
            elif word.find('#') > -1:
                self.inc_hashtag(score, tweet_class)
                continue

            # Otherwise, increment count for this word.
            self.features.setdefault(word, {})
            self.features[word].setdefault(tweet_class, 0)
            self.features[word][tweet_class].setdefault('count', 0)
            self.features[word][tweet_class].setdefault('weight', 0)
            self.inc_word_count(word, score, tweet_class)

    def get_weighted_score(self, word, tweet_class):
        """ Returns unweighted score for a given feature. """
        if word in self.features and tweet_class in self.features[word]:
            return float(self.features[word][tweet_class]['weight'])
        return 0.0

    def get_feature_count(self, word, tweet_class):
        """ Returns number of times word appears in tweets for a given class.. """
        if word in self.features and tweet_class in self.features[word]:
            return self.features[word][tweet_class]['count']
        return 0
