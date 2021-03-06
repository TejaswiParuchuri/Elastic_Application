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

def job():
    check_queue_message()
    print("I'm working...")


schedule.every(10).seconds.do(job)


def check_queue_message():
    response = receive_message()
    if response is not None and response.body is not None:
        print("cancelling sheduled jobs")
        schedule.CancelJob
        print(response.body)
        process_message(response.body)
        print("scheduling 10s")
        schedule.every(10).seconds.do(job)
    else:
        print("Queue Empty")
        #terminate_instance()

def terminate_instance():
    rec = subprocess.check_output(["ec2metadata", "--instance-id"], universal_newlines=True).strip()
    print("current instance is:", rec)

    client = boto3.client('ec2')
    response = client.terminate_instances(
        InstanceIds=[
            rec
        ]
    )
    print(response)


		
def receive_message(name="CSE546_RequestQueue"):
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
    print(response)
    for message in response:
        message.delete()
        return message
		
def process_message(body):
    message_dict = json.loads(body)

    if message_dict['image_filename'] is not None:
        print(message_dict['image_filename'])
        download_file(message_dict['image_filename'])
        run_classifier(file=message_dict['image_filename'])
		
def download_file(key):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(INPUT_BUCKET_NAME).download_file(key, key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
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
        #createFile("stdout.txt", result)
        name=key.split('.')[:-1]
        s3.Bucket(OUTPUT_BUCKET_NAME).upload_file(result,"".join(name)+".txt")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

'''def createFile(file,result):
	with open(file, 'w') as filetowrite:
		filetowrite.write(result)'''
		
		
while True:
    schedule.run_pending()
    time.sleep(10)
