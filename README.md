#### Web Tier:
#### Controller:
#### App Tier: 
App Tier is created from our own AMI which consists of the given classifier code along with the additional code to run the given classifier. <br/>
👉As soon as the instance is created from controller from the given AMI, a cronjob will start which will execute the test.sh shell script which in turn will execute startup.py <br/>
👉startup.py will basically check for any messages available in SQS request queue.<br/>
👉If any messages are available in SQS request queue, the images will be downloaded from s3 bucket and passed to classifier and the result will be stored in s3 bucket and pushed to SQS response queue and further checks for any avaialble messages in SQS request queue <br/>
👉If no messages are available the instance will be terminated.
        
