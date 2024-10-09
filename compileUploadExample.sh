python ./tools/compiler.py --input ./src/cryptomus-scam.txt --output ./build/cryptomus-scam.txt
if [ $? -eq 0 ]; then
    echo Compile OK
else
    echo Compile FAIL
    exit 1
fi
python ./tools/uploader.py --post ./build/cryptomus-scam.txt --blog ./private/wordpress
