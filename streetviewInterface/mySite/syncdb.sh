#!/bin/bash

rm -rf ImagePicker/migrations
scp -r michaelc@138.197.220.71:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/ImagePicker/migrations ImagePicker/migrations

scp michaelc@138.197.220.71:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/db.sqlite3 db.sqlite3

