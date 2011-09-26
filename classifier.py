import sqlite3
import re
import unicodedata
import operator

class TweetClassifier():
    def __init__(self):
        self.class_count = {}
        self.class_count.setdefault('D', 0)
        self.class_count.setdefault('R', 0)

        # Will track three types of features initially:
        # 1. Words found in tweets.
        # 2. Tweets at other users ("@").
        # 3. Hashtags.
        # 
        # Potential future features: images, links.

        self.features = {}
        for element in ['*tweet_at*', '*hashtag*', '*link*']:
            self.features.setdefault(element, {})
            self.features[element].setdefault('D', {})
            self.features[element].setdefault('R', {})
            self.features[element].setdefault('total', 0)
            self.features[element]['D'].setdefault('count', 0)
            self.features[element]['D'].setdefault('weight', 0)
            self.features[element]['R'].setdefault('count', 0)
            self.features[element]['R'].setdefault('weight', 0)

        self.exclusions = ['and', 'at', 'i', 'my', 'is', 'with', '&', '"', 
                           'the', 'to', 'on', 'in', 'of', 'for', 'a', 'this',
                           'will', 'be', 'you', 'from', '-', 'our', 'we', 
                           'about', 'that', 'are']

    #######
    ## These methods help tally tweet counts for a class.
    #######
    def inc_class_count(self, tweet_class):
        """ Increase count of tweets in a class by one. """
        self.class_count[tweet_class] += 1

    def get_class_count(self, tweet_class):
        """ Return the number of tweets in a given class. """
        return float(self.class_count[tweet_class])

    def get_tweet_class_prob(self, tweet_class):
        """ Return the probability of a tweet belonging to tweet_class. """
        total_count = self.get_class_count("D") + self.get_class_count("R")
        return float(self.get_class_count(tweet_class)) / total_count

    def get_feature_count(self, word):
        """ Return total number of times a feature occurs. """

        if word.find('http://') > -1:
            word = '*link*'
        elif word.find('@') > -1:
            word = '*tweet_at*'
        elif word.find('#') > -1:
            word = '*hashtag*'

        return float(self.get_feature_count_in_class(word, "D")) + \
               self.get_feature_count_in_class(word, "R")

    def get_feature_count_in_class(self, word, tweet_class):
        """ 
        Returns number of times word appears in tweets for a given class.
        Also manages links, hashtags, tweets at other users.
        """
        if word.find('http://') > -1:
            return float(self.features['*link*'][tweet_class]['count'])
        elif word.find('@') > -1:
            return float(self.features['*tweet_at*'][tweet_class]['count'])
        elif word.find('#') > -1:
            return float(self.features['*hashtag*'][tweet_class]['count'])
        elif word in self.features:
            try:
                return float(self.features[word][tweet_class]['count'])
            except KeyError:
                pass
        return 0.0

    def get_prob(self, word, tweet_class):
        """ 
        Returns P(feature | class): probability that a feature appears in a 
        tweet given the tweet's class.
        
        P(feature | class) = P(feature appear in class) / P(class)
        """
        try:
            feature_count = self.get_feature_count_in_class(word, tweet_class)
        except KeyError:
            feature_count = 0.0

        # Using Laplace smoothing. All features get +1 to avoid sparseness 
        # issues. See Manning on NB text classifiers
        # (http://nlp.stanford.edu/IR-book/)
        return (feature_count + 1) / self.get_class_count(tweet_class)

    def calculate_bias(self):
        """ 
        Returns bias. In this case, will assume independence and set bias to
        proportion of Democratic tweets in training set.
        """
        return float(self.class_count['D']) / (self.class_count['D'] + 
                                               self.class_count['R'])

    #######
    ## The next set of methods deal with features within tweets.
    #######
    def print_common_features(self, n=10):
        """ Prints n most common features and their class counts. """
        for f in sorted(self.features.keys(), 
                        key=lambda x: (self.features[x]['total']), 
                        reverse=True)[:n]:
            print "%s: %i appearances (%i for Dem, %i for GOP)" % (f, 
                self.features[f]['total'], self.features[f]['D']['count'], 
                self.features[f]['R']['count'])

    def split_words(self, row):
        """ Splits tweets into a list of words. """
        tweet = row[0]
        r = re.compile(u'[^a-zA-Z@#://]')
        for word in tweet.split():
            word = unicodedata.normalize('NFKD', word)
            r.sub('', word)
            yield word.lower()

    def inc_word_count(self, word, score, tweet_class):
        """ Increment weighted count and count for a given word. """
        self.features[word][tweet_class]['weight'] += abs(score)/100 
        self.features[word][tweet_class]['count'] += 1
        self.features[word]['total'] += 1

    # Replace these three functions with a single, special function.
    def inc_tweet_at(self, score, tweet_class):
        """ 
        Increase tweet_at by legislator's vote score, and increase tally
        by one.
        """
        self.features['*tweet_at*'][tweet_class]['weight'] += abs(score)/100
        self.features['*tweet_at*'][tweet_class]['count'] += 1
        self.features['*tweet_at*']['total'] += 1

    def inc_link(self, score, tweet_class):
        """ 
        Increase link count by legislator's vote score, and increase tally
        by one.
        """
        self.features['*link*'][tweet_class]['weight'] += abs(score)/100
        self.features['*link*'][tweet_class]['count'] += 1
        self.features['*link*']['total'] += 1

    def inc_hashtag(self, score, tweet_class):
        """ 
        Increment the effect of a hashtag by 'votescore'. Also tally
        number of total hashtags that appear.
        """
        self.features['*hashtag*'][tweet_class]['weight'] += abs(score)/100
        self.features['*hashtag*'][tweet_class]['count'] += 1
        self.features['*hashtag*']['total'] += 1
    #/replace

    def id_voter_party(self, score, party):
        """ 
        Identifies voter party based on score. Score < 0 --> GOP. 
        Score > 0 --> Dem. Score = 0 --> return voter's self-id'd party.

        Obvious problems with this at the moderate end--some voters may 
        identify one way and vote another. 
        """

        # Comment first four lines out, depending on how I treat moderates.
        
        if score < 0:
            return 'R'
        elif score > 0:
            return 'D'
        return party

    #######
    ## Finally, get to training.
    #######
    def train(self, row):
        """ Trains classifier using a row from the training set. """
        party = row[1]
        score = row[2]
        tweet_class = self.id_voter_party(score, party)
        self.inc_class_count(tweet_class)
        words = self.split_words(row)

        for word in words:
            # Hashtag or @? Inc and move on.
            if word in self.exclusions:
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
            self.features[word].setdefault('D', {})
            self.features[word].setdefault('R', {})
            self.features[word].setdefault('total', 0)
            self.features[word][tweet_class].setdefault('count', 0)
            self.features[word][tweet_class].setdefault('weight', 0)
            self.inc_word_count(word, score, tweet_class)

    def get_weighted_score(self, word, tweet_class):
        """ Returns unweighted score for a given feature. """
        if word in self.features and tweet_class in self.features[word]:
            return float(self.features[word][tweet_class]['weight'])
        return 0.0
