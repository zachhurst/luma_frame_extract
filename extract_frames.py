# Import necessary modules
import os  # This module provides functions to interact with the operating system.
import subprocess  # This module allows you to spawn new processes, connect to their input/output/error pipes, and obtain their return codes.
import json  # This module provides methods for parsing JSON, a common format for storing data.

def list_video_files():
    # Extend the tuple to include a broader range of common video file extensions
    video_extensions = ('.mp4', '.mov', '.avi', 
                        '.mkv', '.flv', '.wmv', 
                        '.mpeg', '.mpg', '.m4v',
                        '.webm', '.vob', '.ogv',
                        '.3gp', '.m2ts', '.ts')
    
    # List all files in the current directory ('.') and filter out the ones that match the video extensions
    files = [f for f in os.listdir('.') if f.lower().endswith(video_extensions)]
    
    # Return the list of video files
    return files

# Define a function to allow the user to select a video file from a list
def select_video_file(files):
    # Loop through each file in the list, enumerating them starting at 1
    for index, file in enumerate(files, 1):
        print(f"{index}: {file}")  # Display the file with its corresponding index

    while True:
        try:
            # Prompt the user to input the number corresponding to their choice of video file
            choice = int(input("Select a video file by number: "))
            
            # Check if the user's choice is within the valid range
            if 1 <= choice <= len(files):
                return files[choice - 1]  # Return the selected file
            else:
                print("Invalid choice, try again.")
        except ValueError:
            print("Invalid input, please enter a number.")

# Define a function to get frame timecodes from a video file
def get_frame_timecodes(video_file):
    # Prepare the command to run `ffprobe` with specific options to get frame information
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'frame=pts_time,pkt_pts_time,pkt_dts_time,coded_picture_number',
        '-of', 'json',
        video_file
    ]
    
    # Run the command and capture the output
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse the JSON output to get frame information
    frames_info = json.loads(result.stdout)
    
    # Create a dictionary to store frame numbers and their corresponding timecodes
    frame_timecodes = {}
    
    # Loop through each frame and extract necessary information
    for frame in frames_info['frames']:
        frame_num = int(frame['coded_picture_number'])  # Get frame number
        timecode = frame.get('pkt_pts_time') or frame.get('pts_time') or frame.get('pkt_dts_time')  # Get the timecode
        
        # Store the frame number and its timecode in the dictionary if timecode is available
        if timecode is not None:
            frame_timecodes[frame_num] = float(timecode)
    
    # Return the dictionary of frame timecodes
    return frame_timecodes

# Define a function to extract the last 4 frames from a video file
def extract_final_frames(video_file):
    # Get the base name of the video file (without extension)
    base_name = os.path.splitext(video_file)[0]
    
    # Create an output directory for the extracted frames
    output_dir = os.path.join(os.getcwd(), base_name)
    os.makedirs(output_dir, exist_ok=True)

    # Prepare the command to get the total number of frames in the video
    cmd = f"ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 \"{video_file}\""
    
    # Run the command and capture the output
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Convert the output to an integer to get the total number of frames
    total_frames = int(result.stdout.strip())

    # Get the timecodes for each frame
    frame_timecodes = get_frame_timecodes(video_file)

    # Determine the frame numbers for the last 4 frames
    start_frame = max(total_frames - 4, 0)  # Ensure start_frame is not less than 0
    frame_numbers = range(start_frame, start_frame + 4)

    # Loop through each frame number to extract the frame
    for i, frame_number in enumerate(frame_numbers):
        timecode = frame_timecodes.get(frame_number, 0.0)  # Get the timecode for the frame (default to 0.0 if not found)
        
        # Format the timecode to a string (hours:minutes:seconds.milliseconds)
        timecode_str = f"{int(timecode // 3600):02}:{int((timecode % 3600) // 60):02}:{int(timecode % 60):02}.{int((timecode * 1000) % 1000):03}"
        
        # Define the output filename for the extracted frame
        output_image = os.path.join(output_dir, f'{base_name}_{i + 1}_{timecode_str}.png')
        
        # Prepare the command to extract the frame using `ffmpeg`
        cmd = f"ffmpeg -i \"{video_file}\" -vf \"select=eq(n\\,{frame_number})\" -vsync vfr \"{output_image}\" -hide_banner -loglevel error -y"
        
        # Run the command to extract the frame
        subprocess.run(cmd, shell=True)

# Define the main function to orchestrate the listing, selection, and extraction of video files
def main():
    # Get the list of video files in the current directory
    files = list_video_files()
    
    # Check if there are no video files found
    if not files:
        print("No video files found in the current directory.")
        return

    # Allow the user to select a video file from the list
    selected_video = select_video_file(files)
    
    # Extract the final frames from the selected video
    extract_final_frames(selected_video)
    
    # Inform the user that the frames have been saved
    print(f"Extracted frames saved in folder: {selected_video}")

# Call the main function only if this script is run directly (not imported as a module)
if __name__ == "__main__":
    main()
