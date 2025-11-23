#!/usr/bin/env python3
"""
duckyPad Device Controller
Mount/unmount SD card, detect connected duckyPad devices
"""
import argparse
import contextlib
import io
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add vendor directory to path
sys.path.insert(0, str(Path(__file__).parent / "vendor"))

try:
    import hid  # type: ignore
    from hid_common import scan_duckypads, get_empty_pc_to_duckypad_buf  # type: ignore
    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False

# HID command constant for software reset
HID_COMMAND_SW_RESET = 20


def duckypad_hid_sw_reset(dp_dict: Dict[str, Any], reboot_into_usb_msc_mode: bool = False) -> bool:
    """Send software reset command to duckyPad device
    
    Args:
        dp_dict: Device info dictionary from scan_duckypads()
        reboot_into_usb_msc_mode: True to mount SD card, False to unmount
        
    Returns:
        True if reset command was sent successfully
    """
    if not HID_AVAILABLE:
        return False
        
    try:
        # Scan again because HID path might have changed
        dp_list = scan_duckypads()
        if dp_list is None or len(dp_list) == 0:
            return False
            
        # Find device with matching serial
        dp_to_reset_hid_path = []
        for this_dp in dp_list:
            if this_dp["serial"] == dp_dict["serial"]:
                dp_to_reset_hid_path.append(this_dp["hid_path"])
                
        if len(dp_to_reset_hid_path) == 0:
            return False
            
        # Build HID command buffer
        pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
        pc_to_duckypad_buf[2] = HID_COMMAND_SW_RESET  # Command type
        if reboot_into_usb_msc_mode:
            pc_to_duckypad_buf[3] = 1
            
        # Send reset command
        myh = hid.device()
        myh.open_path(dp_to_reset_hid_path[0])
        myh.write(pc_to_duckypad_buf)
        myh.close()
        
        return True
        
    except Exception:
        return False


class Colors:
    """ANSI color codes"""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def print_color(message: str, color: str):
    """Print colored message"""
    print(f"{color}{message}{Colors.RESET}")


