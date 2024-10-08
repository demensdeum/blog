python ./tools/compiler.py --input ./src/cryptoBBS.txt --output ./build/cryptoBBS.txt
if [ $? -eq 0 ]; then
    echo Compile OK
else
    echo Compile FAIL
    exit 1
fi
python ./tools/uploader.py --post ./build/cryptoBBS.txt --blog ./private/wordpress
