#!/bin/bash
aws ec2 request-spot-instances --spot-price 0.21 --instance-count 1 --type "one-time" --launch-specification file://specification.json
