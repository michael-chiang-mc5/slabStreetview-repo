import boto3
import datetime
client = boto3.client('ec2')

response = client.describe_spot_instance_requests()

open_or_active_request = 0
for request in response['SpotInstanceRequests']:
    state = request['State']
    print(state)
    if state == 'open' or state == "active":
        open_or_active_request += 1

if open_or_active_request == 0:


    print("no open/active requests, opening new request")
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
    print("open/active requests exist, doing nothing")
