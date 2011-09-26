def partition_sample(limit, DB, group):
    """
    Partitions sample of tweets into a training sample. Will use the compliment
    later to construct a test sample.
    """

    # Set table to modify.
    if group == "r":
        set = "reps"
    else:
        set = "sens"

#     DB.execute("drop table %s_test" % set)
#     DB.execute("""create table %s_test as select tweet, party, libscore 
#               from %s_scored_tweets order by random() limit %i""" % 
#               (set, set, limit))

    return DB.execute("""select tweet, party, libscore from 
                      %s_scored_tweets except select tweet, party, 
                      libscore from %s_test""" % (set, set))
