import urllib2
from BeautifulSoup import BeautifulSoup

URL = "http://tweetcongress.org/members/index"

for party in ["D", "R", "I"]:
    handles = set([])
    for page in range(1, 50):
        html = urllib2.urlopen(URL + '/page:' + str(page) + '/party:' + party)
        soup = BeautifulSoup(html)
        for tag in soup.findAll('p'):
            try:
                if tag['class'] == "tweetTitle":
                    contents = tag.contents[0].strip()
                    i = contents.find('@')
                    if party == 'D':
                        handles.add(contents[i:])
                    elif party == 'R':
                        handles.add(contents[i:])
            except KeyError:
                continue
    print len(handles)
    with open('./%s.py' % party, 'w') as f:
        f.write('#!/usr/bin/python\n\n')
        f.write("%s = ['" % party)
        for handle in handles:
            f.write("%s', '" % handle)
        f.write("']")
