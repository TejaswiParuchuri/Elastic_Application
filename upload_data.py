import os
import sys
import time
import shutil
import boto3
import json
import threading
from botocore.exceptions import ClientError
from aws_credentials import *
from flask import Flask, render_template, request, redirect, url_for
import socket
import logging

REGION = "us-east-1"
UPLOAD_PATH = 'uploads'
RESULTS_PATH = 'results'
INPUT_BUCKET = "cse546-input-p1"
OUTPUT_BUCKET = "cse546-output-p1"


def isTreadAlive(threads):
    for t in threads:
        if t.isAlive():
            return 1
    return 0

def download_file(key):
    s3 = boto3.resource('s3')

    try:
        s3.Bucket(OUTPUT_BUCKET).download_file(key, RESULTS_PATH+"/"+key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    return 1

def _key_existing_size__list(key):
    """return the key's size if it exist, else None"""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(OUTPUT_BUCKET)
    objs = list(bucket.objects.filter(Prefix=key).limit(1))
    if objs:
        return True
    else:
        return False
    # response = s3.Object(OUTPUT_BUCKET,key).exists()
    # print(response)
    # return response

def receive_message(name="CSE546_ResponseQueue"):
    sqs = boto3.resource('sqs')
    queue = sqs.Queue('https://sqs.us-east-1.amazonaws.com/992611621996/CSE546_ResponseQueue.fifo')
    response = queue.receive_messages(
        
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=1,
        VisibilityTimeout=120,
        WaitTimeSeconds=2
    )
    print("64: ",response)
    for message in response:
        message.delete()
        return message

def createSQSMessage(image_filename, result_filename, processed):
    message = {}
    message['image_filename'] = image_filename
    message['result_filename'] = result_filename
    message['processed'] = processed
    message['time'] = time.time()
    return json.dumps(message)


def uploadS3Input(myfile, bucketName, object_name=None):
    print(" ---- s3 upload")
    s3_client = boto3.client('s3',
                             aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             region_name=REGION
                             )

    if object_name is None:
        object_name = myfile

    try:
        message = {}
        response = s3_client.upload_file(UPLOAD_PATH+"/"+myfile, bucketName,
                                         object_name, Callback=ProgressPercentage(UPLOAD_PATH+"/"+myfile))
        print(" Uploading image file : " + str(myfile) + " : " + str(response))
        message = createSQSMessage(
            myfile, "noresultfile", False)
        sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=REGION
        )
        print(socket.gethostname())
        response = sqs_client.list_queues()
        print(response['QueueUrls'][0])
        queueUrl = 'https://sqs.us-east-1.amazonaws.com/992611621996/CSE546_RequestQueue.fifo'
        # queueUrl = response['QueueUrls'][0]
        response = sqs_client.send_message(
            QueueUrl=queueUrl,
            MessageBody=message,
            MessageGroupId=str(socket.gethostname())
        )
        print("Message has been sent to queue : " +
              str(queueUrl) + " : " + str(response['MessageId']))

    except ClientError as e:
        logging.error(e)
        return False
    return True


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = True  # threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        # with self._lock:
        self._seen_so_far += bytes_amount
        percentage = (self._seen_so_far / self._size) * 100
        sys.stdout.write(
            "\r%s  %s / %s  (%.2f%%)" % (
                self._filename, self._seen_so_far, self._size,
                percentage))
        sys.stdout.flush()

def getResponseQueueMessageCount(name="CSE546_ResponseQueue.fifo"):
    sqs = boto3.resource('sqs')

    response = sqs.get_queue_by_name(QueueName='CSE546_ResponseQueue.fifo')
    print(response.url)
    print("VisibilityTimeout: ", response.attributes.get('VisibilityTimeout'))
    print("ApproximateNumberOfMessages: ", response.attributes.get('ApproximateNumberOfMessages'))
    print("ApproximateNumberOfMessagesNotVisible: ", response.attributes.get('ApproximateNumberOfMessagesNotVisible'))
    print("148: ",response)
    return int(response.attributes.get('ApproximateNumberOfMessages'))

