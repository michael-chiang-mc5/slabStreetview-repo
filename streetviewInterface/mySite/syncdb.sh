#!/bin/bash

rm -rf ImagePicker/migrations
scp -r michaelc@104.131.145.75:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/ImagePicker/migrations ImagePicker/migrations


scp michaelc@104.131.145.75:/home/michaelc/dev/slabStreetview-repo/streetviewInterface/mySite/db.sqlite.8-1-2017_1af8a3f74e3c720ef044a956cf35fa78cb0e3236 db.sqlite3
