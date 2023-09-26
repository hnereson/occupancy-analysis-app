import pandas as pd
from dotenv import load_dotenv
import os 
import boto3 
import json  
from io import StringIO    

load_dotenv()
MASTER_ACCESS_KEY = os.getenv("MASTER_ACCESS_KEY")
MASTER_SECRET = os.getenv("MASTER_SECRET")
board_id = os.getenv('board_id')

def s3_init():  
    
    # --- s3 client --- 
    s3 = boto3.client('s3', region_name = 'us-west-1', 
          aws_access_key_id=MASTER_ACCESS_KEY, 
          aws_secret_access_key=MASTER_SECRET) 
    return s3 

def grab_s3_file(f, bucket, idx_col=None, is_json=False):
    s3 = s3_init()
    data = s3.get_object(Bucket=bucket, Key=f)['Body'].read().decode('utf-8') 
    
    # Check if the file is a JSON
    if is_json:
        return json.loads(data)  # Return the parsed JSON data as a dictionary
    
    # If the file is a CSV
    if idx_col is None:
        data = pd.read_csv(StringIO(data)) 
    else:
        data = pd.read_csv(StringIO(data), index_col=idx_col)

# we can add a pickle function to this if needed
    return data 