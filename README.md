# slabStreetview-repo

# use this to automatically launch CTPN aws spot requests
*/10 * * * * echo 'source /home/michaelc/dev/slabStreetview-repo/aws_manager/venv/bin/activate; cd /home/michaelc/dev/slabStreetview-repo/aws_manager/; python spot_instance_request_launcher.py' | /bin/bash

ssh michaelc@104.131.145.75
