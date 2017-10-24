#!/bin/bash

rm -rf ImagePicker/migrations
scp -r michaelc@104.131.145.75:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/ImagePicker/migrations ImagePicker/migrations


scp michaelc@104.131.145.75:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/db.sqlite3 db.sqlite3

