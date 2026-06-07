"""Platform/capability assessment for Wira Local onboarding.

The product can run on more machines than the fully private local-model lane can.
This module keeps those truths separate so the GUI can recommend the right brain
path without pretending every machine has equal local-AI support.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import platform


@dataclass(frozen=True)
class PlatformAssessment:
    system: str
    machine: str
    ram_gb: int
    platform_label: str
    support_tier: str
    local_ai_tier: str
    recommended_brain_summary: str
    local_option_blurb: str
    welcome_blurb: str
    local_setup_blurb: str
    download_label: str



def system_ram_gb() -> int:
    """Best-effort total physical RAM in GB on macOS, Windows, and Linux.

    Returns 0 only when the platform genuinely can't be probed; callers treat 0
    as "unknown", not "small". The previous implementation used ``os.sysconf``,
    which does not exist on Windows, so every Windows machine silently reported
    0 GB and got downgraded to the limited local-AI tier.
    """
    # macOS / Linux / other Unix.
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        phys_pages = os.sysconf("SC_PHYS_PAGES")
        if page_size > 0 and phys_pages > 0:
            return int((page_size * phys_pages) / (1024 ** 3))
    except (AttributeError, ValueError, OSError):
        pass

    # Windows: query the kernel directly via GlobalMemoryStatusEx.
    try:
        import ctypes

        class _MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        if getattr(ctypes, "windll", None) is not None:
            stat = _MemoryStatusEx()
            stat.dwLength = ctypes.sizeof(_MemoryStatusEx)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                return int(stat.ullTotalPhys / (1024 ** 3))
    except Exception:
        pass

    return 0


# Private alias kept for backward compatibility with earlier imports.
_system_ram_gb = system_ram_gb


def assess(*, machine: str | None = None, system: str | None = None, ram_gb: int | None = None) -> PlatformAssessment:
    sys_name = (system or platform.system() or "").strip() or "Unknown"
    machine_name = (machine or platform.machine() or "").strip() or "unknown"
    ram = system_ram_gb() if ram_gb is None else max(ram_gb, 0)

    sys_lower = sys_name.lower()
    machine_lower = machine_name.lower()

    if sys_lower == "darwin":
        if machine_lower in {"arm64", "aarch64"}:
            return PlatformAssessment(
                system=sys_name,
                machine=machine_name,
                ram_gb=ram,
                platform_label="Apple Silicon Mac",
                support_tier="full",
                local_ai_tier="recommended",
                recommended_brain_summary="Start free or connect ChatGPT now, or keep everything private on this Mac.",
                local_option_blurb="This is Wira's best local-private path. Ollama is a strong fit here if you want the brain to stay private on this Mac.",
                welcome_blurb="This Apple Silicon Mac can use the fast cloud lane, ChatGPT, or the full private local-AI lane.",
                local_setup_blurb="Wira is preparing a private AI model on this Mac. This happens once.",
                download_label="Download for Mac",
            )
        return PlatformAssessment(
            system=sys_name,
            machine=machine_name,
            ram_gb=ram,
            platform_label="Intel Mac",
            support_tier="supported",
            local_ai_tier="limited",
            recommended_brain_summary="Start with the cloud or ChatGPT lane for the smoothest setup on this Intel Mac.",
            local_option_blurb="Private local AI can still be tried here, but it is not the default recommendation unless you know this Mac is strong enough.",
            welcome_blurb="This Intel Mac is supported for the fast cloud lane and ChatGPT. Local AI is optional and more machine-dependent.",
            local_setup_blurb="Wira is preparing a private AI model on this Intel Mac. This can be slower than the cloud or ChatGPT path.",
            download_label="Download for Mac",
        )

    if sys_lower == "windows":
        local_tier = "recommended" if ram >= 16 else "limited"
        local_blurb = (
            "This Windows machine is strong enough to try private local AI if you want it."
            if local_tier == "recommended"
            else "Private local AI is optional on Windows and usually best on stronger machines. Start free or connect ChatGPT first."
        )
        return PlatformAssessment(
            system=sys_name,
            machine=machine_name,
            ram_gb=ram,
            platform_label="Windows PC",
            support_tier="supported",
            local_ai_tier=local_tier,
            recommended_brain_summary="Start free or connect ChatGPT for the fastest setup on this Windows PC.",
            local_option_blurb=local_blurb,
            welcome_blurb="This Windows PC is supported for the fast cloud lane and ChatGPT. Private local AI depends more on the machine.",
            local_setup_blurb="Wira is preparing a private AI model on this Windows PC. This may take a while depending on the machine.",
            download_label="Download for Windows",
        )

    return PlatformAssessment(
        system=sys_name,
        machine=machine_name,
        ram_gb=ram,
        platform_label=f"{sys_name} computer",
        support_tier="limited",
        local_ai_tier="unsupported",
        recommended_brain_summary="Use one of Wira's best-supported Mac or Windows setups for the smoothest path, or start with a cloud brain if you're experimenting here.",
        local_option_blurb="This platform is not yet a first-class local setup for Wira.",
        welcome_blurb="Wira's best-supported setup is currently on Mac and Windows machines.",
        local_setup_blurb="This platform is not yet a first-class local-AI setup for Wira.",
        download_label="Download Wira",
    )
