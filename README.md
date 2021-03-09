### Elastic Cloud Application

This Elastic Cloud Application provides an image recognition service, which uses a deep learning model to predict the images provided by users.<br/><br/>
The main purpose of this project is to understand and effectively utilize cloud computing Iaas services (compute, storage and message) to meet the demand with scaling up and down the resources. We have used the most widely used resources from Amazon Web Services(AWS) i.e. Amazon Elastic Compute Cloud (EC2), Amazon Simple Storage (S3) and Amazon Simple Queue Service(SQS).<br/><br/>

#### Web Tier:
Web Tier provides a web interface to access the cloud application i.e. to provide input to the deeplearning model and views the generated results.<br/>
👉 Once, a user uploads images using the web interface, the web tier will upload the image into the Amazon Simple Storage Service (S3) and also sends a message into an input Simple Queue Service (sqs).<br/>
👉 The web tier waits until any response is generated in the response sqs queue.<br/>
👉 Once, responses are genearted the web tier will retrieve the predicted results for each image and then displays it to the user.<br/><br/>
#### Controller:


#### AppTier: 
App Tier is created from our own AMI which consists of the given classifier code along with the additional code to run the given classifier. <br/>
👉As soon as the instance is created from controller from the given AMI, a cronjob will start which will execute the test.sh shell script which in turn will execute startup.py <br/>
👉startup.py will basically check for any messages available in SQS request queue.<br/>
👉If any messages are available in SQS request queue, the images will be downloaded from s3 bucket and passed to classifier and the result will be stored in s3 bucket and pushed to SQS response queue and further checks for any avaialble messages in SQS request queue <br/>
👉If no messages are available the instance will be terminated.
        
