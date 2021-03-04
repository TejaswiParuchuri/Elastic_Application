import os
import sys
import time
import shutil
import boto3
import json
import threading
from botocore.exceptions import ClientError
from aws_credentials import *

REGION = "us-east-1"
UPLOAD_PATH = 'uploads'
RESULTS_PATH = 'results'
INPUT_BUCKET = "input-images-cc"
OUTPUT_BUCKET = "output-text-cc"


def isTreadAlive(threads):
    for t in threads:
        if t.isAlive():
            return 1
    return 0


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
        print(" Uploading video file : " + str(myfile) + " : " + str(response))
        message = createSQSMessage(
            myfile, "noresultfile", False)
        sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=REGION
        )

        # response = sqs_client.list_queues()
        # print(response['QueueUrls'][0])
        queueUrl = 'https://queue.amazonaws.com/130782845993/RequestQueue'
        response = sqs_client.send_message(
            QueueUrl=queueUrl,
            DelaySeconds=2,
            MessageBody=message
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


if __name__ == '__main__':
    main()
