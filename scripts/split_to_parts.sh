mediainfo
ffmpeg -i ./video.mp4 -acodec copy -vcodec copy -t 9:00:0  video.part-0.mp4
ffmpeg -i ./video.mp4 -acodec copy -vcodec copy -ss 9:00:0  video.part-1.mp4