"""
Scraping politicians' Twitter accounts from tweetcongress.org.

Did not know of Sunlight Labs API until after this was written.
"""

import urllib2
from BeautifulSoup import BeautifulSoup

URL = "http://tweetcongress.org/members/index"

for party in ["D", "R"]:
    accounts = set([])

    # Access the URL, save the HTML using Beautiful Soup.
    for page in range(1, 50):
        html = urllib2.urlopen(URL + '/page:' + str(page) + '/party:' + party)
        soup = BeautifulSoup(html)

        # Parse HTML with Beautiful Soup. Ugly stuff down here.
        for tag in soup.findAll('p'):
            try:
                if tag['class'] == "tweetTitle":
                    contents = tag.contents[0].strip()
                    i = contents.find('@')
                    accounts.add(contents[i:])
            except KeyError:
                continue

    # How many legislators did I find?
    print len(handles)

    # Save their Twitter accounts to a new file, formatted as a list.
    with open('./%s.py' % party, 'w') as f:
        f.write('#!/usr/bin/python\n\n')
        f.write("%s = ['" % party)
        for account in accounts:
            f.write("%s', '" % account)
        f.write("']")
