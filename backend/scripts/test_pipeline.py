"""
Test script for Day 1-2: Basic detection and tracking pipeline.

This script tests the core pipeline on a sample video or webcam.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pipeline import process_video_simple


def test_sample_video():
    """Test pipeline on a sample video."""
    print("="*60)
    print("SENTINELAI - Day 1-2 Pipeline Test")
    print("="*60)

    # Paths
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / "data"

    # Check for sample video
    sample_video = data_dir / "sample_videos" / "test.mp4"

    if not sample_video.exists():
        print(f"\n⚠️  Sample video not found: {sample_video}")
        print("\nPlease add a test video to data/sample_videos/test.mp4")
        print("\nYou can download sample videos from:")
        print("  - MOT17: https://motchallenge.net/data/MOT17/")
        print("  - Pexels: https://www.pexels.com/search/videos/people%20walking/")
        print("\nOr record your own using:")
        print("  python scripts/record_webcam.py")
        return

    # Output paths
    output_video = data_dir / "processed" / "test_output.mp4"
    events_json = data_dir / "events" / "test_events.json"

    # Ensure directories exist
    output_video.parent.mkdir(parents=True, exist_ok=True)
    events_json.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nInput: {sample_video}")
    print(f"Output Video: {output_video}")
    print(f"Events JSON: {events_json}")
    print()

    # Run pipeline
    try:
        results = process_video_simple(
            str(sample_video),
            str(output_video),
            str(events_json),
        )

        print("\n✅ Pipeline test completed successfully!")
        print(f"\nWatch output video: {output_video}")
        print(f"View events: {events_json}")

        # Print some events
        events = results["events"]
        if events:
            print(f"\nSample Events (first 5):")
            for event in events[:5]:
                print(f"  Frame {event['frame_number']}: "
                      f"Track {event['track_id']} - {event['action']}")

    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()


def test_webcam():
    """Test pipeline on webcam (future feature)."""
    print("Webcam testing not yet implemented (Week 2)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test SentinelAI pipeline")
    parser.add_argument(
        "--mode",
        choices=["video", "webcam"],
        default="video",
        help="Test mode",
    )

    args = parser.parse_args()

    if args.mode == "video":
        test_sample_video()
    else:
        test_webcam()
