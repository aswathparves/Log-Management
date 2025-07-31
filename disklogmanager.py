#!/usr/bin/env/python3
import os
import shutil
import subprocess
import time
import yaml
import argparse
from datetime import datetime

#----------------------------------
# Load Config
#----------------------------------
def load_config(config_path="config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
    

#--------------------------------------------
# Logging helper
#--------------------------------------------

def log_message(message, log_file):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    entry = f"{timestamp} {message}"
    print(entry)
    with open(log_file, "a") as f:
        f.write(entry + "\n")
        
#----------------------------------------------
# Check Disk Usage
#----------------------------------------------
def get_disk_usage_percent(path):
    usage = shutil.disk_usage(path)
    percent = (usage.used / usage.total) * 100
    return round(percent, 2)

#----------------------------------------------
# Find old log files
#----------------------------------------------
def find_old_logs(directory, min_days_old):
    if not os.path.exists(directory):
        return []
    cmd = [
        "find", directory,
        "-type", "f",
        "-name", "*.log",
        "-mtime", f"+{min_days_old}"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    files = result.stdout.strip().split("\n")
    return [f for f in files if f]

#---------------------------------------------------
# Compress logs
#---------------------------------------------------
def compress_logs(file_list, archive_dir, dry_run, nice_level, ionice_class):
    if not file_list:
        return 0, 0
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir, exist_ok=True)
        
    #Archive name based on date/time
    archive_name = datetime.now().strftime("logs-%Y%m%d-%H%M%S.tar.gz")
    archive_path = os.path.join(archive_dir, archive_name)
    
    
    # Build tar command
    cmd = [
        "nice", f"{nice_level}",
        "ionice", f" -c{ionice_class}",
        "tar", "--remove-files", "-czf", archive_path
    ] + file_list
    
    if dry_run:
        print(f"[DRY-RUN] Would run: {' '.join(cmd)}")
        return 0, 0
    
    before_size = sum(os.path.getsize(f) for f in file_list)
    subprocess.run(cmd, check=False)
    after_size = os.path.getsize(archive_path)

    return before_size, after_size

# ------------------------
# Main Loop
# ------------------------
def main():
    parser = argparse.ArgumentParser(description="Disk Log Manager Daemon")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry mode (no deletion/compression)")
    args = parser.parse_args()

    config = load_config()
    log_file = os.path.join("logs", "disklogmanager.log")
    os.makedirs("logs", exist_ok=True)

    while True:
        usage = get_disk_usage_percent(config['disk_path'])
        log_message(f"Disk usage at {usage}% (threshold {config['threshold_percent']}%)", log_file)

        if usage >= config['threshold_percent']:
            log_message(f"Threshold exceeded! Starting compression...", log_file)

            for log_dir in config['log_directories']:
                old_logs = find_old_logs(log_dir, config['min_days_old'])
                if old_logs:
                    log_message(f"Found {len(old_logs)} old log files in {log_dir}", log_file)
                    before, after = compress_logs(
                        old_logs,
                        os.path.join("archives", os.path.basename(log_dir.strip("/"))),
                        args.dry_run,
                        config['nice_level'],
                        config['ionice_class']
                    )
                    if not args.dry_run:
                        saved = before - after
                        log_message(f"Compressed {len(old_logs)} files: {before/1024/1024:.2f}MB → {after/1024/1024:.2f}MB (Saved {saved/1024/1024:.2f}MB)", log_file)
                else:
                    log_message(f"No old logs found in {log_dir}", log_file)

        time.sleep(config['check_interval_seconds'])

if __name__ == "__main__":
    main()
