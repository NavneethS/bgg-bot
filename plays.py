import requests
from xml.etree import ElementTree

BASE_URL = 'https://boardgamegeek.com'

def parse_comments(text):
    pass

def fetch_plays(user="s_nav"):
    """

    """
    print("Fetching plays for user {}".format(user))
    page = 1
    url = BASE_URL + """/xmlapi2/plays?username={}&page={}""".format(user, page)
    
    r = requests.get(url)
    root = ElementTree.fromstring(r.content)
    for play in root.findall('play'):
        date = play.get('date')
        game = play.find('item').get('name')
        game_id = play.find('item').get('objectid')
        try:
            text = play.find('comments').text
        except AttributeError:
            text = ""

        print(date, game, game_id, text)

fetch_plays()
