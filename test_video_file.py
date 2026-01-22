"""
Test Video File - Diagnostic script to check if a video can be read properly
"""

import sys
import cv2
from pathlib import Path

def test_video(video_path: str):
    """Test if a video file can be opened and read."""
    path = Path(video_path)

    print("=" * 60)
    print("VIDEO FILE DIAGNOSTIC TEST")
    print("=" * 60)
    print(f"\nVideo path: {path}")
    print(f"File exists: {path.exists()}")

    if not path.exists():
        print("\n❌ ERROR: File does not exist!")
        return False

    print(f"File size: {path.stat().st_size / (1024*1024):.2f} MB")
    print(f"File extension: {path.suffix}")

    # Try to open with OpenCV
    print("\n" + "-" * 60)
    print("Opening video with OpenCV...")
    cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        print("\n❌ ERROR: OpenCV cannot open this video file!")
        print("\nPossible reasons:")
        print("1. Unsupported codec (try converting to H.264 MP4)")
        print("2. Corrupted video file")
        print("3. Missing codec on system")
        return False

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

    # Decode fourcc
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

    print(f"\n✅ Video opened successfully!")
    print(f"\nVideo Properties:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Total frames: {total_frames}")
    print(f"  Duration: {total_frames/fps:.2f} seconds")
    print(f"  Codec: {codec}")

    # Try reading first 10 frames
    print("\n" + "-" * 60)
    print("Testing frame reading (first 10 frames)...")

    successful_reads = 0
    failed_reads = 0

    for i in range(10):
        ret, frame = cap.read()

        if not ret or frame is None:
            print(f"  Frame {i}: ❌ FAILED to read")
            failed_reads += 1
        else:
            print(f"  Frame {i}: ✅ OK (shape: {frame.shape})")
            successful_reads += 1

    cap.release()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Successful reads: {successful_reads}/10")
    print(f"Failed reads: {failed_reads}/10")

    if failed_reads > 0:
        print("\n⚠️  WARNING: Some frames could not be read!")
        print("This video may have issues. Try:")
        print("1. Re-encoding with ffmpeg:")
        print(f"   ffmpeg -i {path.name} -c:v libx264 -preset fast output.mp4")
        print("2. Using a different video file")
        return False
    else:
        print("\n✅ Video file is OK and should work with SentinelAI!")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_video_file.py <path_to_video>")
        print("\nExample:")
        print("  python test_video_file.py data/uploads/test.mp4")
        sys.exit(1)

    video_path = sys.argv[1]
    success = test_video(video_path)

    sys.exit(0 if success else 1)
