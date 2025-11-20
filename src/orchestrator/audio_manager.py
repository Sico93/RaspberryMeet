"""
Audio and video device management for RaspberryMeet.

Handles automatic detection and configuration of conference speakerphones
and webcams for optimal BigBlueButton experience.
"""
import subprocess
from pathlib import Path
from typing import List, Optional, Dict

try:
    import pulsectl
    PULSECTL_AVAILABLE = True
except ImportError:
    PULSECTL_AVAILABLE = False
    print("pulsectl not available - audio management disabled")

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class AudioDevice:
    """Represents an audio input/output device."""

    def __init__(self, name: str, description: str, index: int, is_default: bool = False):
        self.name = name
        self.description = description
        self.index = index
        self.is_default = is_default

    def __repr__(self):
        default_marker = " [DEFAULT]" if self.is_default else ""
        return f"AudioDevice({self.description}{default_marker})"


class VideoDevice:
    """Represents a video capture device."""

    def __init__(self, device_path: str, name: str):
        self.device_path = device_path
        self.name = name

    def __repr__(self):
        return f"VideoDevice({self.device_path}: {self.name})"


class AudioVideoManager:
    """
    Manages audio and video device detection and configuration.

    Automatically detects conference speakerphones and webcams,
    and configures them as default devices for BigBlueButton meetings.
    """

    def __init__(self, preferred_devices: Optional[List[str]] = None):
        """
        Initialize audio/video manager.

        Args:
            preferred_devices: List of preferred device names (in priority order)
        """
        self.preferred_devices = preferred_devices or [
            "Jabra Speak 510",
            "Anker PowerConf",
            "eMeet M2",
            "HDMI Audio",
        ]

        self.pulse: Optional[pulsectl.Pulse] = None
        if PULSECTL_AVAILABLE:
            try:
                self.pulse = pulsectl.Pulse("raspberrymeet")
                logger.info("PulseAudio connection established")
            except Exception as e:
                logger.warning(f"Failed to connect to PulseAudio: {e}")
                self.pulse = None
        else:
            logger.warning("pulsectl not available - audio management disabled")

    def get_audio_sources(self) -> List[AudioDevice]:
        """
        Get all available audio input devices (sources).

        Returns:
            List of AudioDevice objects for input devices
        """
        if not self.pulse:
            logger.warning("PulseAudio not available")
            return []

        try:
            sources = []
            server_info = self.pulse.server_info()
            default_source = server_info.default_source_name

            for source in self.pulse.source_list():
                # Skip monitor sources (they're outputs, not real inputs)
                if ".monitor" in source.name:
                    continue

                is_default = (source.name == default_source)
                device = AudioDevice(
                    name=source.name,
                    description=source.description,
                    index=source.index,
                    is_default=is_default,
                )
                sources.append(device)

            logger.debug(f"Found {len(sources)} audio input devices")
            return sources

        except Exception as e:
            logger.error(f"Error getting audio sources: {e}")
            return []

    def get_audio_sinks(self) -> List[AudioDevice]:
        """
        Get all available audio output devices (sinks).

        Returns:
            List of AudioDevice objects for output devices
        """
        if not self.pulse:
            logger.warning("PulseAudio not available")
            return []

        try:
            sinks = []
            server_info = self.pulse.server_info()
            default_sink = server_info.default_sink_name

            for sink in self.pulse.sink_list():
                is_default = (sink.name == default_sink)
                device = AudioDevice(
                    name=sink.name,
                    description=sink.description,
                    index=sink.index,
                    is_default=is_default,
                )
                sinks.append(device)

            logger.debug(f"Found {len(sinks)} audio output devices")
            return sinks

        except Exception as e:
            logger.error(f"Error getting audio sinks: {e}")
            return []

    def find_best_audio_device(self, devices: List[AudioDevice]) -> Optional[AudioDevice]:
        """
        Find the best audio device based on preferences.

        Args:
            devices: List of available devices

        Returns:
            Best matching device or None
        """
        if not devices:
            return None

        # Try to find preferred device
        for preferred in self.preferred_devices:
            for device in devices:
                if preferred.lower() in device.description.lower():
                    logger.info(f"Found preferred device: {device.description}")
                    return device

        # Fallback: return first non-default device, or default if it's the only one
        non_defaults = [d for d in devices if not d.is_default]
        if non_defaults:
            logger.info(f"Using first available device: {non_defaults[0].description}")
            return non_defaults[0]

        logger.info(f"Using default device: {devices[0].description}")
        return devices[0]

    def set_default_source(self, device: AudioDevice) -> bool:
        """
        Set default audio input device.

        Args:
            device: AudioDevice to set as default

        Returns:
            True if successful, False otherwise
        """
        if not self.pulse:
            logger.error("PulseAudio not available")
            return False

        try:
            self.pulse.default_set(device.name)
            logger.info(f"Set default audio input: {device.description}")
            return True

        except Exception as e:
            logger.error(f"Failed to set default source: {e}")
            return False

    def set_default_sink(self, device: AudioDevice) -> bool:
        """
        Set default audio output device.

        Args:
            device: AudioDevice to set as default

        Returns:
            True if successful, False otherwise
        """
        if not self.pulse:
            logger.error("PulseAudio not available")
            return False

        try:
            self.pulse.default_set(device.name)
            logger.info(f"Set default audio output: {device.description}")
            return True

        except Exception as e:
            logger.error(f"Failed to set default sink: {e}")
            return False

    def configure_audio(self) -> bool:
        """
        Automatically configure audio devices.

        Finds and sets the best available conference speakerphone
        as default input and output device.

        Returns:
            True if successfully configured, False otherwise
        """
        logger.info("Configuring audio devices...")

        # Get available devices
        sources = self.get_audio_sources()
        sinks = self.get_audio_sinks()

        if not sources or not sinks:
            logger.warning("No audio devices found")
            return False

        # Find best devices
        best_source = self.find_best_audio_device(sources)
        best_sink = self.find_best_audio_device(sinks)

        # Set as defaults
        success = True
        if best_source and not best_source.is_default:
            success &= self.set_default_source(best_source)

        if best_sink and not best_sink.is_default:
            success &= self.set_default_sink(best_sink)

        if success:
            logger.info("Audio configuration complete")
        else:
            logger.warning("Audio configuration partially failed")

        return success

    def get_video_devices(self) -> List[VideoDevice]:
        """
        Get all available video capture devices (webcams).

        Uses v4l2 to enumerate /dev/video* devices.

        Returns:
            List of VideoDevice objects
        """
        devices = []

        # Find all /dev/video* devices
        video_paths = sorted(Path("/dev").glob("video*"))

        for path in video_paths:
            # Try to get device name using v4l2-ctl
            try:
                result = subprocess.run(
                    ["v4l2-ctl", "--device", str(path), "--info"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )

                if result.returncode == 0:
                    # Parse device name from output
                    for line in result.stdout.split("\n"):
                        if "Card type" in line:
                            name = line.split(":")[-1].strip()
                            device = VideoDevice(str(path), name)
                            devices.append(device)
                            break
                    else:
                        # Fallback name
                        device = VideoDevice(str(path), f"Camera {path.name}")
                        devices.append(device)

            except (subprocess.TimeoutExpired, FileNotFoundError):
                # v4l2-ctl not available or timeout - use basic info
                device = VideoDevice(str(path), f"Camera {path.name}")
                devices.append(device)

            except Exception as e:
                logger.debug(f"Error reading video device {path}: {e}")

        logger.info(f"Found {len(devices)} video devices")
        return devices

    def get_system_info(self) -> Dict[str, any]:
        """
        Get audio/video system information.

        Returns:
            Dictionary with system information
        """
        info = {
            "pulseaudio_available": self.pulse is not None,
            "audio_sources": [],
            "audio_sinks": [],
            "video_devices": [],
            "default_source": None,
            "default_sink": None,
        }

        # Audio info
        if self.pulse:
            sources = self.get_audio_sources()
            sinks = self.get_audio_sinks()

            info["audio_sources"] = [
                {"name": s.name, "description": s.description, "is_default": s.is_default}
                for s in sources
            ]
            info["audio_sinks"] = [
                {"name": s.name, "description": s.description, "is_default": s.is_default}
                for s in sinks
            ]

            # Find defaults
            for source in sources:
                if source.is_default:
                    info["default_source"] = source.description
                    break

            for sink in sinks:
                if sink.is_default:
                    info["default_sink"] = sink.description
                    break

        # Video info
        video_devices = self.get_video_devices()
        info["video_devices"] = [
            {"path": v.device_path, "name": v.name}
            for v in video_devices
        ]

        return info

    def cleanup(self):
        """Clean up PulseAudio connection."""
        if self.pulse:
            try:
                self.pulse.close()
                logger.debug("PulseAudio connection closed")
            except Exception as e:
                logger.debug(f"Error closing PulseAudio: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
