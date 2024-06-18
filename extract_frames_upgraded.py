"""
The purpose of this script was to automate frame extraction from Luma Labs, Dream Machine
videos allowing users to extend their Luma generations. Luma added an extend option 
to their application on June 17, 2024 rendering this code obsolete. It may still be
useful for other video generation AIs.

Today I updated it to address a metadata inconsistency with iOS preview cropped video outputs 
which seems to strip metadata for "coded_picture_number". We now use sequential frame indexing 
and frame timing information instead for cross-file compatibility. 

This script extracts the last 4 frames from a selected video file in the current directory.

It lists available video files, allows the user to select one, and saves the extracted frames
in a folder named after the video file's base name. The extracted frame files are named
with the format {video_file_base_name}_{frame_index}_{time_code}.png where time_code 
represents the time position of the frame within the video.

**Requirements:**
- Ensure `ffmpeg` and `ffprobe` are installed and added to your system's PATH.
  You can install them using the following commands:
    - Windows: Download from https://ffmpeg.org/download.html and add to PATH.
    - macOS: `brew install ffmpeg`
    - Linux: Use your package manager, e.g. `apt-get install ffmpeg`.

**How to run the script:**
1. Place the script in the same directory as your video files.
2. Run the script using Python 3: `python extract_frames.py`
3. Follow the prompts to select the video file.
"""

import os  # Provides functions to interact with the operating system
import subprocess  # Allows the script to call external programs like ffmpeg and ffprobe
import json  # Provides methods for parsing JSON data

def list_video_files():
    # List of video file extensions to be considered
    video_extensions = ('.mp4', '.mov', '.avi', 
                        '.mkv', '.flv', '.wmv', 
                        '.mpeg', '.mpg', '.m4v',
                        '.webm', '.vob', '.ogv',
                        '.3gp', '.m2ts', '.ts')
    
    # List all files in the current directory that have one of the video extensions
    files = [f for f in os.listdir('.') if f.lower().endswith(video_extensions)]
    
    # Return the list of video files
    return files

def select_video_file(files):
    # Print an enumerated list of video files
    for index, file in enumerate(files, 1):
        print(f"{index}: {file}")

    while True:
        try:
            # Prompt user to select a video file by number
            choice = int(input("Select a video file by number: "))
            
            # If the choice is valid, return the corresponding file
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("Invalid choice, try again.")
        except ValueError:
            print("Invalid input, please enter a number.")

def get_frame_timecodes(video_file):
    # Command to run ffprobe and get frame timecodes
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'frame=pts_time,pkt_pts_time,pkt_dts_time',
        '-of', 'json',
        video_file
    ]
    
    # Run the command and capture the output
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse the JSON output from ffprobe
    frames_info = json.loads(result.stdout)
    
    # Dictionary to store frame timecodes
    frame_timecodes = {}

    # Loop through each frame info and extract timecode
    for idx, frame in enumerate(frames_info.get('frames', [])):
        # Debug print to display frame info
        print(f"Frame {idx}: {frame}")
        
        # Extract timecode from available fields
        timecode = frame.get('pkt_pts_time') or frame.get('pts_time') or frame.get('pkt_dts_time')
        
        if timecode is not None:
            frame_timecodes[idx] = float(timecode)

    return frame_timecodes

def extract_final_frames(video_file):
    # Get the base name of the file without extension
    base_name = os.path.splitext(video_file)[0]
    
    # Create a directory to save the frames
    output_dir = os.path.join(os.getcwd(), base_name)
    os.makedirs(output_dir, exist_ok=True)

    # Command to get the number of frames in the video
    cmd = f"ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 \"{video_file}\""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    try:
        # Get the total number of frames by converting the output to an integer
        total_frames = int(result.stdout.strip())
    except ValueError:
        print("Error: Couldn't determine the number of frames in the video file.")
        return

    if total_frames == 0:
        print("Error: No frames detected in the video file.")
        return

    # Get the timecodes for each frame from the video file
    frame_timecodes = get_frame_timecodes(video_file)
    
    # Determine the starting frame for the last 4 frames
    start_frame = max(total_frames - 4, 0)
    frame_numbers = range(start_frame, start_frame + 4)

    # Loop through the frame numbers and extract each frame
    for i, frame_number in enumerate(frame_numbers):
        timecode = frame_timecodes.get(frame_number, 0.0)
        
        # Format the timecode into a string
        timecode_str = f"{int(timecode // 3600):02}:{int((timecode % 3600) // 60):02}:{int(timecode % 60):02}.{int((timecode * 1000) % 1000):03}"
        
        # Define the output filename for the extracted frame
        output_image = os.path.join(output_dir, f'{base_name}_{i + 1}_{timecode_str}.png')
        
        # Command to extract the frame using ffmpeg
        cmd = f"ffmpeg -i \"{video_file}\" -vf \"select=eq(n\\,{frame_number})\" -vsync vfr \"{output_image}\" -hide_banner -loglevel error -y"
        
        # Run the command to extract the frame
        subprocess.run(cmd, shell=True)

def main():
    # List all available video files in the current directory
    files = list_video_files()
    
    # If no video files are found, print a message and exit
    if not files:
        print("No video files found in the current directory.")
        return
    
    # Prompt the user to select a video file
    selected_video = select_video_file(files)
    
    # Extract the final frames from the selected video
    extract_final_frames(selected_video)
    
    # Print the location where frames were saved
    print(f"Extracted frames saved in folder: {selected_video}")

if __name__ == "__main__":
    main()
