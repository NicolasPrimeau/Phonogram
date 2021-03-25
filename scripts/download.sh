set -e;
BASE_PATH="./data";
S3_BUCKET=phonogram.nostalgica;
BOOK_TITLE=$1;
LANGUAGE=$2;

BOOK_PATH=${BASE_PATH}/${BOOK_TITLE}/${LANGUAGE};
S3_PATH=s3://${S3_BUCKET}/${BOOK_TITLE}/${LANGUAGE};

aws s3 cp --recursive "${S3_PATH}" "${BOOK_PATH}"
