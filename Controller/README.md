We followed the below steps to create a new Linux EC2 instance for the Controller job, create all the necessary files present this folder and run the code:

1. Create a new Controller EC2 instance (running), with the appropriate Ubuntu AMI image, security group and key-pair for the project
2. Should have a ppk file for logging into the instance through SSH client
3. Login to the Controller using Putty, by giving the SSH Client URL and the correct ppk file and then, create a directory called controller_cse546. 
4. Change the directory to /home/ubuntu/controller_cse546.
5. Create a requirements file for all the necessary libraries.
6. Install pip and all the required libraries using the commands below: 
    sudo apt-update
    sudo apt-upgrade
    sudo apt install python3-pip
    pip3 --version
    python3 -m pip install -r requirements
7. create a file called controller.py, for the main program 
8. Run  the program using the command python3 controller.py to perform the Controller job, every 10 seconds
