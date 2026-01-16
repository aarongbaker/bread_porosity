# Installation & Verification Checklist

## Before You Start

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Windows, macOS, or Linux OS confirmed
- [ ] Sample bread images available (JPG or PNG)
- [ ] Terminal/Command Prompt access

---

## 🍎 macOS Installation

### Step 1: Install Python & Dependencies

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.9+
brew install python@3.9

# Verify Python installation
python3 --version
```

### Step 2: Clone/Navigate to Project

```bash
cd ~/Desktop/bread_porosity
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import cv2, numpy, matplotlib, scipy; print('✓ All packages installed')"
```

Expected output: `✓ All packages installed`

### Step 5: Run GUI

```bash
python gui.py
```

The GUI should launch with the modern dark theme! 🎨

---

## 🪟 Windows Installation

### Step 1: Install Python

1. Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Click "Install Now"
4. Verify installation:

```powershell
python --version
```

### Step 2: Navigate to Project

```powershell
cd C:\Users\YourUsername\Desktop\bread_porosity
```

### Step 3: Create Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activation again
.\venv\Scripts\Activate.ps1

# Verify activation (you should see (venv) in your prompt)
```

### Step 4: Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verify installation:
```powershell
python -c "import cv2, numpy, matplotlib, scipy; print('✓ All packages installed')"
```

Expected output: `✓ All packages installed`

### Step 5: Run GUI

```powershell
python gui.py
```

The GUI should launch with the modern dark theme! 🎨

---

## 🐧 Linux Installation

### Step 1: Install Python & Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.9 python3-pip python3-venv

# Or for Fedora/RHEL
sudo dnf install python3.9 python3-pip

# Verify installation
python3 --version
```

### Step 2: Navigate to Project

```bash
cd ~/Desktop/bread_porosity
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import cv2, numpy, matplotlib, scipy; print('✓ All packages installed')"
```

Expected output: `✓ All packages installed`

### Step 5: Run GUI

```bash
python gui.py
```

The GUI should launch with the modern dark theme! 🎨

---

## ✅ Verify Tool Structure

Check that all files exist:

### macOS/Linux
```bash
files=("__init__.py" "gui.py" "analyze.py" "quality_control.py" "export_reporting.py" "requirements.txt" "README.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then echo "✓ $file"; else echo "✗ MISSING: $file"; fi
done
```

### Windows
```powershell
$files = @(
    "__init__.py",
    "gui.py",
    "analyze.py",
    "quality_control.py",
    "export_reporting.py",
    "requirements.txt",
    "README.md"
)
foreach ($file in $files) {
    if (Test-Path $file) { Write-Host "✓ $file" } 
    else { Write-Host "✗ MISSING: $file" }
}
```

Expected: All files should show ✓

---

## 🧪 Test Import

### macOS/Linux
```bash
python -c "
from gui import BreadPorositytoolGUI
from quality_control import QualityControlManager
from export_reporting import ExportEngine
print('✓ All modules import successfully')
"
```

### Windows
```powershell
python -c "
from gui import BreadPorositytoolGUI
from quality_control import QualityControlManager
from export_reporting import ExportEngine
print('✓ All modules import successfully')
"
```

Expected output: `✓ All modules import successfully`

---

## 🔧 Troubleshooting Installation

### Issue: "No module named cv2"
```bash
# macOS/Linux
pip install opencv-python

# Windows
pip install opencv-python
```

### Issue: "No module named numpy"
```bash
pip install numpy
```

### Issue: "No module named matplotlib"
```bash
pip install matplotlib
```

### Issue: All dependencies installed but still getting import errors

**macOS/Linux:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Windows:**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: Python not found (Windows)
- Reinstall Python and **check "Add Python to PATH"**
- Use `py` instead of `python`: `py --version`

### Issue: Permission denied (macOS/Linux)
```bash
# Run with sudo if needed
sudo pip install -r requirements.txt
```

### Issue: Virtual environment won't activate

**macOS/Linux:**
```bash
# Make sure you're in the project directory
cd ~/Desktop/bread_porosity
source venv/bin/activate
```

**Windows:**
```powershell
# Make sure you're in the project directory
cd C:\Users\YourUsername\Desktop\bread_porosity
.\venv\Scripts\Activate.ps1
```

---

## 🚀 Quick Start After Installation

1. **Launch GUI**: `python gui.py`
2. **Load Image**: Click "📂 Open Folder"
3. **Select Image**: Choose a bread slice image
4. **Analyze**: Click "▶ Analyze"
5. **View Results**: Check "📈 Results" tab

---

## 📋 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.9 | 3.11+ |
| RAM | 2 GB | 4 GB+ |
| Disk space | 500 MB | 2 GB+ |
| Image size | 1 MP | 3-12 MP |

---

## 🎯 Next Steps

1. Read [README.md](README.md) for feature overview
2. Read [QUICK_START.md](QUICK_START.md) for usage guide
3. Analyze your first bread image
4. Check [FEATURES.md](FEATURES.md) for advanced features
5. Review [BREAD_TYPE_PROFILES.md](BREAD_TYPE_PROFILES.md) for quality control

---

**Installation complete! Ready to analyze bread! 🍞📊**
