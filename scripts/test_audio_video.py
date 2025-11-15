#!/usr/bin/env python3
"""
Audio/Video Hardware Test Script.

Tests conference speakerphones and webcams for BigBlueButton readiness.

Usage:
    python scripts/test_audio_video.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrator.audio_manager import AudioVideoManager
from src.utils.logger import setup_logger


logger = setup_logger("test_audio_video", level="INFO")


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


def test_audio_devices():
    """Test audio device detection and configuration."""
    print_header("🎤 Audio Device Test")

    with AudioVideoManager() as manager:
        # Check PulseAudio availability
        if not manager.pulse:
            print("❌ PulseAudio not available")
            print("   Install with: sudo apt install pulseaudio pulseaudio-utils")
            return False

        print("✅ PulseAudio is available\n")

        # List audio sources (microphones)
        print("Audio Input Devices (Microphones):")
        print("-" * 70)
        sources = manager.get_audio_sources()

        if not sources:
            print("  ⚠️  No audio input devices found")
        else:
            for source in sources:
                default_marker = " [DEFAULT]" if source.is_default else ""
                print(f"  {'✓' if source.is_default else ' '} {source.description}{default_marker}")

        print()

        # List audio sinks (speakers)
        print("Audio Output Devices (Speakers):")
        print("-" * 70)
        sinks = manager.get_audio_sinks()

        if not sinks:
            print("  ⚠️  No audio output devices found")
        else:
            for sink in sinks:
                default_marker = " [DEFAULT]" if sink.is_default else ""
                print(f"  {'✓' if sink.is_default else ' '} {sink.description}{default_marker}")

        print()

        # Test auto-configuration
        print("Testing automatic device configuration...")
        if manager.configure_audio():
            print("✅ Audio configuration successful")

            # Show new defaults
            info = manager.get_system_info()
            print(f"\nConfigured defaults:")
            print(f"  Input:  {info['default_source']}")
            print(f"  Output: {info['default_sink']}")
        else:
            print("⚠️  Audio configuration failed or no changes needed")

        return len(sources) > 0 and len(sinks) > 0


def test_video_devices():
    """Test video device detection."""
    print_header("📹 Video Device Test")

    with AudioVideoManager() as manager:
        # List video devices
        video_devices = manager.get_video_devices()

        if not video_devices:
            print("⚠️  No webcams found")
            print("   Troubleshooting:")
            print("   - Is your webcam connected?")
            print("   - Try: ls -l /dev/video*")
            print("   - Install v4l2-utils: sudo apt install v4l2-utils")
            return False

        print(f"Found {len(video_devices)} webcam(s):\n")

        for i, device in enumerate(video_devices, 1):
            print(f"  {i}. {device.name}")
            print(f"     Device: {device.device_path}")

        print("\n✅ Video devices detected successfully")
        return True


def test_preferred_devices():
    """Test if preferred conference speakerphones are detected."""
    print_header("🔍 Preferred Device Detection")

    preferred_devices = [
        "Jabra Speak 510",
        "Anker PowerConf",
        "eMeet M2",
        "Logitech",
    ]

    with AudioVideoManager(preferred_devices=preferred_devices) as manager:
        if not manager.pulse:
            print("⚠️  PulseAudio not available")
            return False

        sources = manager.get_audio_sources()
        sinks = manager.get_audio_sinks()

        print("Checking for preferred conference speakerphones...\n")

        found_devices = []
        for preferred in preferred_devices:
            # Check sources
            for source in sources:
                if preferred.lower() in source.description.lower():
                    print(f"  ✅ Found: {source.description} (input)")
                    found_devices.append(source.description)
                    break

            # Check sinks
            for sink in sinks:
                if preferred.lower() in sink.description.lower():
                    if sink.description not in found_devices:
                        print(f"  ✅ Found: {sink.description} (output)")
                        found_devices.append(sink.description)
                    break

        if not found_devices:
            print("  ℹ️  No preferred conference devices found")
            print("     Currently using default system audio devices")
            print("\nSupported speakerphones:")
            for device in preferred_devices:
                print(f"     - {device}")
        else:
            print(f"\n✅ Detected {len(found_devices)} preferred device(s)")

        return len(found_devices) > 0


def show_system_info():
    """Show complete system information."""
    print_header("📊 System Information")

    with AudioVideoManager() as manager:
        info = manager.get_system_info()

        # PulseAudio status
        pa_status = "✅ Available" if info["pulseaudio_available"] else "❌ Not Available"
        print(f"PulseAudio: {pa_status}")

        # Default devices
        if info["default_source"]:
            print(f"Default Input: {info['default_source']}")
        else:
            print("Default Input: Not set")

        if info["default_sink"]:
            print(f"Default Output: {info['default_sink']}")
        else:
            print("Default Output: Not set")

        # Device counts
        print(f"\nDevice Count:")
        print(f"  Audio Inputs:  {len(info['audio_sources'])}")
        print(f"  Audio Outputs: {len(info['audio_sinks'])}")
        print(f"  Webcams:       {len(info['video_devices'])}")


def run_all_tests():
    """Run all hardware tests."""
    print("\n" + "=" * 70)
    print("🧪 RaspberryMeet Audio/Video Hardware Test")
    print("=" * 70)

    results = {
        "audio": False,
        "video": False,
        "preferred": False,
    }

    # Run tests
    try:
        results["audio"] = test_audio_devices()
        results["video"] = test_video_devices()
        results["preferred"] = test_preferred_devices()
        show_system_info()

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1

    # Summary
    print_header("📋 Test Summary")

    all_passed = all(results.values())

    print(f"Audio Devices:      {'✅ PASS' if results['audio'] else '❌ FAIL'}")
    print(f"Video Devices:      {'✅ PASS' if results['video'] else '❌ FAIL'}")
    print(f"Preferred Devices:  {'✅ FOUND' if results['preferred'] else 'ℹ️  NOT FOUND'}")

    print()

    if all_passed:
        print("✅ All hardware tests PASSED!")
        print("\nYour system is ready for BigBlueButton meetings.")
        print("\nNext steps:")
        print("  1. Run demo_gpio_meeting.py to test the full setup")
        print("  2. Configure autostart: sudo ./scripts/install_services.sh")
    else:
        print("⚠️  Some tests failed")
        print("\nTroubleshooting:")

        if not results["audio"]:
            print("  Audio Issues:")
            print("    - Install PulseAudio: sudo apt install pulseaudio")
            print("    - Run audio setup: ./scripts/setup_audio.sh")

        if not results["video"]:
            print("  Video Issues:")
            print("    - Check webcam connection")
            print("    - Install v4l2-utils: sudo apt install v4l2-utils")

        if not results["preferred"]:
            print("  Conference Speakerphone:")
            print("    - Connect USB speakerphone")
            print("    - For Bluetooth: run ./scripts/pair_bluetooth.sh")

    print("\n" + "=" * 70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(run_all_tests())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
