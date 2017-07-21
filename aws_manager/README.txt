Might need to configure awscli to run on new machine

See http://docs.aws.amazon.com/cli/latest/userguide/installing.html
    http://docs.aws.amazon.com/cli/latest/userguide/tutorial-ec2-ubuntu.html

1) Install cli:
    pip install awscli
2) Configure cli
    aws configure
3) Create security keys
   aws ec2 create-security-group --group-name devenv-sg --description "security group for development environment in EC2"
   aws ec2 authorize-security-group-ingress --group-name devenv-sg --protocol tcp --port 22 --cidr 0.0.0.0/0
   aws ec2 create-key-pair --key-name devenv-key --query 'KeyMaterial' --output text > devenv-key.pem
   chmod 400 devenv-key.pem
   # security group id = "sg-77a15511"

4) Run instance
   # ubuntu 14.04 = ami-89f3dee9
   aws ec2 run-instances --image-id ami-89f3dee9 --security-group-ids sg-77a15511 --count 1 --instance-type t2.micro --key-name devenv-key --query 'Instances[0].InstanceId'
   # i-065951693ef723fae

5) Retrieve IP. Replace XXX with id returned in (4)
  aws ec2 describe-instances --instance-ids XXX --query 'Reservations[0].Instances[0].PublicIpAddress'

6) SSH to instance. XXX is IP returned in (5)
   ssh -i devenv-key.pem ubuntu@XXX


#######
# Spot instances for CTPN
# http://docs.aws.amazon.com/cli/latest/reference/ec2/request-spot-instances.html
######

1) Requesting spot instance
    aws ec2 request-spot-instances --spot-price 0.21 --instance-count 1 --type "one-time" --launch-specification file://specification.json

    Note: "UserData" runs:
      #!/bin/bash
      cd /home/ubuntu/CTPN_GPU/
      python mc/textDetector.py


      sudo shutdown -h now
#####
#
######

Notes:
Can detect whether working from slabJonathan google api

TODO
- create request with cheap instance https://serverfault.com/questions/592423/how-do-i-launch-an-amazon-ec2-spot-instance-with-userdata
- run sh script like in user data:
    #!/bin/bash
    curl https://maps.googleapis.com/maps/api/streetview?size=400x400'&'location=40.720032,-73.988354'&'fov=90'&'heading=235'&'pitch=10'&'key=AIzaSyBcJe8KOEyhDKa1YM3H8XBofeChujcfo28
    sudo shutdown -h now
- check to see whether google api registered command
- backup db
- modify 104... to send CTPN metadata one by one, with pending
- modify CTPN to take in metadata one at a time
- create and run spot request. should be able to ssh in to debug
- create script to continuously monitor shutdown and renew request if necessary

Using launch wizard:
http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/launching-instance.html#launch-instance-console

1) Start-up script
    send api call to google streetview
    shut down
2) spot instance
    - use user data

http://docs.aws.amazon.com/cli/latest/reference/ec2/request-spot-instances.html

https://serverfault.com/questions/592423/how-do-i-launch-an-amazon-ec2-spot-instance-with-userdata
https://stackoverflow.com/questions/25204262/passing-a-shell-script-as-user-data-in-amazon-aws-ec2-request-spot-instances

####

    aws ec2 run-instances --image-id ami-abcd1234 --count 1 --instance-type m3.medium \
    --key-name my-key-pair --subnet-id subnet-abcd1234 --security-group-ids sg-abcd1234 \
    --user-data file://my_script.txt
