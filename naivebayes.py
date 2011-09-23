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
        Rewritten. Now compares probabilities that tweet is Dem or GOP,
        and returns a classification based on the higher probability.
        -AC, 9/22/11
        """
        words = self.split_words(tweet)
        prob_d = 1
        prob_r = 1

        for word in words:
            try:
                prob_d *= self.get_prob(word, "D") if \
                          self.get_prob(word, 'D') > 0 else 1
                prob_r *= self.get_prob(word, "R") if \
                          self.get_prob(word, 'R') > 0 else 1
            except ValueError:
                # Skip word if not found in trainer.
                continue

        prob_d *= (self.get_tweet_class_prob('D'))
        prob_r *= (self.get_tweet_class_prob('R'))
        #print "P(class = D): %0.2f, P(class = R): %0.2f" % (prob_d, prob_r)
        if prob_d > prob_r:
            return 'D'
        return 'R'

def test_classifier(CLASSIFIER, DB, group):
    """
    Group overhead for classifier into a program and run it. Prints resulting
    accuracy for group.
    """

    print CLASSIFIER.class_count['D']
    print CLASSIFIER.class_count['R']
    print CLASSIFIER.class_count['D'] + CLASSIFIER.class_count['R']

    total = 0
    correct = 0
    true_pos = 0
    positives = 0
    test_set = DB.execute("select tweet, party, libscore from %s_test" % group)

    # Loop over test 
    for tweet in test_set:
        total += 1
        output_class = CLASSIFIER.classify(tweet)

        if output_class == tweet[1]:
            correct += 1
            if output_class == "D":
                true_pos += 1

        if output_class is "D":
            positives += 1

    print "Precision (%s): %d / %d: %.2f" % (group, true_pos, positives,
                                             0 if float(positives) == 0.0 else float(true_pos)/float(positives))
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
