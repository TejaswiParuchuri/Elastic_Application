We need to create a new Linux EC2 instance for the Controller job, create all the necessary files present this folder and then follow the steps below:

1. Create a new Controller instance (running), with the appropriate Ubuntu AMI image, security group and key-pair for the project
2. Should have a ppk file for logging into the instance through SSH client
3. Log in to the instance through SSH and create a directory called controller_cse546
4. Create a requirements file for all the necessary libraries
5. Install pip: 
    sudo apt-update
    sudo apt-upgrade
    sudo apt install python3-pip
    pip3 --version
    python3 -m pip install -r requirements
6. create a file called startup.py, for the initial code
7. create a file called create_server.py for the utility code
8. Run startup.py to perform the Controller job, every 20 seconds
