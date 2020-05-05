import time
import requests
import urllib
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from xml.etree import ElementTree

# TODO
# display search results count
# player count distribution

BASE_URL = "https://boardgamegeek.com"


def geeksearch(text):
    """
    Returns the search results against a query as on the bgg search page
    Parameters:
        - text: str. Query string
    Returns:
        - pagehtml: str. html content of page to be parsed 
    """
    text = urllib.parse.quote_plus(text.lower().strip())
    results = []

    url = (
        BASE_URL
        + "/geeksearch.php?action=search&objecttype=boardgame&q={}&B1=Go".format(text)
    )
    print("Making geeksearch request")
    r = requests.get(url)
    pagehtml = r.text
    return pagehtml

def topsearch(page, ranktype='strategy'):
    """
    Returns the 100 (one page) results on the bgg ranking page
    Parameters:
        - page: int. page number
        - ranktype: str. strategy game rank, or all game rank
    Returns:
        - pagehtml: str. html content of page to be parsed. 100 games per page
    """
    if ranktype == 'strategy':
        url = BASE_URL + "/strategygames/browse/boardgame/page/{}".format(page)
    else:
        url = BASE_URL + "/browse/boardgame/page/{}".format(page)
    r = requests.get(url)
    pagehtml = r.text
    return pagehtml

def getgames(pagehtml):
    """
    Scrape basic fields from BGG html page
    Parameters:
        - pagehtml: str. html content extracted from BGG. Result of topsearch() or geeksearch()
    Returns:
        - results: list(dict). List of games with rank, title, gameid, geekrating, avgrating, numvoters 
    """
    results = []
    parsed = BeautifulSoup(pagehtml, "html.parser")
    table = parsed.find("table", {"class": "collection_table"})

    rows = table.find_all("tr")
    for row in rows:
        if row.attrs.get("id") == "row_":
            rankcell = row.find("td", "collection_rank")
            rank = rankcell.text.strip()

            gamecell = row.find("td", "collection_objectname")
            game = gamecell.find("a", href=True)
            title = game.text
            link = game["href"]
            gameid = game["href"].split("/")[2]

            ratingcells = row.find_all("td", "collection_bggrating")
            geekrating = float(ratingcells[0].text.strip())
            avgrating = float(ratingcells[1].text.strip())
            numvoters = int(ratingcells[2].text.strip())

            results.append(
                {
                    "rank": rank,
                    "title": title,
                    "link": link,
                    "gameid": gameid,
                    "geekrating": geekrating,
                    "avgrating": avgrating,
                    "numvoters": numvoters,
                }
            )

    print("{} results found".format(len(results)))
    return results


def fetch_bgg(game):
    """
    Given a bgg game id, retrieve game data
    Parameters:
        - game: str. A BGG game id
    Returns:
        - fields. dict
            - Name
            - Min Players
            - Max Players
            - Play Time
            - Categories
            - Mechanics
            - Num Ratings
            - Avg Rating
            - Weight
            - Rank
            - Strategy Rank
    """
    fields = {}

    print("Fetching data for game {}".format(game))
    url = (
        BASE_URL
        + """/xmlapi2/thing?id={}
            &versions=1
            &videos=1
            &stats=1
            &marketplace=1
            &ratingcomments=1&pagesize=100&page=1""".format(
            game
        )
    )

    r = requests.get(url)
    root = ElementTree.fromstring(r.content)[0]
    assert root.get("id") == str(game)

    fields["Name"] = root.find("name").get("value")
    fields["Image"] = root.find("thumbnail").text
    fields["Year"] = root.find("yearpublished").get("value")
    fields["Min Players"] = root.find("minplayers").get("value")
    fields["Max Players"] = root.find("maxplayers").get("value")
    fields["Play Time"] = root.find("playingtime").get("value")

    cats = []
    mechs = []
    for link in root.findall("link"):
        if link.get("type") == "boardgamecategory":
            cats.append(link.get("value"))
        elif link.get("type") == "boardgamemechanic":
            mechs.append(link.get("value"))
    fields["Categories"] = cats
    fields["Mechanics"] = mechs

    ratings = root.find("statistics").find("ratings")
    fields["Num Ratings"] = ratings.find("usersrated").get("value")
    fields["Avg Rating"] = ratings.find("average").get("value")
    fields["Weight"] = ratings.find("averageweight").get("value")

    for rank in ratings.find("ranks").findall("rank"):
        if rank.get("name") == "boardgame":
            fields["Rank"] = rank.get("value")
        if rank.get("name") == "strategygames":
            fields["Strategy Rank"] = rank.get("value")

    return fields


def get_gamedata(game):
    """

    """
    bgg_row = fetch_bgg(game)

    # TODO: get geekmarket/bgp price and reddit rank
    # reddit_row = fetch_reddit(game)
    # bgp_row = fetch_price(game):
    return bgg_row


def search(text):
    pagehtml = geeksearch(text)
    results = getgames(pagehtml)
    try:
        top_hit = results[0]["gameid"]
        game_fields = get_gamedata(top_hit)
        game_fields["Link"] = BASE_URL + results[0]["link"]
    except IndexError:
        return {"Error": "Game not found"}
    return game_fields


# print(search('Mombas'))

def filtergames(df, threshold):
    
    return df[df['geekrating'] >= threshold]

def research():
    threshold = 6.517
    run_id = "runx"
    new = []

    done = False
    page = 1
    while not done:
        pageresults = getgames(topsearch(page))
        new.extend(pageresults)
        if pageresults[-1]['geekrating']<threshold:
            break
        page += 1
       
    print('{} pages added'.format(page))
    
    new_df = pd.DataFrame(new)
    new_df = new_df.set_index('gameid')
    new_df = filtergames(new_df, threshold)
    
    expanded_new = []
    for gid, game in new_df.iterrows():
        try:
            game_fields = get_gamedata(gid)
            game_fields["Link"] = BASE_URL + game["link"]
            game_fields["Geek Rating"] = game['geekrating']
            game_fields["GameId"] = gid
            expanded_new.append(game_fields)
        except Exception as e:
            print(e)
            print('EXC', gid)
        time.sleep(2)

    expanded_new_df = pd.DataFrame(expanded_new)
    expanded_new_df = expanded_new_df.set_index('GameId')

    expanded_new_df.to_csv('research.csv')
    return