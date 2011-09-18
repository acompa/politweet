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

        self.features = {}

        # Track tweets at other users, hashtags, and links independently
        # of words.
        for element in ['*tweet_at*', '*hashtag*', '*link*']:
            self.features.setdefault(element, {})
            self.features[element].setdefault('D', {})
            self.features[element].setdefault('R', {})
            self.features[element]['D'].setdefault('count', 0)
            self.features[element]['D'].setdefault('weight', 0)
            self.features[element]['R'].setdefault('count', 0)
            self.features[element]['R'].setdefault('weight', 0)

    #######
    ## These methods help tally tweet counts for a class.
    #######
    def inc_tweet_class_count(self, tweet_class):
        """ Increase count of features in a tweet class by one. """
        self.tweet_class_count[tweet_class] += 1

    def get_tweet_class_count(self, tweet_class):
        """ Return the number of features in a given class. """
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
        print features_per_class
        print self.get_tweet_class_count(tweet_class)
        return features_per_class / self.get_tweet_class_count(tweet_class)

    #######
    ## The next set of methods deal with features within tweets.
    #######
    def split_words(self, row):
        """ Splits tweets into a list of words. """
        tweet = row[0]
        for word in tweet.split():
            yield word

    def inc_word_count(self, word, score, tweet_class):
        """ Increment weighted count and count for a given word. """
        self.features[word][tweet_class]['weight'] += abs(score)/100 
        self.features[word][tweet_class]['count'] += 1

    # Replace these three functions with a single, special function.
    def inc_tweet_at(self, score, tweet_class):
        """ 
        Increase tweet_at by legislator's vote score, and increase tally
        by one.
        """
        self.features['*tweet_at*'][tweet_class]['weight'] += abs(score)/100
        self.features['*tweet_at*'][tweet_class]['count'] += 1

    def inc_link(self, score, tweet_class):
        """ 
        Increase link count by legislator's vote score, and increase tally
        by one.
        """
        self.features['*link*'][tweet_class]['weight'] += abs(score)/100
        self.features['*link*'][tweet_class]['count'] += 1

    def inc_hashtag(self, score, tweet_class):
        """ 
        Increment the effect of a hashtag by 'votescore'. Also tally
        number of total hashtags that appear.
        """
        self.features['*hashtag*'][tweet_class]['weight'] += abs(score)/100
        self.features['*hashtag*'][tweet_class]['count'] += 1
    #/replace

    def id_voter_party(self, score, party):
        """ 
        Identifies voter party based on score. Score < 0 --> GOP. 
        Score > 0 --> Dem. Score = 0 --> return voter's self-id'd party.
        Obvious problems with this at the moderate end--some voters may 
        identify one way and vote another. 

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
        score = row[2]
        tweet_class = self.id_voter_party(score, party)
        words = self.split_words(row)

        for word in words:
            self.inc_tweet_class_count(tweet_class)
            # Hashtag or @? Inc and move on.
            if word == '"':
                continue
            elif word.find('@') > -1:
                self.inc_tweet_at(score, tweet_class)
                continue
            elif word.find('#') > -1:
                self.inc_hashtag(score, tweet_class)
                continue
            elif word.find('http') > -1:
                self.inc_link(score, tweet_class)
                continue

            # Otherwise, increment count for this word.
            self.features.setdefault(word, {})
            self.features[word].setdefault(tweet_class, {})
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
