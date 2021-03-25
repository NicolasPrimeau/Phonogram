set -e;
BASE_PATH="./data";
S3_BUCKET=phonogram.nostalgica;
BOOK_TITLE=$1;
LANGUAGE=$2;

BOOK_PATH=${BASE_PATH}/${BOOK_TITLE}/${LANGUAGE};
S3_PATH=s3://${S3_BUCKET}/${BOOK_TITLE}/${LANGUAGE};

aws s3 cp --recursive --exclude "audio.mp3" --exclude "video.mp4" "${BOOK_PATH}" "${S3_PATH}"
