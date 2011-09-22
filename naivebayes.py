import sqlite3
import re
import math

from classifier import TweetClassifier
from utilities import partition_sample

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
        
        Using natural logs, this can be simplified to:
        
        P(class | features) = 1 / (1 + e^eta), eta = sum( ln(1-p_xi) - ln(p_i))
        
        to avoid floating-point underflow.
        
        (thanks to anonymous Wikipedia editors for this tip: 
        http://en.wikipedia.org/wiki/Bayesian_spam_filtering)
        """
        words = self.split_words(tweet)
        eta = 0

        for word in words:
            try:
                print self.get_prob(word, "D")
                eta += math.log(1 - self.get_prob(word, "D")) - math.log(
                         self.get_prob(word, "D"))
            except ValueError:
                # Skip word if not found in trainer.
                continue

        if  1 / (1 + math.exp(eta)) > 0.5:
            return "D"
        return "R"

def test_classifier(CLASSIFIER, DB, group):
    """
    Group overhead for classifier into a program and run it. Prints resulting
    accuracy for group.
    """

    total = 0
    correct = 0
    positives = 0
    test_set = DB.execute("select tweet, party, libscore from %s_test" % group)

    # Loop over test 
    for tweet in test_set:
        total += 1
        output_class = CLASSIFIER.classify(tweet)

        if output_class == tweet[1]:
            correct += 1

        if output_class is "D":
            positives += 1

    print "Precision (%s): %d / %d: %.2f" % (group, correct, positives, 
                                             float(correct)/float(positives))
    print "Recall (%s): %d / %d: %.2f" % (group, correct, total, 
                                          float(correct)/float(total))


def main():
    """
    Main script.

    NOTE: as a future extension, consider one trainer for each congressional
    body. How do senators, reps tweet?
    """
      
    DB = sqlite3.connect("data/tweets")
    CLASSIFIER = NBClassifier()

    # Train the classifier using sample of legislators' tweets.    
    r_limit = int(0.3 * 188331)
    training_set = partition_sample(r_limit, DB, 'r')    
    for row in training_set:
        CLASSIFIER.train(row)

    # Now attempt to classify tweets in test set.
    test_classifier(CLASSIFIER, DB, 'reps')

    s_limit = int(0.3 * 29463)
    training_set = partition_sample(r_limit, DB, 'd')    
    for row in training_set:
        CLASSIFIER.train(row)

    # Same thing for senators.
    test_classifier(CLASSIFIER, DB, 'sens')

# Run main() from bash.
if __name__ == "__main__":
    main()
