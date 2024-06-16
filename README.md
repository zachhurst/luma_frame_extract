# luma_frame_extract
Py script to extract final 4 frames from video file

This is python program that helps extract the last four frames from a Luma Labs - Dream Machine video file. Services are popping up to charge users for this. It's useful for extending videos in Dream Machine (likely Sora, Kling, etc. too). 

It first lists all video files in the current directory, then asks the user to choose a video file by number. Once a file is chosen, the program uses a tool called FFmpeg to extract the last four frames of the video and saves them as images in a new folder. The images are named with the original file name, a frame number, and a timestamp. The program also prints a message to let the user know where the extracted frames are saved. 

You'll need ffmpeg if you don't already have it (pip install ffmpeg-python).
