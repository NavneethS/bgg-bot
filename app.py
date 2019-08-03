from flask import Flask, request, jsonify
from secrets import slack_access_token as token
import requests
import random

from bgg import search

app = Flask(__name__)

def contains_word(s, w):
    return f' {w} ' in f' {s} '

def respond_to_greeting(user, channel):
    greetings = ["Howdy", "Hello there", "Wassup", "Ahoy"]
    response_text = '{} <@{}>!'.format(random.choice(greetings), user)
    r = requests.post(
        url="https://slack.com/api/chat.postMessage", 
        json={'text':response_text, 'channel': channel}, 
        headers={"Authorization": "Bearer {}".format(token)}
    )

    return r.status_code

def fetch_game(game, user, channel):
    game_fields = search(game)
    response_text = "\n🏆 {}\n\n🎲 {}\n\n⚖️ {}\n\n👨‍👩‍👧‍👦 {}-{}\n\n⌛ {}\n\n⚙️ {}\n\n📝 {}\n\n".format(game_fields['Rank'], game_fields['Name'], game_fields['Weight'], game_fields['Min Players'], game_fields['Max Players'], game_fields['Play Time'], ', '.join(game_fields['Mechanics']), ', '.join(game_fields['Categories']))
    r = requests.post(
        url="https://slack.com/api/chat.postMessage", 
        json={'text':response_text, 'channel': channel}, 
        headers={"Authorization": "Bearer {}".format(token)}
    )

    return r.status_code


@app.route('/', methods=['POST'])
def endpoint():
    """
    Slack Event API Listener
    """
    body = request.json 

    #Return the challenge for verification
    if list(body) == ["token", "challenge", "type"]:
        return jsonify({"challenge": body["challenge"]}), 200

    print(body)
    event = body['event']
    if event['type'] == 'app_mention':
        text = event['text'].lower()
        if contains_word(text, 'hi') or contains_word(text, 'hello'):
            status = respond_to_greeting(event['user'], event['channel'])
            assert status == 200
            return jsonify({'status':'ok'}), 200
        
        if contains_word(text, 'fetch'):
            game = text.split('fetch')[-1].strip()
            fetch_game(game, event['user'], event['channel'])
            return jsonify({'status':'ok'}), 200
        
 
if __name__ == '__main__':
    #To treat this as a listener for the Slack Events API, the URL must be verified, internet facing and respond to the challenge request made by slack. Deployed to the "internet" using ngrok.
    app.run('0.0.0.0')