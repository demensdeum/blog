source ~/.bash_profile
if [ -z "$1" ]; then
    echo "Error: No filename provided."
    echo "Usage: ./script_name.sh <filename>"
    exit 1
fi

filename=$1

python3 ./tools/mediaUploader.py --media ./media/"$filename" --blog ./private/wordpress
