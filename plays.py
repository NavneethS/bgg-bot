import requests
import string
import operator

from xml.etree import ElementTree

from secrets import player_alias, players
from app import contains_word

BASE_URL = 'https://boardgamegeek.com'

#Special Cases:
# Great Zimbabwe
# Lewis Clark
# Star Wars X wing
# Patchwork
# Gardens of Babylon


def make_stats(player, all_scores, player_count):

    ranks = {}
    for i in range(1, player_count+1):
        ranks[i] = []

    for game in all_scores:
        scores = game[3]
        if len(scores) == player_count and player in scores:
            rank = scores.index(player) + 1
            ranks[rank].append(game[1])
    
    return ranks


def parse_comments(text):
    """
    """
    scores = {}
    text = text.lower()
    for line in text.split('\n'):
        try:
            player, score = tuple(word.strip() for word in line.split('-'))
            score = score.split()[0]
            player = player.split()[0]

            if player in player_alias:
                player = player_alias[player]
            scores[player] = int(score)
            
        except ValueError:
            continue

    scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    order = [score[0] for score in scores]
    
    return tuple(order)

def fetch_plays(user="s_nav"):
    """

    """
    

    print("Fetching all plays for user {}".format(user))
    page = 0
    all_scores = []

    while True:
        page += 1
        url = BASE_URL + """/xmlapi2/plays?username={}&page={}""".format(user, page)

        r = requests.get(url)
        root = ElementTree.fromstring(r.content)
        if not root.findall('play'):
            break

        for play in root.findall('play'):
            date = play.get('date')
            game = play.find('item').get('name')
            game_id = play.find('item').get('objectid')
            try:
                text = play.find('comments').text
            except AttributeError:
                text = ""

            scores = parse_comments(text)
            player_count = len(set(scores).intersection(players))

            if player_count >= 2 and len(scores) == player_count:
                #print(date, game, game_id, scores)
                all_scores.append((date, game, game_id, scores))
    
    return all_scores

all_scores = fetch_plays()
print(len(all_scores))


for player in players:
    ranks = make_stats(player, all_scores, 4)
    print(player, dict((k,len(v)) for k,v in ranks.items()))

