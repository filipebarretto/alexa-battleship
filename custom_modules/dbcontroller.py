import os
import boto3
from custom_modules import data
import decimal
import json

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')


# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)


def convert_board(board):
    new_board = [[int(board[x][y]) for y in range(data.BOARD_WIDTH)] for x in range(data.BOARD_HEIGHT)]
    return new_board


# SAVES THE BOARD TO DYNAMODB
def save_board(user_id, user_board, opponent_board, user_hits, opponent_hits):
    print("Saving board to DynamoDB")
    
    table = dynamodb.Table(os.environ[data.CURRENT_GAMES_TABLE])
    item = {
        'id': user_id,
        'user_board': user_board,
        'opponent_board': opponent_board,
        'user_hits': user_hits,
        'opponent_hits': opponent_hits
    }

    response = table.put_item(Item=item)

    return response



def load_board(user_id):
    print("Loading board from DynamoDB")
    table = dynamodb.Table(os.environ[data.CURRENT_GAMES_TABLE])
    
    # fetch todo from the database
    result = table.get_item(Key={'id': user_id})
    
    item = {
        'id': result['Item'].get("id"),
        'user_board': convert_board(result['Item'].get("user_board")),
        'opponent_board': convert_board(result['Item'].get("opponent_board")),
        'user_hits': int(result['Item'].get("user_hits")),
        'opponent_hits': int(result['Item'].get("opponent_hits"))
    }

    return item

def save_board_img(user_id, player, png_data):
    print("Saving board image to S3")
    s3_bucket = os.environ[data.BOARD_IMAGES_BUCKET]
    obj_key = user_id + "-" + player + ".png"
    
    print("S3 Bucket: " + s3_bucket)
    print("Obj Key: " + obj_key)
    
    response = s3.put_object(Body=png_data, Bucket=s3_bucket, Key=obj_key)
    return response

def get_board_img(user_id, player):
    print("Loading board image from S3")
    s3_bucket = os.environ[data.BOARD_IMAGES_BUCKET]
    obj_key = user_id + "-" + player + ".png"
    
    url = s3.generate_presigned_url("get_object", Params = {"Bucket": s3_bucket, "Key": obj_key}, ExpiresIn = 3600)

    return url