class DuckyPadDevice:
    """Control duckyPad Pro device via HID"""
    
    def __init__(self, verbose: bool = False):
        """Initialize device controller
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        
        if not HID_AVAILABLE:
            if verbose:
                print_color("Warning: HID library not available. Device control disabled.", Colors.YELLOW)
    
    def scan_devices(self) -> Optional[List[Dict[str, Any]]]:
        """Scan for connected duckyPad devices
        
        Returns:
            List of device info dicts, or None if error
        """
        if not HID_AVAILABLE:
            if self.verbose:
                print_color("HID not available", Colors.YELLOW)
            return None
        
        try:
            devices = scan_duckypads()
            if self.verbose and devices:
                print_color(f"Found {len(devices)} duckyPad device(s):", Colors.GREEN)
                for device in devices:
                    print_color(f"  Serial: {device['serial']}, FW: {device['fw_version']}", Colors.CYAN)
            return devices
        except Exception as e:
            if self.verbose:
                print_color(f"Error scanning devices: {e}", Colors.RED)
            return None
    
    def mount_sd_card(self, device_dict: Optional[Dict[str, Any]] = None) -> bool:
        """Mount SD card by rebooting duckyPad into USB mass storage mode
        
        Args:
            device_dict: Specific device to mount (default: first found device)
            
        Returns:
            True if successful, False otherwise
        """
        if not HID_AVAILABLE:
            if self.verbose:
                print_color("HID not available - cannot mount SD card", Colors.RED)
            return False
        
        try:
            # If no device specified, scan for devices
            if device_dict is None:
                devices = self.scan_devices()
                if not devices or len(devices) == 0:
                    if self.verbose:
                        print_color("No duckyPad devices found", Colors.RED)
                    return False
                device_dict = devices[0]
                if self.verbose:
                    print_color(f"Using device: {device_dict['serial']}", Colors.CYAN)
            
            if self.verbose:
                print_color("Mounting SD card...", Colors.CYAN)
            
            # Reboot into USB mass storage mode (mounts SD card)
            # Suppress vendor debug output
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                duckypad_hid_sw_reset(device_dict, reboot_into_usb_msc_mode=True)
            
            if self.verbose:
                print_color("✓ SD card mount command sent", Colors.GREEN)
                print_color("  Wait a few seconds for SD card to appear", Colors.YELLOW)
            
            return True
            
        except Exception as e:
            if self.verbose:
                print_color(f"Error mounting SD card: {e}", Colors.RED)
            return False
    
    def unmount_sd_card(self, device_dict: Optional[Dict[str, Any]] = None) -> bool:
        """Unmount SD card by rebooting duckyPad into normal mode
        
        Args:
            device_dict: Specific device to unmount (default: first found device)
            
        Returns:
            True if successful, False otherwise
        """
        if not HID_AVAILABLE:
            if self.verbose:
                print_color("HID not available - cannot unmount SD card", Colors.RED)
            return False
        
        try:
            # If no device specified, scan for devices
            if device_dict is None:
                devices = self.scan_devices()
                if not devices or len(devices) == 0:
                    if self.verbose:
                        print_color("No duckyPad devices found", Colors.RED)
                    return False
                device_dict = devices[0]
                if self.verbose:
                    print_color(f"Using device: {device_dict['serial']}", Colors.CYAN)
            
            if self.verbose:
                print_color("Unmounting SD card...", Colors.CYAN)
            
            # Reboot into normal mode (unmounts SD card)
            # Suppress vendor debug output
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                duckypad_hid_sw_reset(device_dict, reboot_into_usb_msc_mode=False)
            
            if self.verbose:
                print_color("✓ SD card unmount command sent", Colors.GREEN)
                print_color("  duckyPad is rebooting into normal mode", Colors.YELLOW)
            
            return True
            
        except Exception as e:
            if self.verbose:
                print_color(f"Error unmounting SD card: {e}", Colors.RED)
            return False


def mount(verbose: bool = False) -> bool:
    """Mount SD card (programmatic interface)
    
    Args:
        verbose: Enable verbose output
        
    Returns:
        True if successful, False otherwise
    """
    controller = DuckyPadDevice(verbose=verbose)
    return controller.mount_sd_card()


def unmount(verbose: bool = False) -> bool:
    """Unmount SD card (programmatic interface)
    
    Args:
        verbose: Enable verbose output
        
    Returns:
        True if successful, False otherwise
    """
    controller = DuckyPadDevice(verbose=verbose)
    return controller.unmount_sd_card()


def scan(verbose: bool = True) -> Optional[List[Dict[str, Any]]]:
    """Scan for connected devices (programmatic interface)
    
    Args:
        verbose: Enable verbose output
        
    Returns:
        List of device info dicts, or None if error
    """
    controller = DuckyPadDevice(verbose=verbose)
    return controller.scan_devices()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Control duckyPad Pro device (mount/unmount SD card)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # 'scan' command
    scan_parser = subparsers.add_parser("scan", help="Scan for connected duckyPad devices")
    scan_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    # 'mount' command
    mount_parser = subparsers.add_parser("mount", help="Mount SD card (reboot into USB mode)")
    mount_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    # 'unmount' command
    unmount_parser = subparsers.add_parser("unmount", help="Unmount SD card (reboot into normal mode)")
    unmount_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    controller = DuckyPadDevice(verbose=args.verbose)
    
    if args.command == "scan":
        devices = controller.scan_devices()
        if not devices:
            print_color("No duckyPad devices found", Colors.YELLOW)
            return 1
        return 0
    
    elif args.command == "mount":
        if controller.mount_sd_card():
            return 0
        else:
            return 1
    
    elif args.command == "unmount":
        if controller.unmount_sd_card():
            return 0
        else:
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


