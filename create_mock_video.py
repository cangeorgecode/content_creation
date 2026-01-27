from moviepy import ColorClip
import os

def create_mock():
    os.makedirs("media", exist_ok=True)
    
    # Create a simple red video (No Text to avoid ImageMagick requirement)
    # Just a solid color is enough for testing
    video = ColorClip(size=(1080, 1920), color=(150, 50, 50), duration=10)
    
    # Let's add silent audio
    from moviepy import AudioClip
    def make_frame(t): return [0, 0]
    audio = AudioClip(make_frame, duration=10, fps=44100)
    video = video.with_audio(audio)
    
    output = "media/mock_avatar.mp4"
    video.write_videofile(output, fps=24)
    print(f"Created {output} (Simple Color Version)")

if __name__ == "__main__":
    create_mock()
