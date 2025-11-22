# deployers

Profile deployment utilities for duckyPad Pro.

## Scripts

### deploy_profiles.py

Deploy profiles to duckyPad SD card with automatic backup and profile_info.txt management.

**Features:**

- Auto-detects duckyPad SD card
- Creates timestamped backup of SD card contents (excludes .dsb bytecode files)
- Deploys profiles with automatic profile numbering
- Updates profile_info.txt with all deployed profiles
- Interactive confirmations (can be bypassed with `--force`)
- Validates profiles before deployment

**Usage:**

```bash
# Deploy single profile
python helpers/deployers/deploy_profiles.py profiles/my-profile

# Deploy multiple profiles
python helpers/deployers/deploy_profiles.py profiles/profile1 profiles/profile2

# Custom backup location
python helpers/deployers/deploy_profiles.py profiles/my-profile -b ~/backups/my-backup

# Verbose mode
python helpers/deployers/deploy_profiles.py profiles/my-profile -v

# Skip confirmations (force)
python helpers/deployers/deploy_profiles.py profiles/my-profile -f
```

**Workflow:**

1. **Detection**: Finds duckyPad SD card automatically
2. **Validation**: Checks profiles have config.txt and key files
3. **Confirmation**: Shows deployment plan and asks for confirmation
4. **Backup**: Creates backup at `~/.duckypad/backups/backup_TIMESTAMP/`
5. **Deploy**: Copies profiles to SD card as `profileN_Name`
6. **Update**: Regenerates profile_info.txt with all profiles

**Profile Numbering:**

- Finds next available profile number on SD card
- Preserves existing profiles
- Example: If SD card has profile1-5, new profiles start at profile6

**Backup Location:**

- Default: `~/.duckypad/backups/backup_YYYYMMDD_HHMMSS/`
- Custom: Use `--backup-path` flag
- Excludes: .dsb bytecode files (can be regenerated with compiler)

**Requirements:**

- SD card must contain profile_info.txt (duckyPad formatted card)
- Source profiles should have:
  - `config.txt` (recommended)
  - At least one `keyN.txt` file (recommended)

**Exit Codes:**

- `0`: Deployment successful
- `1`: Deployment failed or cancelled
