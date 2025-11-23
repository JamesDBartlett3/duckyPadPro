#!/usr/bin/env python3
"""
Profile Info Manager
Handles SD card detection and profile_info.txt parsing for duckyPad Pro
"""

import platform
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ProfileInfoManager:
    """Manage profile name to index mapping from profile_info.txt"""
    
    def __init__(self, sd_card_path: Optional[Path] = None):
        """Initialize profile info manager
        
        Args:
            sd_card_path: Optional path to SD card (overrides auto-detection)
        """
        self.sd_card_path = sd_card_path
        self.profile_mapping: Dict[str, int] = {}
        self.loaded = False
    
    def detect_sd_card(self) -> Optional[Path]:
        """Auto-detect duckyPad SD card across operating systems
        
        Returns:
            Path to SD card root if found, None otherwise
        """
        # If path was provided, use it
        if self.sd_card_path:
            if self._is_valid_sd_card(self.sd_card_path):
                return self.sd_card_path
            return None
        
        system = platform.system()
        
        if system == "Windows":
            return self._detect_windows()
        elif system == "Darwin":  # macOS
            return self._detect_macos()
        elif system == "Linux":
            return self._detect_linux()
        
        return None
    
    def _is_valid_sd_card(self, path: Path) -> bool:
        """Check if path contains profile_info.txt
        
        Args:
            path: Path to check
            
        Returns:
            True if profile_info.txt exists in path
        """
        if not path.exists() or not path.is_dir():
            return False
        
        profile_info = path / "profile_info.txt"
        return profile_info.exists() and profile_info.is_file()
    
    def _detect_windows(self) -> Optional[Path]:
        """Detect SD card on Windows
        
        Returns:
            Path to SD card if found
        """
        # Check common drive letters
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            drive = Path(f"{letter}:/")
            if self._is_valid_sd_card(drive):
                return drive
        
        return None
    
    def _detect_macos(self) -> Optional[Path]:
        """Detect SD card on macOS
        
        Returns:
            Path to SD card if found
        """
        volumes = Path("/Volumes")
        
        if not volumes.exists():
            return None
        
        # Check all mounted volumes
        for volume in volumes.iterdir():
            if volume.is_dir() and self._is_valid_sd_card(volume):
                return volume
        
        return None
    
    def _detect_linux(self) -> Optional[Path]:
        """Detect SD card on Linux
        
        Returns:
            Path to SD card if found
        """
        # Check /media/* (common for auto-mounted removable media)
        media = Path("/media")
        if media.exists():
            for user_dir in media.iterdir():
                if user_dir.is_dir():
                    for mount in user_dir.iterdir():
                        if mount.is_dir() and self._is_valid_sd_card(mount):
                            return mount
        
        # Check /mnt/* (manual mounts)
        mnt = Path("/mnt")
        if mnt.exists():
            for mount in mnt.iterdir():
                if mount.is_dir() and self._is_valid_sd_card(mount):
                    return mount
        
        return None
    
    def parse_profile_info(self, sd_card_path: Path) -> Dict[str, int]:
        """Parse profile_info.txt and build name to index mapping
        
        Args:
            sd_card_path: Path to SD card root
            
        Returns:
            Dictionary mapping profile names to indices (0-based)
            
        Format example:
            1 Welcome
            2 Firefox
            3 Chrome
            
        Maps to:
            {'Welcome': 0, 'Firefox': 1, 'Chrome': 2}
        """
        profile_info_path = sd_card_path / "profile_info.txt"
        
        if not profile_info_path.exists():
            return {}
        
        mapping = {}
        
        try:
            with open(profile_info_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Parse format: "N ProfileName"
                    parts = line.split(maxsplit=1)
                    
                    if len(parts) != 2:
                        continue
                    
                    try:
                        profile_num = int(parts[0])
                        profile_name = parts[1]
                        
                        # Convert to 0-based index (profile1 = index 0)
                        mapping[profile_name] = profile_num - 1
                    except ValueError:
                        # Skip malformed lines
                        continue
        
        except Exception:
            return {}
        
        return mapping
    
    def load_profile_mapping(self) -> bool:
        """Load profile mapping from SD card
        
        Returns:
            True if mapping loaded successfully, False otherwise
        """
        if self.loaded:
            return True
        
        # Detect SD card
        sd_card = self.detect_sd_card()
        
        if not sd_card:
            return False
        
        # Parse profile_info.txt
        self.profile_mapping = self.parse_profile_info(sd_card)
        self.loaded = len(self.profile_mapping) > 0
        self.sd_card_path = sd_card
        
        return self.loaded
    
    def get_profile_index(self, profile_name: str) -> Optional[int]:
        """Get profile index by name
        
        Args:
            profile_name: Profile name to look up
            
        Returns:
            Profile index (0-based) if found, None otherwise
        """
        return self.profile_mapping.get(profile_name)
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profile names
        
        Returns:
            Sorted list of profile names
        """
        return sorted(self.profile_mapping.keys())
    
    def transform_goto_commands(self, script_content: str) -> Tuple[str, List[str]]:
        """Transform GOTO_PROFILE commands from names to indices
        
        Args:
            script_content: Original script content
            
        Returns:
            Tuple of (transformed content, list of warnings)
        """
        warnings = []
        
        # Pattern to match GOTO_PROFILE ProfileName (non-greedy, stops at newline or end)
        # Matches word characters, hyphens, and spaces but stops at newline
        pattern = r'GOTO_PROFILE\s+([A-Za-z0-9_\-][A-Za-z0-9_\-\s]*?)(?=\s*$|\s*\n)'
        
        def replace_func(match):
            profile_name = match.group(1).strip()
            
            # Check if it's already a number
            if profile_name.isdigit():
                return match.group(0)  # Leave numeric references unchanged
            
            # Look up profile name
            index = self.get_profile_index(profile_name)
            
            if index is not None:
                return f"GOTO_PROFILE {index}"
            else:
                # Profile not found - it's likely a new profile that will be deployed
                # Leave the name as-is; it will be resolved at deployment time
                return match.group(0)  # Leave unchanged
        
        transformed = re.sub(pattern, replace_func, script_content, flags=re.MULTILINE)
        
        return transformed, warnings

