#!/usr/bin/env python3
"""
SentinelAI Setup Validation Script
Checks that all dependencies and components are working correctly.
"""

import sys
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text):
    """Print a section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def check_pass(message):
    """Print a passing check."""
    print(f"{GREEN}✓{RESET} {message}")


def check_fail(message, error=None):
    """Print a failing check."""
    print(f"{RED}✗{RESET} {message}")
    if error:
        print(f"  {RED}Error: {error}{RESET}")


def check_warn(message):
    """Print a warning."""
    print(f"{YELLOW}⚠{RESET} {message}")


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        check_pass(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        check_fail(f"Python version: {version.major}.{version.minor}.{version.micro} (need 3.9+)")
        return False


def check_imports():
    """Check that all required packages can be imported."""
    print_header("Checking Python Dependencies")

    packages = [
        ("torch", "PyTorch"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("ultralytics", "Ultralytics (YOLO)"),
        ("boxmot", "BoxMOT (tracking)"),
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("tqdm", "tqdm"),
    ]

    all_passed = True
    for package, name in packages:
        try:
            __import__(package)
            check_pass(f"{name} installed")
        except ImportError as e:
            check_fail(f"{name} not found", str(e))
            all_passed = False

    return all_passed


def check_cuda():
    """Check CUDA availability."""
    print_header("Checking GPU Support")

    try:
        import torch

        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            check_pass(f"CUDA available: {device_name}")
            return True
        else:
            check_warn("CUDA not available (will use CPU)")
            return False
    except Exception as e:
        check_fail("Error checking CUDA", str(e))
        return False


def check_project_structure():
    """Check that project directories exist."""
    print_header("Checking Project Structure")

    base_dir = Path(__file__).parent
    required_dirs = [
        "backend",
        "backend/core",
        "backend/utils",
        "backend/scripts",
        "data/uploads",
        "data/processed",
        "data/events",
        "data/sample_videos",
    ]

    all_passed = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            check_pass(f"Directory: {dir_path}")
        else:
            check_fail(f"Directory missing: {dir_path}")
            all_passed = False

    return all_passed


def check_core_modules():
    """Check that core modules can be imported."""
    print_header("Checking Core Modules")

    sys.path.insert(0, str(Path(__file__).parent / "backend"))

    modules = [
        ("core.detector", "YOLOv8Detector"),
        ("core.tracker", "ByteTracker"),
        ("core.actions", "ActionClassifier"),
        ("core.events", "EventLogger"),
        ("core.video_io", "VideoReader"),
        ("core.pipeline", "VideoPipeline"),
        ("utils.performance", "PerformanceMonitor"),
        ("utils.visualization", "draw_annotations"),
    ]

    all_passed = True
    for module, name in modules:
        try:
            __import__(module)
            check_pass(f"{name} module")
        except Exception as e:
            check_fail(f"{name} module", str(e))
            all_passed = False

    return all_passed


def check_yolo_model():
    """Check if YOLO model can be loaded."""
    print_header("Checking YOLO Model")

    try:
        from ultralytics import YOLO

        print("  Downloading/loading YOLOv8n model...")
        model = YOLO("yolov8n.pt")
        check_pass("YOLOv8n model loaded successfully")
        return True
    except Exception as e:
        check_fail("Failed to load YOLO model", str(e))
        return False


def check_sample_video():
    """Check if sample video exists."""
    print_header("Checking Test Data")

    base_dir = Path(__file__).parent
    sample_video = base_dir / "data" / "sample_videos" / "test.mp4"

    if sample_video.exists():
        check_pass(f"Sample video found: {sample_video}")
        return True
    else:
        check_warn("Sample video not found")
        print(f"  {YELLOW}Please add a test video to: {sample_video}{RESET}")
        print(f"  {YELLOW}Download from: https://www.pexels.com/search/videos/people%20walking/{RESET}")
        return False


def run_quick_test():
    """Run a quick pipeline test."""
    print_header("Running Quick Pipeline Test")

    try:
        sys.path.insert(0, str(Path(__file__).parent / "backend"))

        from core.detector import YOLOv8Detector
        from core.tracker import ByteTracker
        from core.actions import ActionClassifier
        import numpy as np

        # Create components
        print("  Creating detector...")
        detector = YOLOv8Detector()

        print("  Creating tracker...")
        tracker = ByteTracker()

        print("  Creating action classifier...")
        classifier = ActionClassifier()

        # Test with dummy frame
        print("  Testing with dummy frame...")
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        detections = detector.detect(dummy_frame)
        tracks = tracker.update(detections, 0)

        check_pass("Pipeline components initialized successfully")
        return True

    except Exception as e:
        check_fail("Pipeline test failed", str(e))
        return False


def print_summary(results):
    """Print validation summary."""
    print_header("Validation Summary")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"Total checks: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")

    if failed == 0:
        print(f"\n{GREEN}🎉 All checks passed! You're ready to start.{RESET}")
        print(f"\n{BLUE}Next steps:{RESET}")
        print("  1. Add a test video to data/sample_videos/test.mp4")
        print("  2. Run: python backend/scripts/test_pipeline.py")
        print("  3. Check output: data/processed/test_output.mp4")
    else:
        print(f"\n{RED}❌ Some checks failed. Please fix the issues above.{RESET}")

    return failed == 0


def main():
    """Run all validation checks."""
    print(f"{BLUE}")
    print("  ____             _   _            _    _    ___  ")
    print(" / ___|  ___ _ __ | |_(_)_ __   ___| |  / \\  |_ _| ")
    print(" \\___ \\ / _ \\ '_ \\| __| | '_ \\ / _ \\ | / _ \\  | |  ")
    print("  ___) |  __/ | | | |_| | | | |  __/ |/ ___ \\ | |  ")
    print(" |____/ \\___|_| |_|\\__|_|_| |_|\\___|_/_/   \\_\\___|")
    print(f"{RESET}")
    print(f"{BLUE}Setup Validation{RESET}\n")

    results = {}

    # Run checks
    results["python_version"] = check_python_version()
    results["imports"] = check_imports()
    results["cuda"] = check_cuda()
    results["structure"] = check_project_structure()
    results["modules"] = check_core_modules()
    results["yolo"] = check_yolo_model()
    results["sample_video"] = check_sample_video()
    results["pipeline"] = run_quick_test()

    # Print summary
    success = print_summary(results)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
