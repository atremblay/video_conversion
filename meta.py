from bs4 import BeautifulSoup
import urllib2
import numpy as np
import sqlite3


class Meta(object):
    """docstring for Meta"""
    def __init__(self, dbPath):
        super(Meta, self).__init__()
        self.dbPath = dbPath
        self.conn = sqlite3.connect(dbPath)
        self.cursor = self.conn.cursor()

    def get_meta(self, show, season, episodeNumber):
        print "Getting meta data for "
        print show, season, episodeNumber

        soup = self.get_html(show, season)

        if soup is None:
            print "Couldn't get the html source"
            return None

        episodeNumbers = list()
        episodeNames = list()
        episodeDescriptions = list()

        for tag in soup.find_all('meta'):
            if tag.has_attr('itemprop') and 'episodeNumber' in tag['itemprop']:
                episodeNumbers.append(tag['content'])
        episodeNumbers = np.array(episodeNumbers, dtype='int')

        for tag in soup.find_all('a'):
            if tag.has_attr('itemprop') and 'name' in tag['itemprop']:
                episodeNames.append(tag.string.decode('utf-8'))
        episodeNames = np.array(episodeNames)

        for tag in soup.find_all('div'):
            if tag.has_attr('class') and 'item_description' in tag['class']:
                description = tag.string
                if description is not None:
                    description = description
                episodeDescriptions.append(description)

        episodeDescriptions = np.array(episodeDescriptions)

        print episodeNumbers
        print episodeDescriptions
        ep_index = np.where([episodeNumbers == episodeNumber])[1]
        # ep_index = episodeNumbers.index(str(episodeNumber))
        if len(ep_index) == 0:
            print "Did not find that episode number"
            return None

        name = episodeNames[ep_index][0]
        description = episodeDescriptions[ep_index][0]

        if description is not None:
            description = description.strip()

        return (name, description)

    def get_html(self, show, season):
        url = self.get_url(show, season)
        if url is None:
            return None
        url = url[0]
        usock = urllib2.urlopen(url)
        html = usock.read()
        usock.close()

        soup = BeautifulSoup(html.decode('utf-8', 'ignore'))
        return soup

    def get_url(self, show, season):
        query = """SELECT url FROM meta WHERE show=? and season=? """
        self.cursor.execute(query, (show, season))
        result = self.cursor.fetchone()
        return result
