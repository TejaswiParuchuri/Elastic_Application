import schedule
import time
import boto3
import threading


def isTreadAlive(threads):
    for t in threads:
        if t.isAlive():
            return 1
    return 0

#job related to controller for spinning up app-tier instances
def controller_job():
    check_request_queue()
    print("Controller job - Checking request queue has started...")

def check_request_queue():
    #get all the messages in the Request SQS Queue
    sqs = boto3.resource('sqs')
    response = sqs.get_queue_by_name(QueueName='CSE546_RequestQueue.fifo')
    print("ApproximateNumberOfMessages: ", response.attributes.get('ApproximateNumberOfMessages'))
    #Check request SQS queue to start app instances accordingly
    num_messages = int(response.attributes.get('ApproximateNumberOfMessages'))
    if num_messages > 0:
        schedule.CancelJob
        num_instances = num_messages
        print("initial no of instances to start: ", num_instances)
        if num_instances > 17:
            num_instances = 17
            print("no of instances were greater that 17, so made them equal to 17")
        print("new no of instances to start: ", num_instances)
        create_new_running_instances(number=num_instances)
        time.sleep(20)
    else:
        global instance_number_name
        instance_number_name=0
        print("no of messages are less than or equal to 0")
    print("Controller job - Checking request queue has ended")

def create_instance(instance_name):
    ec2 = boto3.resource('ec2')
    instances = ec2.create_instances(
                    ImageId='ami-07e50df3335210dbc',
                    MinCount=1,
                    MaxCount=1,
                    InstanceType='t2.micro',
                    KeyName='CSE546ProjectKey',
                    TagSpecifications=[
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                    {               
                                        'Key': 'Name',
                                        'Value': instance_name
                                    },
                                    ]               
                        },
                    ]
                )

#create new instances based on messages in request queue and currently active instances
def create_new_running_instances(number=1):
    #get all the instances which are in running and pending statuses
    active_instances = boto3.resource('ec2').instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running']}])
    count=0
    for active_instance in active_instances:
        count+=1
    max_num_instances = 17 #as already 3 instances for controller,webtier and app controller are already there in running or stopped state
    num_instances_to_start=number+2 #2 is added to number as already 2 instances for controller,webtier are in running state
    print("number of running or pending instances : ",count)
	
    if count > 0:
        num_instances_to_start = num_instances_to_start - count
		
    num_instances_to_start = min(max_num_instances, num_instances_to_start ) 
    print("Final instances to start : ", num_instances_to_start)
    #start the instances
    createThreads = []
    if num_instances_to_start > 0:
        for i in range(0,num_instances_to_start):
            global instance_number_name
            instance_number_name+=1
            tthread = threading.Thread(
                target=create_instance, args=('AppTier'+str(instance_number_name)))
            tthread.start()
            createThreads.append(tthread)
            time.sleep(0.05)
            
    while(isTreadAlive(createThreads)):
            continue



#the controller job runs every 20 seconds
schedule.every(20).seconds.do(controller_job)
instance_number_name=0

while True:
    schedule.run_pending()
    time.sleep(20)
