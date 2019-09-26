# bgg-bot
BoardGameGeek.com integrated slack bot

## How to test/dev

1. `source bot-env/bin/activate`
2. Install requirements
3. `python app.py`
4. `ngrok http 5000`. 
5. Add url to slack app

## How to deploy

1. Make config file `secrets.py`
2. Create AWS IAM with full access and store credentials in `~/.aws/credentials` 
3. Create `zappa_settings.json` or `zappa init`

```json
{
    "dev": {
        "app_function": "app.app",
        "profile_name": null,
        "project_name": "bgg-bot",
        "runtime": "python3.6",
        "s3_bucket": "...",
        "aws_region": "..."
    }
}
```

6. `zappa deploy dev` to pack and deploy to AWS Lambda
7. Add url to slack app

`zappa tail` for logs or `zappa update dev` for updating module changes (not endpoints)

## Ideas : 
1. Poll my BGG plays and post update after a new play logged.
2. Aggregate and store leaderboard
3. Query support for leaderboard. Stats, etc.
4. Fetch game details from BGG. Rank, summary, etc.

## Taskboard Done : 

1. Structure the app
2. Implement hi
3. Bug: post to correct channel
4. Implement game lookup
5. Geeksearch
6. Implement fetch <game> command
7. Implement die roll

## TODO:

### Next steps
0. Good name for bot
1. Display average BGG rating and num ratings in `fetch`
2. Leaderboard, logs and stats

### Good to have
1. requirements.txt

### Eventually
1. Unit tests
2. Quiz/game mode

