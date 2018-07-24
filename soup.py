from bs4 import BeautifulSoup

import urllib.request as urllib2
#specify the url
wiki = "https://en.wikipedia.org/wiki/List_of_state_and_union_territory_capitals_in_India"
wiki = 'https://en.wikipedia.org/wiki/The_Terminal'
wiki = 'https://en.wikipedia.org/wiki/2007_in_film'
wiki = 'https://en.wikipedia.org/wiki/List_of_romantic_comedy_films'
#Query the website and return the html to the variable 'page'
page = urllib2.urlopen(wiki)
#import the Beautiful soup functions to parse the data returned from the website
#Parse the html in the 'page' variable, and store it in Beautiful Soup format
soup = BeautifulSoup(page)
all_tables=soup.find_all('table')
right_table=soup.find('table', class_='wikitable')
