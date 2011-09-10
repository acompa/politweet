"""
Trims Sunlight Labs API down to names, party membership, and Twitter accounts.
"""

import csv

def get_congress_members():
    """
    Obtains names, party membership, Twitter accounts for members of Congress.
    Writes info out to a CSV file.
    """
    with open('legislators_raw.csv', 'r') as f:
        data = csv.reader(f)
        out = csv.writer(open('legislators.csv', 'w'), delimiter=',')
        for row in data:
            if row[21] is not "":
                out.writerow([row[0], row[1], row[3], row[6], row[21]])
            
def main():
    get_congress_members()
