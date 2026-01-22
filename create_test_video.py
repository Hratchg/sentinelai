"""
Create a simple test video that's guaranteed to work with SentinelAI
"""

import cv2
import numpy as np
from pathlib import Path

def create_test_video():
    """Create a 10-second test video with moving rectangles (simulating people)"""

    output_path = Path("test_video.mp4")

    # Video properties
    width, height = 1280, 720
    fps = 30
    duration_sec = 10
    total_frames = fps * duration_sec

    # Create video writer with H.264 codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, float(fps), (width, height))

    if not out.isOpened():
        print("❌ Failed to create video writer")
        return False

    print(f"Creating test video: {width}x{height} @ {fps} FPS, {duration_sec} seconds...")

    # Generate frames with moving rectangles (simulating people)
    for frame_num in range(total_frames):
        # Create blank frame (gray background)
        frame = np.ones((height, width, 3), dtype=np.uint8) * 128

        # Add some "people" (rectangles) moving across screen
        person1_x = int((frame_num / total_frames) * width)
        person1_y = height // 2
        cv2.rectangle(frame,
                     (person1_x, person1_y - 100),
                     (person1_x + 60, person1_y + 100),
                     (0, 255, 0), -1)  # Green rectangle

        person2_x = width - int((frame_num / total_frames) * width)
        person2_y = height // 3
        cv2.rectangle(frame,
                     (person2_x, person2_y - 80),
                     (person2_x + 50, person2_y + 120),
                     (255, 0, 0), -1)  # Blue rectangle

        # Add frame number text
        cv2.putText(frame, f"Frame {frame_num}/{total_frames}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Write frame
        out.write(frame)

        if frame_num % 30 == 0:
            print(f"  Progress: {frame_num}/{total_frames} frames ({frame_num/total_frames*100:.0f}%)")

    out.release()

    print(f"\n✅ Test video created successfully: {output_path}")
    print(f"   File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"\nYou can now upload this video to test SentinelAI!")
    print(f"Upload it at: http://localhost:5173")

    return True


if __name__ == "__main__":
    create_test_video()
