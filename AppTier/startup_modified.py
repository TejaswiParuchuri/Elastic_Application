import schedule
import time
import subprocess
import boto3
import json
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import json
import sys
import numpy as np
import botocore
import os

INPUT_BUCKET_NAME='cse546-input'
OUTPUT_BUCKET_NAME='cse546-output'

def check():
    check_message_queue()
    print("Checking SQS...")


def check_message_queue():
    response = get_message()
    if response is not None and response.body is not None:
        print("Message Found in SQS....")
        schedule.CancelJob
        process_message(response.body)
        schedule.every(10).seconds.do(check)
    else:
        print("Queue Empty")
        terminate_instance()

def terminate_instance():
    current_instance= subprocess.check_output(["ec2metadata", "--instance-id"], universal_newlines=True).strip()

    client = boto3.client('ec2')
    response = client.terminate_instances(
        InstanceIds=[
            current_instance
        ]
    )

		
def get_message(name="CSE546_RequestQueue"):
    sqs = boto3.resource('sqs')
    queue = sqs.Queue('https://sqs.us-east-1.amazonaws.com/322990531231/CSE546_RequestQueue')
    response = queue.receive_messages(
        
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=1,
        VisibilityTimeout=120,
        WaitTimeSeconds=2
    )
    for message in response:
        message.delete()
        return message
		
def process_message(body):
    message_dict = json.loads(body)
    if message_dict['image_filename'] is not None:
        download_file_from_s3(message_dict['image_filename'])
        run_classifier(file=message_dict['image_filename'])
		
def download_file_from_s3(key):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(INPUT_BUCKET_NAME).download_file(key, key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The image doesn't exist in s3.")
        else:
            raise
		
def run_classifier(file):
    if file is not None:
        os.system("python3 ~/classifier/image_classification.py "+file+" > stdout.txt")
        if os.path.exists(file):
           os.remove(file)
        upload_result(file,'stdout.txt')
		
def upload_result(key,result):
    s3 = boto3.resource('s3')
    try:
        name=key.split('.')[:-1]
        s3.Bucket(OUTPUT_BUCKET_NAME).upload_file(result,".".join(name)+".txt")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The text does not exist in s3.")
        else:
            raise

schedule.every(10).seconds.do(check)
		
while True:
    schedule.run_pending()
    time.sleep(10)
