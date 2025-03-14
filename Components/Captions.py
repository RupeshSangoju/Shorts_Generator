
"""
def add_captions_to_video estatal_path, transcription_data, output_path, font_size=15, font_color='white'):
    try:
        video = VideoFileClip(video_path)
        print(f"Video loaded: {video_path}, Size: {video.w}x{video.h}, Duration: {video.duration}s")
        font = 'DejaVu-Sans'
        caption_clips = []
        effect_clips = []

        full_width = int(video.w * 0.9)  # 90% width, 5% padding each side
        print(f"Full caption width: {full_width}px (90% of {video.w})")

        for i, (text, start, end) in enumerate(transcription_data):
            text = text.strip()
            if not text:
                continue
            
            # No background, full width, smaller font
            txt_clip = TextClip(text, fontsize=font_size, color=font_color, font=font, method='label', transparent=True)
            if txt_clip.w > full_width:
                txt_clip = TextClip(text, fontsize=font_size, color=font_color, font=font, size=(full_width, None), method='caption', transparent=True, align='center')
                print(f"Caption wrapped: '{text}' | Width: {txt_clip.w}/{full_width} | Height: {txt_clip.h}")
            else:
                print(f"Caption single-line: '{text}' | Width: {txt_clip.w}/{full_width} | Height: {txt_clip.h}")

            y_pos = int(video.h * 0.8)  # 80% (20% from bottom)
            txt_clip = txt_clip.set_duration(end - start).set_start(start).set_position(('center', y_pos))
            print(f"Caption {i} placed at y={y_pos}, Start: {start}s, End: {end}s")
            caption_clips.append(txt_clip)

            if i % 2 == 0 or start % 5 < 0.1:
                flare = add_light_flare(video, start)
                effect_clips.append(flare)
                print(f"Added flare at {start}s")

            zoomed_segment = apply_zoom_effect(video.subclip(start, end), start, end)
            effect_clips.append(zoomed_segment)
            print(f"Added zoom from {start}s to {end}s")

        print(f"Combining {len(caption_clips)} captions and {len(effect_clips)} effects")
        final_video = CompositeVideoClip([video] + effect_clips + caption_clips)
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
            remove_temp=True
        )
        
        video.close()
        for clip in caption_clips + effect_clips:
            clip.close()
        final_video.close()
        print(f"Captions added successfully. Video saved as: {output_path}")
    except Exception as e:
        print(f"Error adding captions: {str(e)}")
        raise
"""
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def apply_zoom_effect(clip, start_time, end_time, zoom_factor=1.2):
    duration = end_time - start_time
    zoom_in = clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / (duration / 2)) if t < duration / 2 else zoom_factor - (zoom_factor - 1) * ((t - duration / 2) / (duration / 2)))
    return zoom_in.set_start(start_time).set_duration(duration)
"""
def add_captions_to_video(video_path, transcription_data, output_path):
    video = VideoFileClip(video_path)
    caption_clips = []
    effect_clips = []
    
    # Captions (simple, synced)
    for text, start, end in transcription_data:
        txt_clip = TextClip(text, fontsize=24, color='white', bg_color='transparent',
                           method='caption', size=(video.w * 0.8, None), align='center')

        txt_start = start - transcription_data[0][1]  # Offset by highlight start
        txt_end = end - transcription_data[0][1]
        if txt_start < 0: txt_start = 0
        if txt_end > video.duration: txt_end = video.duration
        txt_clip = txt_clip.set_start(txt_start).set_end(txt_end).set_position(('center', 0.75), relative=True)
        caption_clips.append(txt_clip)
    
    # Zoom In/Out (every 10s)
    zoom_duration = 2.0
    for t in range(0, int(video.duration), 10):
        end_time = min(t + zoom_duration, video.duration)
        zoom_clip = apply_zoom_effect(video, t, end_time, zoom_factor=1.2)
        effect_clips.append(zoom_clip)
    """
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