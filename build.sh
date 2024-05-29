rm -rf ./build
mkdir ./build
./tools/wordpressFormatter.py src/CRUD/CRUD.txt build/CRUD.txt
./tools/wordpressFormatter.py src/CRUD/CRUD.txt build/CRUD.en.txt --translate-to-english
