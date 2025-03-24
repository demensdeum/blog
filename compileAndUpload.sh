#!/bin/bash
source ~/.bash_profile

# Initialize variable
only_upload=false

# Parse arguments
for arg in "$@"; do
    if [ "$arg" == "--only-upload" ]; then
        only_upload=true
    elif [ -z "$filename" ]; then
        filename="$arg"
    fi
done

# Check if the filename argument is provided
if [ -z "$filename" ]; then
    echo "Error: No filename provided."
    echo "Usage: ./compileAndUpload.sh <filename_without_extension> [--only-upload]"
    exit 1
fi

# Compile step (skip if --only-upload is specified)
if [ "$only_upload" = false ]; then
    python3 ./tools/compiler.py --input ./src/"$filename".txt --output ./build/"$filename".txt
    if [ $? -eq 0 ]; then
        echo "Compile OK"
    else
        echo "Compile FAIL"
        exit 1
    fi
else
    echo "Skipping compilation step"
fi

# Upload step
python3 ./tools/uploader.py --post ./build/"$filename".txt --blog ./private/wordpress
