python ./tools/compiler.py --input ./src/bgfx-emscripten.txt --output ./build/bgfx-emscripten.txt
if [ $? -eq 0 ]; then
    echo Compile OK
else
    echo Compile FAIL
    exit 1
fi
python ./tools/uploader.py --post ./build/bgfx-emscripten.txt --blog ./private/wordpress