import boto3
import decimal
import json
from time import sleep


dynamodb = boto3.resource("dynamodb")
gamesTable = dynamodb.Table('games')
bracketsTable = dynamodb.Table('brackets')

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

def lambda_handler(event, context):
    game_id = event.get('pathParameters').get('gameId')
    body = json.loads(event.get('body'))
    result = body.get('result')
    next_game_id = body.get('nextGameId')
    response = []
    updated_game = gamesTable.update_item(
        Key={'id': game_id},
        UpdateExpression='SET #rs = :val1',
        ExpressionAttributeValues={
            ":val1": result
        },
        ExpressionAttributeNames={
            "#rs": "result"
        },
        ReturnValues="ALL_NEW",
    )
    response.append(updated_game)
    winner_id = result.get('winner').get('participantId')
    if next_game_id.lower() == "champion":
        bracket_id = body.get('bracketId')
        bracketsTable.update_item(
            Key={'id': bracket_id},
            UpdateExpression='SET #attr1 = :val1',
            ExpressionAttributeNames={'#attr1': 'winner'},
            ExpressionAttributeValues={':val1': winner_id},
            ReturnValues="NONE"
        )
    else:
        updated_next_game = gamesTable.update_item(
            Key={'id': next_game_id },
            UpdateExpression="ADD participants :element",
            ExpressionAttributeValues={":element": set([winner_id])},
            ReturnValues="ALL_NEW"
        )
        response.append(updated_next_game)
    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response, indent=4, cls=DecimalEncoder)
    }
