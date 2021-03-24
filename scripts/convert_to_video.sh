BASE_PATH="./data";
BOOK_TITLE=$1;
LANGUAGE=$2;

BOOK_PATH=${BASE_PATH}/${BOOK_TITLE}/${LANGUAGE};
IMAGE_PATH=${BOOK_PATH}/wallpaper.png;
AUDIO_PATH=${BOOK_PATH}/audio.mp3;
VIDEO_PATH=${BOOK_PATH}/video.mp4;

ffmpeg -loop 1 \
-i "${IMAGE_PATH}" \
-i "${AUDIO_PATH}" \
-c:v libx264 \
-tune stillimage \
-c:a aac \
-b:a 192k \
-pix_fmt yuv420p \
-shortest "${VIDEO_PATH}"
