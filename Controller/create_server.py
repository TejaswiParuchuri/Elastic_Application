#get all the instances which are in running and pending statuses
def get_starting_running_instance_ids():
    instances = boto3.resource('ec2').instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running']}])
    i = 1
    #to print the number of the instance
    print("Instances in pending or running status: ")
    for instance in instances:
        print("Instance ", i, ": ", instance.id, instance.instance_type)
        i += 1
    return instances

#create new instances based on messages in request queue and currently active instances
def create_new_running_instances(number=1):
    active_instances = get_starting_running_instance_ids()

    i = 0
    active_instance_ids = []
    max_num_instances = 10
    num_instances_to_start = number + 3
    for instance in active_instances:
        active_instance_ids.append(instance.id)
        i += 1

    print("number of running or pending instances : ", len(active_instance_ids))
    if len(active_instance_ids) > 0:
        num_instances_to_start = num_instances_to_start - len(active_instance_ids)

    print("max_instances to start : ", max_num_instances)
    num_instances_to_start = min(max_num_instances, num_instances_to_start)
    print("Final instances to start : ", num_instances_to_start)
    if num_instances_to_start > 0:
        create_new_instance(num_instances_to_start)
    print("check running instance end")

def create_new_instance(number=1):
    ec2 = boto3.resource('ec2')

    # create new EC2 instances, based on the number sent in the arguement
    instances = ec2.create_instances(
        ImageId='ami-08a41a3ae9b75c195',
        MinCount=1,
        MaxCount=number,
        InstanceType='t2.micro',
        KeyName='CSE546ProjectKey'
    )
    print("New Instances created: ", instances)
