import json
import time
import datetime
import collections
from random import randint


## LAMBDA HANDLER ##
def lambda_handler(event, context):
    # TODO: THIS IS A MOCK RESPONSE - Save to Dynamo and return object
    title = get_title(event)
    if (title is not None):
        return success_response(title)
    else:
        return error_response()


def get_title(event):
    body = event.get('body')
    if (body is None): return None
    title = None
    if (is_json(body)):
        title = json.loads(body).get('title')
    elif (isinstance(body, collections.Mapping)):
        title = body.get('title')
    return title


## IS JSON ##
def is_json(body):
    try:
        json.loads(body)
    except:
        return False
    return True


## ERROR RESPONSE ##
def error_response():
    return {
        'statusCode': 400,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({'error': 'No Title Provided in Request'})
    }


## SUCCESS RESPONSE ##
def success_response(title):
    user_id = randint(1, 996)
    game_id = randint(1, 996)
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'id': randint(0, 1000),
            'title': title,
            'owner': user_id + 1,
            'winner': None,
            'users': [
                {
                    'id': user_id + 1,
                    'first': 'Andrew',
                    'second': 'Allison',
                    'rank': 4,
                    'seed': 1
                },
                {
                    'id': user_id + 2,
                    'first': 'Marcus',
                    'second': 'Guimaraes',
                    'rank': 1,
                    'seed': 4
                },
                {
                    'id': user_id + 3,
                    'first': 'Ryan',
                    'second': 'Kroonenberg',
                    'rank': 3,
                    'seed': 3
                },
                {
                    'id': user_id + 4,
                    'first': 'Jeff',
                    'second': 'Bezos',
                    'rank': 2,
                    'seed': 2
                }
            ],
            'rounds': [
                [
                    {
                        'id': game_id + 1,
                        'participants': [user_id + 1, user_id + 2],
                        'round': 1,
                        'result': None
                    },
                    {
                        'id': game_id + 2,
                        'participants': [user_id + 3, user_id + 4],
                        'round': 1,
                        'result': {
                            'winner': {
                                'participantId': user_id + 4,
                                'score': 10
                            },
                            'loser': {
                                'participantId': user_id + 3,
                                'score': 7
                            }
                        }
                    }
                ],
                [
                    {
                        'id': game_id + 3,
                        'participants': [None, user_id + 4],
                        'round': 2,
                        'result': None
                    }
                ]
            ],
            'createdAt': timestamp,
            'lastUpdated': timestamp
        })
    }