def main():
    try:
        uploadkeys = os.listdir(UPLOAD_PATH+"/")
        # uploadkeys = [entry.split(".")[0] for entry in uploadkeys]
        start_time = time.time()
        uploadThreads = []
        for uploadkey in uploadkeys:
            tthread = threading.Thread(
                target=uploadS3Input, args=(uploadkey, INPUT_BUCKET,))
            tthread.start()
            uploadThreads.append(tthread)
            time.sleep(0.05)
            # uploadS3Input(uploadkey, INPUT_BUCKET,)

        while(isTreadAlive(uploadThreads)):
            continue

        for uploadkey in uploadkeys:
            shutil.move(UPLOAD_PATH+"/"+uploadkey, RESULTS_PATH+"/"+uploadkey)
            # os.remove(UPLOAD_PATH+"/"+uploadkey)

        end_time = time.time()
        print(" All S3 uploads are done. Time taken : " + str(end_time-start_time))
    except Exception as e:
        raise e
    print("Waiting 10 sec")
    time.sleep(10)
    print("started again")
    alreadyDownloaded = {}
    print("180: ",uploadkeys)
    while(len(alreadyDownloaded.keys())<len(uploadkeys)):
        while getResponseQueueMessageCount()>0:
            response = receive_message()
            print("184: ",response)
            if response is not None:
                print("186: ",response.body)
                message = json.loads(response.body)
                print("188: ",message)
                if message['image_filename'] is not None and message["image_filename"] in uploadkeys:
                    print("190: Recieving Message : ",message)
                    alreadyDownloaded[message["image_filename"]] = message["result"]
        print("192: ", alreadyDownloaded)
        time.sleep(2)

    # results = {}
    # for uploadkey in uploadkeys:
    #     f = open(RESULTS_PATH+"/"+uploadkey.split(".")[0]+".txt", "r")
    #     results[uploadkey] = str(f.read())
    print("199 : ",alreadyDownloaded)
    return alreadyDownloaded

def download(uploadkeys):
    print(uploadkeys)
    while(len(alreadyDownloaded.keys())>=len(uploadkeys)):
       while getResponseQueueMessageCount()>0:
            response = receive_message()
            print("182: ",response)
            if response is not None:
                print("183: ",response.body)
                message = json.loads(response.body)
                print("185: ",message)
                if message['image_filename'] is not None and message["image_filename"] in uploadkeys:
                    print("186: Recieving Message : ",message)
                    alreadyDownloaded[message["image_filename"]] = message["result"]
            time.sleep(1)

    # results = {}
    # for uploadkey in uploadkeys:
    #     f = open(RESULTS_PATH+"/"+uploadkey.split(".")[0]+".txt", "r")
    #     results[uploadkey] = str(f.read())
    print(alreadyDownloaded)
    return alreadyDownloaded

# def download(uploadkeys):
#     if not uploadkeys:
#         return
#     alreadyDownloaded = []
#     while(len(alreadyDownloaded)!=len(uploadkeys)):
#         print(len(alreadyDownloaded)," ",len(uploadkeys)," :", len(alreadyDownloaded)!=len(uploadkeys))
#         for uploadkey in uploadkeys:
#             if uploadkey in alreadyDownloaded:
#                 continue
#             uploadkey = ".".join(uploadkey.split(".")[:-1])+".txt"
#             if _key_existing_size__list(uploadkey) and  download_file(uploadkey):
#                 alreadyDownloaded.append(uploadkey)
    
#     results = {}
#     for uploadkey in uploadkeys:
#         f = open(RESULTS_PATH+"/"+uploadkey.split(".")[0]+".txt", "r")
#         results[uploadkey] = str(f.read())
#     print(results)
#     return redirect(url_for('index'))

if __name__ == '__main__':
    main()
