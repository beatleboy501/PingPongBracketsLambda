from __future__ import print_function
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal
from base64 import b64encode, b64decode
from json import dumps, loads, JSONEncoder
import pickle

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        elif isinstance(o, set):
            return list(o)
        return super(DecimalEncoder, self).default(o)


dynamodb = boto3.resource("dynamodb")
brackets_table = dynamodb.Table('brackets')
games_table = dynamodb.Table('games')

def lambda_handler(event, context):
    bracket_id = event.get('pathParameters').get('bracketId')
    if(bracket_id is not None):
        try:
            brackets_response = brackets_table.get_item(
                Key={
                    'id': bracket_id
                }
            )
            games_response = games_table.query(
                IndexName='bracketId-index',
                KeyConditionExpression=Key('bracketId').eq(bracket_id)
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {
                'statusCode': 404,
                'isBase64Encoded': False,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps('Bracket / Games Not Found for Bracket Id: ' + bracket_id)
            }
        else:
            bracket = brackets_response['Item']
            rounds = get_rounds(games_response['Items'])
            users = get_users(list(bracket.get('users')))
            jsonBody = {
                'bracket': bracket,
                'users': users,
                'rounds': rounds
            }
            return {
                'statusCode': 200,
                'isBase64Encoded': False,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(jsonBody, indent=4, cls=DecimalEncoder)
            }
    else:
        return {
            'statusCode': 400,
            'isBase64Encoded': False,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps('Missing bracketId')
        }

def get_rounds(games):
    rounds = {}
    for game in games:
        index = str(int(game.get('round')))
        round = rounds.get(index)
        if round is not None:
            round.append(game)
        else:
            rounds[index] = [game]
    print('rounds')
    print(rounds)
    return rounds


def get_users(user_ids):
    users = []
    invokeLambda = boto3.client('lambda', region_name='us-east-1')
    for id in user_ids:
       response = invokeLambda.invoke(FunctionName = 'get_cognito_user_by_id', InvocationType = 'RequestResponse', Payload = json.dumps({"id": id}))
       user = json.loads(response['Payload'].read()).get('body')
       if(user is not None): users.append(json.loads(user))
    return users
