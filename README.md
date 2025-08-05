# DiskLogManager

**DiskLogManager** is a lightweight Python-based tool for real-time disk usage monitoring and automatic log file compression.  
It helps prevent **disk space exhaustion** by compressing old log files while keeping active logs untouched.

---

## ✨ Features

- **Real-time monitoring** of disk usage (interval-based, not just daily cron)
- **Threshold-based compression** — triggers instantly when usage exceeds a set percentage
- **Keeps active logs safe** — skips the most recent log file so logging continues without interruption
- **Low CPU/I/O impact** — uses `nice` and `ionice` for minimal performance hit
- **Works with any application logs** (tested with Apache2, Nginx, Laravel)
- **Configurable directories** — monitor multiple log folders
- **Simple file structure** — compressed files saved in the same directory as original logs

---

## 📂 Example Directory Setup

```plaintext
/var/log/apache2/
  access.log
  error.log
  fake_apache1.log
  compressed-logs.tar.gz

/var/www/laravel/public/logs/
  laravel-2025-07-31.log
  fake_public1.log
  compressed-logs.tar.gz

/var/www/laravel/storage/logs/
  laravel-2025-07-31.log
  fake_storage1.log
  compressed-logs.tar.gz
  ```

## ⚙️ Configuration

Edit `config.yaml` to suit your needs:

```yaml
# Disk usage threshold percentage
threshold_percent: 70

# How often to check (seconds)
check_interval_seconds: 600

# Minimum file age in days before compression
min_days_old: 7

# Directories to monitor
log_directories:
  - "/var/log/apache2/"
  - "/var/www/laravel/public/logs"
  - "/var/www/laravel/storage/logs"

# Disk path to monitor
disk_path: "/"

# CPU and I/O priority
nice_level: 19
ionice_class: 3
```
## 🚀 Usage

### Dry Run (no files changed)
```bash
sudo python3 disklogmanager.py --dry-run
```
### Run in real-mode
```bash
sudo python3 disklogmanager.py
```
## 🔍 How It Works

1. **Monitors disk usage** at the configured interval.
2. **When threshold is exceeded:**
   - Finds all `.log` files older than `min_days_old`.
   - Skips the most recently modified (active) log file.
   - Compresses the rest into `compressed-logs.tar.gz` in the same directory.
   - Removes original uncompressed files after compression.
3. **Keeps logging live** — Apache/Nginx/Laravel keep writing to their active logs.

## 🚀 This is smaple one 
```
/etc/httpd/conf.d/aswin.conf
/var/log/httpd
```
**Test**

**- checking**

