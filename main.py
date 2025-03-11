
"""
url = input("Enter YouTube video URL: ")

Vid = download_youtube_video(url)
if not Vid:
    print("Error: Unable to download the video.")
    exit()
Vid = Vid.replace(".webm", ".mp4")
print(f"Downloaded video successfully: {Vid}")

Audio = extractAudio(Vid)
if not Audio:
    print("Error: No audio file found.")
    exit()

transcriptions = transcribeAudio(Audio)
if not transcriptions:
    print("Error: No transcriptions found.")
    exit()

TransText = ""
for text, start, end in transcriptions:
    TransText += f"{start} - {end}: {text}\n"

print("Extracting highlight timestamps...")
highlight_result = GetHighlight(TransText)

if not highlight_result or isinstance(highlight_result, str):
    print("Error in getting highlight timestamps. Received:", highlight_result)
    exit()

try:
    start, stop = highlight_result
    if start is not None and stop is not None:
        print(f"Start: {start}s, End: {stop}s")
    else:
        raise ValueError("Invalid timestamps returned from GetHighlight")

    Output = "Out.mp4"
    crop_video(Vid, Output, start, stop)

    cropped = "cropped.mp4"
    crop_to_vertical(Output, cropped)

    final_output = "Final.mp4"
    combine_videos(Output, cropped, final_output)

    filtered_transcriptions = [
        [text, t_start - start, t_end - start]
        for text, t_start, t_end in transcriptions
        if t_start >= start and t_end <= stop
    ]
    for i, (text, t_start, t_end) in enumerate(filtered_transcriptions):
        if t_start < 0:
            filtered_transcriptions[i][1] = 0
        if t_end > (stop - start):
            filtered_transcriptions[i][2] = stop - start

    final_with_captions = "Final_with_captions.mp4"
    add_captions_to_video(final_output, filtered_transcriptions, final_with_captions)

    # Cleanup with retry
    files_to_remove = [Vid, Audio, Output, cropped, "DecOut.mp4", final_output]
    for file in files_to_remove:
        for _ in range(3):  # Retry 3 times
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Removed: {file}")
                    break
            except Exception as e:
                print(f"Error removing {file}: {e}")
                import time
                time.sleep(1)  # Wait before retry

    for temp_file in os.listdir():
        if temp_file.startswith("TEMP_MPY") or temp_file.endswith("_snd.mp4"):
            try:
                os.remove(temp_file)
                print(f"Removed temp file: {temp_file}")
            except Exception as e:
                print(f"Error removing {temp_file}: {e}")

    print("Process completed successfully! Add soothing music in YouTube Shorts.")

except ValueError as e:
    print(f"Error processing timestamps: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")   "
    """
import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
import os
from Components.YoutubeDownloader import download_youtube_video
from Components.Edit import extractAudio, crop_video
from Components.Transcription import transcribeAudio
from Components.Speaker import detect_faces_and_speakers
from Components.FaceCrop import crop_to_vertical, combine_videos
from Components.Captions import add_captions_to_video

def main():
    url = input("Enter YouTube video URL: ")
    video_path = download_youtube_video(url)
    audio_path = extractAudio(video_path)
    transcriptions = transcribeAudio(audio_path)
    
    highlight = None
    for i, segment in enumerate(transcriptions):
        if segment[0].strip().endswith('.'):
            duration = segment[2] - segment[1]
            if duration >= 10:
                highlight = segment
                break
            extended_text = segment[0]
            extended_end = segment[2]
            for next_segment in transcriptions[i+1:]:
                extended_text += " " + next_segment[0]
                extended_end = next_segment[2]
                if extended_end - segment[1] >= 10 and next_segment[0].strip().endswith('.'):
                    highlight = [extended_text, segment[1], extended_end]
                    break
            if highlight:
                break
    if not highlight:
        highlight = transcriptions[0]
    
    start, stop = highlight[1], highlight[2]
    print(f"Selected highlight: {highlight[0]} ({start}s - {stop}s)")
    
    cropped_video = "cropped.mp4"
    crop_video(video_path, cropped_video, start, stop)
    detected_video = "detected.mp4"
    detect_faces_and_speakers(cropped_video, detected_video)
    vertical_video = "vertical.mp4"
    crop_to_vertical(detected_video, vertical_video)
    final_no_captions = "final_no_captions.mp4"
    combine_videos(cropped_video, vertical_video, final_no_captions)
    
    # Filter transcriptions for the cropped duration
    filtered_transcriptions = [
        [text, max(0, t_start - start), min(t_end - start, stop - start)]
        for text, t_start, t_end in transcriptions
        if t_start < stop and t_end > start
    ]
    final_video = "final.mp4"
    add_captions_to_video(final_no_captions, filtered_transcriptions, final_video)
    
    # Cleanup
    for file in [audio_path, cropped_video, detected_video, vertical_video, final_no_captions]:
        if os.path.exists(file):
            os.remove(file)
    print(f"Cleanup done, only {final_video} remains.")

if __name__ == "__main__":
    main()