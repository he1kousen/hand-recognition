"""
Audio control module — wrap pycaw untuk kontrol volume sistem Windows.
"""

from pycaw.pycaw import AudioUtilities


def get_volume_interface():
    """Dapatkan interface volume sistem."""
    speakers = AudioUtilities.GetSpeakers()
    return speakers.EndpointVolume


def set_volume_scalar(scalar: float):
    """Set volume sistem (0.0 - 1.0)."""
    vol = get_volume_interface()
    scalar = max(0.0, min(1.0, scalar))
    vol.SetMasterVolumeLevelScalar(scalar, None)


def get_current_volume() -> float:
    """Ambil volume sistem saat ini (0.0 - 1.0) → return sebagai persen 0-100."""
    vol = get_volume_interface()
    return vol.GetMasterVolumeLevelScalar() * 100


def set_mute(muted: bool):
    """Mute atau unmute volume sistem."""
    vol = get_volume_interface()
    vol.SetMute(muted, None)
