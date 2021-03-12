#### Team Members:
    Gunda Akshay Kumar (1217179379)
    Kusuma Kumari Vanteru (1217031218)
    Tejaswi Paruchuri (1213268054)

#### Elastic IP:
    Elatic IP Address:  34.236.13.196:5000

#### S3 Buckets:
    S3 input bucket:   cse546-input-p1
    S3 output bucket:  cse546-output-p1
    
#### SQS FIFO Queues:
    SQS request queue: CSE546_RequestQueue.fifo
    SQS response queue:CSE546_ResponseQueue.fifo

### Elastic Cloud Application
This Elastic Cloud Application provides an image recognition service, which uses a deep learning model to predict the images provided by users.<br/>
The main purpose of this project is to understand and effectively utilize cloud computing Iaas services (compute, storage and message) to meet the demand with scaling up and down the resources. We have used the most widely used resources from Amazon Web Services(AWS) i.e. Amazon Elastic Compute Cloud (EC2), Amazon Simple Storage (S3) and Amazon Simple Queue Service(SQS).<br/>
#### Web Tier:
Web Tier provides a web interface to access the cloud application i.e. to provide input to the deeplearning model and views the generated results.<br/>
👉 Once, a user uploads images using the web interface, the web tier will upload the image into the Amazon Simple Storage Service (S3) and also sends a message into an input Simple Queue Service (sqs). We have used threads to upload images into the input S3 bucket parallely.<br/>
👉 The web tier waits until any response is generated in the response sqs queue.<br/>
👉 Once, responses are genearted the web tier will retrieve the predicted results for each image and then displays it to the user.<br/>
#### Controller:
👉 The controller reads the number of messages from the input message queue and scales up the number of compute resources based on the demand.<br/>
👉 It runs for every 20 seconds to read if any new requests have been recieved, and also considers the running/pending EC2 instances which have already been instantiated before scaling up the resources.<br/>
#### AppTier: 
App Tier is created from our own AMI which consists of the given classifier code along with the additional code to run the given classifier. <br/>
👉As soon as the instance is created from controller from the given AMI, a cronjob will start which will execute appInstance.py <br/>
👉appInstance.py will basically check for any messages available in SQS request queue.<br/>
👉If any messages are available in SQS request queue, the images will be downloaded from s3 bucket and passed to classifier and the result will be stored in s3 bucket and pushed to SQS response queue and further checks for any avaialble messages in SQS request queue <br/>
👉If no messages are available the instance will be terminated.

##### IAM profile for grading purpose
    URL:https://992611621996.signin.aws.amazon.com/console
    Password: cse546_project1
    Access Key: AKIA6OHCDLRWAEX4V4N4
    Secret Access Key: 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
        
