import sqlite3
import re

from classifier import TweetClassifier

class NBClassifier(classifier.TweetClassifier):
    """
    A subclass of the general classifier. Inherits feature-counting
    methods and dicts. Will also calculate probability using Bayes's
    Theorem.
    """

    def prob_class(tweet_class):
        """ Returns the probability of a given class occurring. """
        
        count = self.get_tweet_class_count(tweet_class)
        total = self.get_total_count()

        return float(count/total)

    def prob_class_given_features():
        """ 
        Returns the probability that a tweet falls into a class given
        the features in that tweet.
        """
        return 0
        
