"""
Trims Sunlight Labs API down to names, party membership, and Twitter accounts.
"""

import csv
from scraper import access_sql_db

def get_congress_members(sql):
    """
    Obtains names, party membership, Twitter accounts for members of Congress.
    Writes info out to SQLite db.
    """
    # Open raw data file and grab relevant columns.
    with open('sunlight.csv', 'r') as f:
        data = csv.reader(f)
        for row in data:
            t = (row[0], row[1], row[2], row[3], row[6], row[21])
            sql.execute(""" insert into identifiers 
                        (title, firstname, midname, lastname, party, twitter_id) 
                        values (?,?,?,?,?,?) """, t)

def main():
    db, sql = access_sql_db()
    sql.execute("drop table identifiers")
    sql.execute(""" create table identifiers (title text, firstname text, 
                midname text, lastname text, party test, twitter_id text)""")
    get_congress_members(sql)

    # Save changes.
    db.commit()

if __name__ == "__main__":
    main()
