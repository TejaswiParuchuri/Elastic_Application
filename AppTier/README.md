We need to create a new Linux EC2 instance for the AppTier controller using DeepLearning AMI, create all the necessary files present in this folder and then run the following commands:

chmod +x test.sh <br/>
chmod 777 stdout.txt <br/>
pip3 install boto3 <br/>
pip3 install schedule <br/>
sudo apt-get install xvfb <br/>
mkdir .aws <br/>
add files config and credentials <br/>
sudo crontab -u ubuntu -e <br/>
@reboot /home/ubuntu/test.sh <br/>

