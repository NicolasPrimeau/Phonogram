set -e

BOOK_TITLE=$1;
LANGUAGE=$2;

echo "Processing video";
PYTHONPATH=./ python ./scripts/process.py -t "${BOOK_TITLE}" -l "${LANGUAGE}";

echo "Creating image thumbnail";
python ./scripts/resize_image.py -t "${BOOK_TITLE}" -l "${LANGUAGE}" -s thumbnail;

echo "Creating image wallpaper";
python ./scripts/resize_image.py -t "${BOOK_TITLE}" -l "${LANGUAGE}" -s wallpaper;

echo "Converting to video";
./scripts/convert_to_video.sh "${BOOK_TITLE}" "${LANGUAGE}";

echo "Done!";