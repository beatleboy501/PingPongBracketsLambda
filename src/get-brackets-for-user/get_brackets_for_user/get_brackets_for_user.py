import boto3
import json
import os


dynamodb = boto3.resource("dynamodb")
client = boto3.client('dynamodb')
brackets_table = dynamodb.Table('brackets')
bracket_users_table = dynamodb.Table('user-brackets')


def lambda_handler(event, context):
    # get full list of users
    user_list = get_users()

    # look up brackets where owner == user_id
    user_id = event.get('pathParameters').get('userId')

    # map id to user from list and return as owner brackets
    owned = get_owned_brackets(client, user_id, user_list)

    # look up bracket:users
    user_brackets = get_user_brackets(client, user_id)

    participant_brackets = get_participant_brackets(client, user_brackets, user_list)

    # map owner to user id from list
    # return as participant brackets
    body = {"owned": owned, "participant": participant_brackets}

    return {
        "statusCode": 200,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(body),
    }


def get_owned_brackets(client, user_id, user_list):
    resp = client.query(
       TableName='brackets',
       IndexName='owner-index',
       ExpressionAttributeNames={
           "#o": "owner",
        },
       ExpressionAttributeValues={
           ':u': {
               'S': user_id,
           },
       },
       KeyConditionExpression='#o = :u',
    )

    # will always return list
    owned_brackets = resp.get('Items')
    return list(map(lambda x: format_bracket(x, user_id, user_list), owned_brackets))


def get_user_brackets(client, user_id):
    resp = client.query(
        TableName='user-brackets',
        Select='ALL_ATTRIBUTES',
        KeyConditionExpression="#u = :u",
        ExpressionAttributeValues={
            ":u":  {"S": user_id}
        },
        ExpressionAttributeNames={
            "#u": "userId"
        }
    )
    return list(map(lambda x: x.get('bracketId').get('S'), resp.get('Items')))


def get_participant_brackets(client, bracket_ids, user_list):
    keys = [{'id': {'S': i}} for i in bracket_ids]
    resp = client.batch_get_item(
        RequestItems={
            'brackets': {
                'Keys': keys
            }
        }
    )
    brackets = list(map(lambda x: format_bracket(x, x.get('owner').get('S'), user_list), resp.get('Responses').get('brackets')))
    print(brackets)
    return brackets


def format_bracket(bracket, ownerId, user_list):
    owner = get_owner_name_by_id(ownerId, user_list)
    return {
      "title": bracket['title']['S'],
      "owner": owner,
      "participantCount": len(bracket['users']['L']),
      "id": bracket['id']['S']
    }


def get_users():
    region = get_region()
    invokeLambda = boto3.client('lambda', region_name=region)
    response = invokeLambda.invoke(FunctionName = 'get_cognito_users', InvocationType = 'RequestResponse')
    users = json.loads(response['Payload'].read()).get('body')
    return users


def get_region():
    try:
      region = os.environ['AWS_REGION']
    except:
      # Not in Lambda environment
      region = "us-east-1"
    return region


def get_owner_name_by_id(id, user_list):
    users = json.loads(user_list)
    found = next((x for x in users if x.get('sub') == id), None)
    if(found):
        full_name = found.get('given_name') + ' ' + found.get('family_name')
        return full_name
    else:
        return id
