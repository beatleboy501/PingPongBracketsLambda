import datetime
import json
import math
import time
from random import randint
from collections import Mapping

## LAMBDA HANDLER ##
def lambda_handler(event, context):
    # TODO: THIS IS A MOCK RESPONSE - Save to Dynamo and return object
    request_params = get_request_params(event)
    if (are_valid(request_params)):
        return success_response(request_params)
    else:
        return error_response()


## GET REQUEST BODY PARAMETERS ##
def get_request_params(event):
    body = event.get('body')
    if (body is None): return None
    title = None
    users = None
    owner = None
    if (is_json(body)):
        jsonBody = json.loads(body)
        title = jsonBody.get('title')
        users = jsonBody.get('users')
        owner = jsonBody.get('owner')
    elif (isinstance(body, Mapping)):
        title = body.get('title')
        users = body.get('users')
        owner = body.get('owner')
    return (title, users, owner)


## IS JSON CHECK ##
def is_json(body):
    try:
        json.loads(body)
    except:
        return False
    return True


## ARE REQUEST PARAMETERS VALID ##
def are_valid(request_params):
    try:
        (title, users, owner) = request_params
        return title is not None and users is not None and users != [] and owner is not None
    except:
        return False


## ERROR RESPONSE ##
def error_response():
    return {
        'statusCode': 400,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': 'Missing non-optional parameters in Request'})
    }


## SUCCESS RESPONSE ##
def success_response(request_params):
    (title, users, owner) = request_params
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    bracket = create_bracket(title, owner, users, timestamp)
    rounds = create_rounds(users)
    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'bracket': bracket,
            'users': users,
            'rounds': rounds
        })
    }


## CREATE BRACKET OBJECT ##
def create_bracket(title, owner, users, timestamp):
    userIds = list(map(lambda user: user['id'], users))
    return { # This will need to be saved in the Bracket table in DynamoDB
        'id': randint(0, 1000),
        'title': title,
        'owner': owner,
        'winner': None,
        'users': userIds,
        'createdAt': timestamp,
        'lastUpdated': timestamp
    }


## CREATE TOURNAMENT ROUNDS ##
def create_rounds(users):
    round_names = ['Final', 'Semifinal', 'Quarterfinal', '1/8 Final', '1/16 Final', '1/32 Final', '1/64 Final']
    def divide_users(arr, depth, m):
        if len(complements) <= depth:
            complements.append(2 ** (depth + 2) + 1)
        complement = complements[depth]
        for i in range(2):
            if complement - arr[i] <= m:
                arr[i] = [arr[i], complement - arr[i]]
                divide_users(arr[i], depth + 1, m)
    def iter(model, next_round_id, next_round_num, round_name_index, rounds, users):
        for brack in model:
            if isinstance(brack, list) and isinstance(brack[0], list):
                game = create_game(None, None, next_round_id, next_round_num, round_names[round_name_index])
                rounds.append(game)
                iter(brack, game.get('id'), next_round_num - 1, round_name_index + 1, rounds, users)
            else:
                part_1 = next((user for user in users if user.get('seed') == brack[0]), None)
                part_2 = next((user for user in users if user.get('seed') == brack[1]), None)
                game = create_game(part_1.get('id'), part_2.get('id'), next_round_id, next_round_num, round_names[round_name_index])
                rounds.append(game)
    num_of_users = len(users)
    bracket_model = [1, 2]
    complements = []
    divide_users(bracket_model, 0, num_of_users) # at this point we have nested arrays showing the bracket by seed, need to iterate over it and create the actual games
    num_of_rounds = int(math.log(len(users), 2))
    rounds = []
    final = create_game(None, None, 'Champion', num_of_rounds, round_names[0])
    rounds.append(final)
    iter(bracket_model, final.get('id'), num_of_rounds - 1, 1, rounds, users)
    return rounds


## CREATE GAME OBJECT ##
def create_game(part_1, part_2, next_game, round, round_name):
    return { # This will need to be saved in the Game table in DynamoDB
        'id': randint(1, 9999),
        'participants': [part_1, part_2],
        'next_game': next_game,
        'round': round,
        'round_name': round_name,
        'result': None
    }
