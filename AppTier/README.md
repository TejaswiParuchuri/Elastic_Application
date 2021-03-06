chmod +x test.sh <br/>
chmod 777 stdout.txt <br/>
pip3 install boto3 <br/>
pip3 install schedule <br/>
sudo apt-get install xvfb <br/>
mkdir .aws <br/>
add files config and credentials <br/>
sudo crontab -u ubuntu -e <br/>
@reboot /home/ubuntu/test.sh <br/>

