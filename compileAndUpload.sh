#!/bin/bash
source ~/.bash_profile

# Check if the argument is provided
if [ -z "$1" ]; then
    echo "Error: No filename provided."
    echo "Usage: ./compileAndUpload.sh <filename_without_extension>"
    exit 1
fi

filename=$1
python3 ./tools/compiler.py --input ./src/"$filename".txt --output ./build/"$filename".txt
if [ $? -eq 0 ]; then
    echo "Compile OK"
else
    echo "Compile FAIL"
    exit 1
fi

python3.10 ./tools/uploader.py --post ./build/"$filename".txt --blog ./private/wordpress
