import boto3
import datetime
client = boto3.client('ec2')

response = client.describe_spot_instance_requests()

open_requests = 0
for request in response['SpotInstanceRequests']:
    state = request['State']
    if state == 'open':
        open_requests += 1

if open_requests == 0:

    #if asdfadsfs: # check to see if there is already a g2 instancce running

    print("no open requests, opening new request")
    response = client.request_spot_instances(
        InstanceCount=1,
        SpotPrice='0.21',
        Type='one-time',
        LaunchSpecification={
            'ImageId': 'ami-289fb148',
            'KeyName': 'devenv-key',
            'SecurityGroups': ['sg-77a15511'],
            'InstanceType': 'g2.2xlarge',
            'Placement': {
                'AvailabilityZone': 'us-west-1a',
            },
            "UserData": "IyEvYmluL2Jhc2gKY2QgL2hvbWUvdWJ1bnR1L0NUUE5fR1BVLwpweXRob24gbWMvdGV4dERldGVjdG9yLnB5",
            'EbsOptimized': True,
            'SecurityGroupIds': [
                'sg-77a15511',
            ],
            'SecurityGroups': [
                'devenv-sg',
            ],
        }
    )
else:
    print("open request exists, doing nothing")
