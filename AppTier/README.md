We need to create a new Linux EC2 instance for the AppTier controller using DeepLearning AMI, create all the necessary files present in this folder and then run the following commands:

chmod 777 classification_result.txt <br/>
pip3 install boto3 <br/>
pip3 install schedule <br/>
mkdir .aws <br/>
add files config and credentials <br/>
sudo crontab -u ubuntu -e <br/>
@reboot sleep(30); python3 /home/ubuntu/appInstance.py <br/>

