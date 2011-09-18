-------
--
-- Match scores to each politician's tweets. I could have probably
-- accomplished this in Python, but I need SQL practice.
-- -AC, 9/10/11 (lol!)
--
-------

-- If the big block below doesn't work, replace the nested SELECT with
-- reps_scores (same for second block too, except sens_scores).
DROP TABLE reps_scored_tweets;
CREATE TABLE reps_scored_tweets AS
     SELECT name, tweets.party as tweet, reps.party as party, libscore
     FROM (SELECT n.firstname, midname, n.lastname, party, twitter_id, libscore
           FROM identifiers AS n,
                       reps AS reps
           WHERE n.title = 'Rep'
	   AND n.firstname = reps.firstname
           AND n.lastname = reps.lastname) as reps, tweets
     WHERE replace(tweets.name, '@', '') = reps.twitter_id;

DROP TABLE sens_scored_tweets;
CREATE TABLE sens_scored_tweets AS
     SELECT name, tweets.party as tweet, sens.party as party, libscore
     FROM (SELECT n.firstname, midname, n.lastname, party, twitter_id, libscore
           FROM identifiers as n,
                   senators as sens
           WHERE n.title = 'Sen'
           AND n.firstname = sens.firstname
           AND n.lastname = sens.lastname) as sens, tweets
     WHERE replace(tweets.name, '@', '') = sens.twitter_id;

-- ALTER TABLE scored_tweets_temp
--     ADD COLUMN score int;

-- UPDATE scored_tweets_temp
--     SET score = libscore
--     WHERE libscore