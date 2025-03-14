from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def apply_zoom_effect(clip, start_time, end_time, zoom_factor=1.2):
    duration = end_time - start_time
    zoom_in = clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / (duration / 2)) if t < duration / 2 else zoom_factor - (zoom_factor - 1) * ((t - duration / 2) / (duration / 2)))
    return zoom_in.set_start(start_time).set_duration(duration)

def add_captions_to_video(video_path, transcription_data, output_path):
    video = VideoFileClip(video_path)
    caption_clips = []
    effect_clips = []
    
    # Captions (simple, synced)
    for text, start, end in transcription_data:
        if not text.strip():  # Skip empty text
            continue
        duration = end - start
        if duration <= 0:  # Skip invalid durations
            continue
        txt_clip = TextClip(
            text, 
            fontsize=24, 
            color='white', 
            bg_color='transparent',
            method='caption', 
            size=(video.w * 0.8, None), 
            align='center'
        )
        txt_start = max(0, start)
        txt_end = min(end, video.duration)
        txt_clip = txt_clip.set_start(txt_start).set_duration(txt_end - txt_start).set_position(('center', 0.75), relative=True)
        caption_clips.append(txt_clip)
        print(f"Added caption: '{text}' from {txt_start}s to {txt_end}s")
    
    # Zoom In/Out (every 10s, optional)
    zoom_duration = 2.0
    for t in range(0, int(video.duration), 10):
        end_time = min(t + zoom_duration, video.duration)
        zoom_clip = apply_zoom_effect(video, t, end_time, zoom_factor=1.2)
        effect_clips.append(zoom_clip)
    
    # Combine
    final_video = CompositeVideoClip([video] + effect_clips + caption_clips)
    final_video.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac', 
        preset='ultrafast', 
        threads=4
    )
    print(f"Captions and zoom added: {output_path}")

    # Combine
    final_video = CompositeVideoClip([video] + effect_clips + caption_clips)
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4)
    print(f"Captions and zoom added: {output_path}")
    
    # Cleanup
    video.close()
    for clip in effect_clips + caption_clips:
        clip.close()
    final_video.close()