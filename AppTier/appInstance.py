import schedule
import subprocess
import boto3
import json
import botocore
import os
import time

INPUT_BUCKET_NAME='cse546-input-p1' #input s3 bucket to download images for classifier
OUTPUT_BUCKET_NAME='cse546-output-p1' #output s3 bucket to store results

# schedule a job to check for any messages available in SQS request qeueue
def check():
    check_message_queue()
    print("Checking SQS...")

#check if any messages are available in request queue. If any messages are available process the messages otherwise terminate the instance
def check_message_queue():
    #get the available message from SQS request queue
    response = get_message()
    if response is not None and response.body is not None:
        print("Message Found in SQS....")
        #if messages are available in SQS request queue cancel the current schedule job and process the message
        schedule.CancelJob
        process_message(response.body)
        #once message is processed start the scheduler
        schedule.every(10).seconds.do(check)
    #if no message is found in SQS request queue terminate the current instnce
    else:
        print("Queue Empty")
        terminate_instance()

#method to terminate the current instance
def terminate_instance():
    current_instance= subprocess.check_output(["ec2metadata", "--instance-id"], universal_newlines=True).strip()

    client = boto3.client('ec2')
    response = client.terminate_instances(
        InstanceIds=[
            current_instance
        ]
    )

#get the message that is there in SQS request queue and then delete the message from queue		
def get_message():
    sqs = boto3.resource('sqs')
    queue = sqs.Queue('https://sqs.us-east-1.amazonaws.com/992611621996/CSE546_RequestQueue.fifo')
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

#method to process the message that is received from SQS request queue
def process_message(body):
    message_dict = json.loads(body)
    if message_dict['image_filename'] is not None:
        #method to download the file from s3 bucket based on the url provided in SQS message
        download_file_from_s3(message_dict['image_filename'])
        #mehthod to run classifier on the downloaded image from s3
        run_classifier(file=message_dict['image_filename'])
		
#method to download the image from s3 input bucket based on the url provided in SQS request queue message
def download_file_from_s3(key):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(INPUT_BUCKET_NAME).download_file(key, key)
    except botocore.exceptions.ClientError as excep:
        if excep.response['Error']['Code'] == "404":
            print("The image doesn't exist in s3.")
        else:
            raise

#method to execute the provided classifier on the downloaded image and save the result to stdout.txt and push the result to SQS Response queue
def run_classifier(file):
    if file is not None:
        os.system("python3 ~/classifier/image_classification.py "+file+" > classification_result.txt")
        if os.path.exists(file):
           os.remove(file)
        message=create_SQS_message(file,'classification_result.txt')
        sqs=boto3.resource('sqs')
        queue=sqs.Queue('https://sqs.us-east-1.amazonaws.com/992611621996/CSE546_ResponseQueue.fifo')
        response=queue.send_message(
                MessageBody=message,
                MessageGroupId='CSE546Project')
        upload_result(file,'classification_result.txt')

#method to create message that has to be sent to SQS Response queue. Message is json with image file name and result
def create_SQS_message(file,resultfile):
    file_data=open(resultfile,"r")
    result=file_data.readline()
    file_data.close()
    print(file,result)
    message={}
    message['image_filename']=file
    message['result']=result
    return json.dumps(message)

#method to upload the result to s3 output bucket
def upload_result(key,resultfile):
    s3 = boto3.resource('s3')
    try:
        name=key.split('.')[:-1]
        file_data=open(resultfile,"r")
        result=file_data.readline()
        file_data.close()
        if '2021_' in key:
            img_name=key.split('2021_')[-1]
            img_final_name=img_name.split('.')[0]
        else:
            img_final_name=key.split('.')[0]
        result=img_final_name+','+result.replace('\n','')
        #print(result)
        file_data=open(resultfile,"w")
        file_data.write(result)
        file_data.close()
        s3.Bucket(OUTPUT_BUCKET_NAME).upload_file(resultfile,".".join(name)+".txt")
    except botocore.exceptions.ClientError as excep:
        if excep.response['Error']['Code'] == "404":
            print("The text does not exist in s3.")
        else:
            raise

schedule.every(10).seconds.do(check)
		
#run until the server is terminated
while True:
    schedule.run_pending()
    time.sleep(10)
