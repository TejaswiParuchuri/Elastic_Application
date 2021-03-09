import schedule
import time
import boto3
import create_server

#job related to controller for spinning up app-tier instances
def controller_job():
    check_request_queue()
    print("Controller job - Checking request queue has started...")

#get all the messages in the Request SQS Queue
def get_request_queue_messages(name="CSE546_RequestQueue.fifo"):
    sqs = boto3.resource('sqs')
    response = sqs.get_queue_by_name(QueueName='CSE546_RequestQueue.fifo')
    print("Request Queue URL: ", response.url)
    print("VisibilityTimeout of Request Queue: ", response.attributes.get('VisibilityTimeout'))
    print("ApproximateNumberOfMessages: ", response.attributes.get('ApproximateNumberOfMessages'))
    print("ApproximateNumberOfMessagesNotVisible: ", response.attributes.get('ApproximateNumberOfMessagesNotVisible'))
    return response


def check_request_queue():
    #Check request SQS queue to start app instances accordingly
    response = get_request_queue_messages()
    num_messages = int(response.attributes.get('ApproximateNumberOfMessages'))
    if num_messages > 0:
        schedule.CancelJob
        num_instances = int(num_messages)
        print("initial no of instances to start: ", num_instances)
        if num_instances > 10:
            num_instances = 10
            print("no of instances were greater that 10, so made them equal to 10")
        print("new no of instances to start: ", num_instances)
        create_server.create_new_running_instances(number=num_instances)
        time.sleep(20)
    else:
        print("no of messages are less than or equal to 0")
    print("Controller job - Checking request queue has ended")


#the controller job runs every 20 seconds
schedule.every(20).seconds.do(controller_job)

while True:
    schedule.run_pending()
    time.sleep(20)
