import sqlite3
import re
import math

from classifier import TweetClassifier

class NBClassifier(TweetClassifier):
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

    def classify(self, tweet):
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
            print self.get_prob(word, "D")
            eta += math.log(1 - self.get_prob(word, "D")) - math.log(
                    self.get_prob(word, "D"))
        if  1 / (1 + exp(eta)) > 0.5:
            return "D"
        return "R"

def main():
    """
    Main script.

    NOTE: as a future extension, consider one trainer for each congressional
    body. How do senators, reps tweet?
    """
      
    DB = sqlite3.connect("data/tweets")
    CLASSIFIER = NBClassifier()

    # Train the classifier using sample of legislators' tweets.
    #
    # Note error in DB setup: legislators' tweets are ACTUALLY in the "party"
    # column of 'tweets' table. Similarly, self-id'd party is in the 'tweet'
    # column of 'tweets' table. Whoops.
    # -AC, 9/18/11
    
    # There are 188331 unique tweets in the data. Partition 30% as a test set,
    # create a reps_test table, then create the training set from the 
    # compliment of it.
    limit = int(0.3 * 188331)
    print limit
    DB.execute("drop table reps_test")
    DB.execute("""create table reps_test as select tweet, party, libscore 
               from reps_scored_tweets order by random() limit %i""" % limit)
    # # Don't actually need to create the training set--just subset the general table.
    training_set = DB.execute("""select tweet, party, libscore from 
                              reps_scored_tweets except select tweet, party, 
                              libscore from reps_test""")
    
    for row in training_set:
        CLASSIFIER.train(row)

#     for row in DB.execute("""select tweet, party, libscore from 
#                           sens_scored_tweets"""):
#         CLASSIFIER.inc_tweet_class_count(row)
#         CLASSIFIER.train(row)

    # Now attempt to classify tweets in test set.
    total = 0
    correct = 0
    test_set = DB.execute("select tweet, party, libscore from reps_test")
    for tweet in test_set:
        total += 1
        if CLASSIFIER.classify(tweet) == tweet[1]:
            correct += 1
    print "Accuracy: %d / %d: %.2d" % (correct, total, correct/total)

# Run main() from bash.
if __name__ == "__main__":
    main()
