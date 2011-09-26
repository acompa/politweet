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

        return float(count)/float(total)

    def classify(self, tweet):
        """ 
        Rewritten. Now compares probabilities that tweet is Dem or GOP,
        and returns a classification based on the higher probability.
        -AC, 9/22/11
        """
        words = self.split_words(tweet)
        prob_d = 0
        prob_r = 0

        for word in words:
            prob_d += math.log(self.get_prob(word, "D"))
            prob_r += math.log(self.get_prob(word, "R"))

        prob_d += math.log(self.get_tweet_class_prob('D'))
        prob_r += math.log(self.get_tweet_class_prob('R'))
        #print "P(class = D): %0.20f  ||||  P(class = R): %0.20f" % (prob_d, prob_r)
        if prob_d > prob_r:
            return 'D'
        return 'R'

def test_classifier(CLASSIFIER, DB, group):
    """
    Group overhead for classifier into a program and run it. Prints resulting
    accuracy for group.
    """

    print "\nTrained %d Dem %s tweets" % (CLASSIFIER.class_count['D'], group)
    print "Trained %d GOP %s tweets" % (CLASSIFIER.class_count['R'], group)
    print "Total %s tweets: %d\n" % (group, CLASSIFIER.class_count['D'] + 
                                   CLASSIFIER.class_count['R'])

    total = 0
    correct = 0
    true_pos = 0
    false_neg = 0
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

        if output_class is "R" and tweet[1] is "D":
            false_neg += 1

    print "Precision (%s): %d / %d: %0.2f" % (group, true_pos, positives,
                                              100 * float(true_pos) / 
                                              float(positives))
    print "Recall (%s): %d / %d: %0.2f" % (group, true_pos, true_pos + 
                                           false_neg,
                                           100 * float(true_pos) / 
                                           float(true_pos+false_neg))
    print "Accuracy (%s): %0.2f" % (group, 100 * float(correct) / float(total))

def main():
    """
    Main script.

    NOTE: as a future extension, consider one trainer for each congressional
    body. How do senators, reps tweet?
    """
      
    DB = sqlite3.connect("data/tweets")
    REP_CLASSIFIER = NBClassifier()

    # Train the classifier using sample of legislators' tweets.    
    r_limit = int(0.2 * 110000)
    training_set = partition_sample(r_limit, DB, 'r')    
    for row in training_set:
        REP_CLASSIFIER.train(row)

    # Print 10 most common features in classifier, along with class info.
    print "\nMOST COMMON REP FEATURES:\n"
    REP_CLASSIFIER.print_common_features(n=20)

    # Test the classifier.
    test_classifier(REP_CLASSIFIER, DB, 'reps')

    SEN_CLASSIFIER = NBClassifier()
    s_limit = int(0.2 * 29463)
    training_set = partition_sample(s_limit, DB, 's')    
    for row in training_set:
        SEN_CLASSIFIER.train(row)

    print "\nMOST COMMON SEN FEATURES:\n"
    SEN_CLASSIFIER.print_common_features(n=20)
    
    # Test the classifier.
    test_classifier(SEN_CLASSIFIER, DB, 'sens')

# Run main() from bash.
if __name__ == "__main__":
    main()
