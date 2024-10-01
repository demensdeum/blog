python ./tools/compiler.py --input ./src/robot-defenders.txt --output ./build/robot-defenders.txt
if [ $? -eq 0 ]; then
    echo Compile OK
else
    echo Compile FAIL
    exit 1
fi
python ./tools/uploader.py --post ./build/robot-defenders.txt --blog ./private/wordpress