#!/bin/bash

rm -rf ImagePicker/migrations
scp -r michaelc@104.131.145.75:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/ImagePicker/migrations ImagePicker/migrations


scp michaelc@104.131.145.75:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/db.sqlite.7-28-17_918936e4feb37d453c548ff8bbd095bd89a33d0b db.sqlite3
