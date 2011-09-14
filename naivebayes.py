import sqlite3
import re
import math

from classifier import TweetClassifier

class NBClassifier(classifier.TweetClassifier):
    """
    A subclass of the general classifier. Inherits feature-counting
    methods and dicts. Will also calculate probability using Bayes's
    Theorem.
    """

    def prob_class(self, tweet_class):
        """ Returns the probability of a given class occurring. """
        
        count = self.get_tweet_class_count(tweet_class)
        total = self.get_total_count()

        return float(count/total)

    def classify(self, tweet, tweet_class):
        """ 
        Returns the probability that a tweet falls into a class given
        the features in that tweet (or: P(class | features) ).
        
        Given the NB assumption of feature independence, we can simply
        multiply the probabilities for each feature like so:
        
        P(class | features) =              p_x1 * p_x2 * ... * p_xn
                              ___________________________________________________
                              (p_x1 * ... * p_xn) + [ (1-p_x1) * ... * (1-p_xn) ]
                              
        where p_xi = P(feature | class) aka TweetClassifier.get_prob(). Using 
        natural logs, this can be simplified to:
        
        P(class | features) = 1 / (1 + e^eta), eta = sum( ln(1-p_xi) - ln(p_i))
        
        to avoid floating-point underflow.
        
        (thanks to anonymous Wikipedia editors for this tip: 
        http://en.wikipedia.org/wiki/Bayesian_spam_filtering#Mathematical_foundation)
        """
        words = self.split_words(tweet)
        eta = 0
        for word in words:
            exponent += math.ln(1 - get_prob(word, "D")_ - math.ln(get_prob(word, "D")))
        return 1 / (1 + exp(eta))

def main():
    """
    Main script.

    NOTE: as a future extension, consider one trainer for each congressional
    body. How do senators, reps tweet?
    """
      
    DB = sqlite3.connect("./tweets")
    CLASSIFIER = TweetClassifier()

    # Train the classifier using sample of legislators' tweets.
    #
    # TO DO: select rows at random from sample. Partition sample into training
    # and test subsets for both reps and senators. SQLite pseudocode below:
    # limit = 0.3 * DB.execute("""select count(*) from reps_score_tweets""")
    # test_set = DB.execute("""create table reps_test as (select tweet, party, libscore from 
    #                           reps_score_tweets order by random() limit 
    #                           ?)""", limit)
    # # Don't actually need to create the training set--just subset the general table.
    # training_set = DB.execute("""(select tweet, party, libscore from 
    #                       reps_score_tweets) except (select tweet, party, libscore from 
    #                       reps_test))""")
    
    for row in DB.execute("""select tweet, party, libscore from 
                          reps_score_tweets"""):
        TRAINER.increment_tweet_class_count(row)
        TRAINER.classify_words(row)

    for row in DB.execute("""select tweet, party, libscore from 
                          sens_score_tweets"""):
        TRAINER.increment_tweet_class_count(row)
        TRAINER.classify_words(row)

    CLASSIFIER.get_tweet_class_count('D')
    CLASSIFIER.get_tweet_class_count('R')
        
    # Now attempt to classify tweets in test set.
    ...
    for tweet in test_set:
        print "Prob. tweet is Dem: %i" % CLASSIFIER.classify(tweet, "D")
        print "Prob. tweet is GOP: %i" % CLASSIFIER.classify(tweet, "R")
        print "Tweet's class: %s" % tweet[1]

# Run main() from bash.
if "__name__" == "__main__":
    main()
