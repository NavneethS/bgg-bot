from flask import Flask, request, jsonify
from secrets import slack_access_token as token
import requests
import random

from bgg import search

app = Flask(__name__)

def contains_word(s, w):
    return f' {w} ' in f' {s} '


def post_message(response_text, channel):
    r = requests.post(
        url="https://slack.com/api/chat.postMessage", 
        json={'text':response_text, 'channel': channel}, 
        headers={"Authorization": "Bearer {}".format(token)}
    )
    return r.status_code

def respond_to_greeting(user, channel):
    greetings = ["Howdy", "Hello there", "Wassup", "Ahoy"]
    response_text = '{} <@{}>!'.format(random.choice(greetings), user)
    return post_message(response_text, channel)
    
def roll_die(die, times, channel):
    results = [str(random.randint(1,die)) for _ in range(times)]
    response_text = "I rolled a {} sided 🎲 {} times for you . Your results are 🔮 {} !".format(str(die), str(times), ', '.join(results))
    return post_message(response_text, channel)


def respond_to_help(channel):
    response_text = "Hello, I am a bot. I live to serve. I will listen for messages tagging me as @bgg-bot followed by a command. Here is a list of commands you can give me:\n\n `help` : show this help message again \n\n `hi/hello` : come say hi. \n\n `fetch <game>` : look up <game> on BGG \n\n `roll <times> d<number>` : roll a <number> sided die <times> number of times"
    return post_message(response_text, channel)


def fetch_game(game, user, channel):
    game_fields = search(game)
    if 'Error' in game_fields:
        response_text = "No board game found"
        return post_message(response_text, channel)
    
    response_text = "\n\n🏅 {}\n\n🎲 {} ({})\n\n⚖️ {} 👨‍👩‍👧‍👦 {}-{} ⌛ {} minutes\n\n⚙️ {}\n\n📝 {}\n\n".format(game_fields['Rank'], game_fields['Name'], game_fields['Year'], game_fields['Weight'], game_fields['Min Players'], game_fields['Max Players'], game_fields['Play Time'], ', '.join(game_fields['Mechanics']), ', '.join(game_fields['Categories']))
    r = requests.post(
        url="https://slack.com/api/chat.postMessage", 
        json={
            'text':response_text, 
            'channel': channel, 
            'attachments': [
                {'text': game_fields['Name'], 'image_url': game_fields['Image']},
                {'fallback': game_fields['Name'], 'actions': [{
                    "type": "button",
                    "text": "View on BGG",
                    "url": game_fields['Link']}]
                }
            ]
        }, 
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
        text = event['text'].lower().strip()
        if text.split()[-1] == 'help':
            status = respond_to_help(event['channel'])
            assert status == 200

        elif contains_word(text, 'hi') or contains_word(text, 'hello'):
            status = respond_to_greeting(event['user'], event['channel'])
            assert status == 200
        
        elif contains_word(text, 'roll'):
            numbers = text.split('roll')[-1].split('d')
            times = int(numbers[0].strip())
            die = int(numbers[1].strip())
            status = roll_die(die, times, event['channel'])

        elif contains_word(text, 'fetch'):
            game = text.split('fetch')[-1].strip()
            fetch_game(game, event['user'], event['channel'])
    
    return jsonify({'status':'ok'}), 200
        
 
if __name__ == '__main__':
    #To treat this as a listener for the Slack Events API, the URL must be verified, internet facing and respond to the challenge request made by slack. Deployed to the "internet" using ngrok.
    app.run('0.0.0.0')