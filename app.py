from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/', methods=['POST'])
def challenge():
    """
    Slack Event API Listener
    """
    body = request.json

    #Return the challenge for verification
    if list(body) == ["token", "challenge", "type"]:
        return jsonify({"challenge": body["challenge"]})

if __name__ == '__main__':
    #To treat this as a listener for the Slack Events API, the URL must be verified, internet facing and respond to the challenge request made by slack. Deployed to the "internet" using ngrok.
    app.run('0.0.0.0')