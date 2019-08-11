import requests
import string
from xml.etree import ElementTree

from secrets import player_alias, players
from app import contains_word

BASE_URL = 'https://boardgamegeek.com'

def parse_comments(text):
    """
    """
    scores = {}
    text = text.lower()
    for line in text.split('\n'):
        try:
            player, score = tuple(word.strip() for word in line.split('-'))
            if player in player_alias:
                player = player_alias[player]
            scores[player] = score
            
        except ValueError:
            continue
    return scores

def fetch_plays(user="s_nav"):
    """

    """
    

    print("Fetching plays for user {}".format(user))
    url = BASE_URL + """/xmlapi2/plays?username={}&page={}""".format(user, 5)
    
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

        scores = parse_comments(text)
        player_count = len(scores.keys() & players) 
        if player_count >= 2:
            print(date, game, game_id, scores)
        

fetch_plays()
