set -e

BOOK_TITLE=$1;
LANGUAGE=$2;

NO_ASK="";

if [[ $3 == "-y" ]]
then
  NO_ASK="-y"
fi;


echo "Processing video"
PYTHONPATH=./ python ./scripts/process.py -t "${BOOK_TITLE}" -l "${LANGUAGE}" $NO_ASK

echo "Creating image wallpaper"
python ./scripts/resize_image.py -t "${BOOK_TITLE}" -l "${LANGUAGE}" -s wallpaper

echo "Converting to video"
./scripts/convert_to_video.sh "${BOOK_TITLE}" "${LANGUAGE}"

echo "Uploading to S3"
./scripts/upload.sh "${BOOK_TITLE}" "${LANGUAGE}"

echo "Done!";