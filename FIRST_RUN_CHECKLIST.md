# First Run Checklist for Bread Porosity Analysis Tool

1. **Install Python 3.9+**
2. **Clone the repository**
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Check for required config files:**
   - `config.json` (should exist)
   - `qc_config.json` (should exist)
5. **Check for required folders:**
   - `unprocessed/` (input images)
   - `processed/` (output images)
   - `output/` (visualizations)
   - `results/` (metrics/results)
   - If missing, create them:
     ```bash
     mkdir -p unprocessed processed output results
     ```
6. **(Linux/Mac) Install Tkinter if needed:**
   - macOS: `brew install python-tk`
   - Ubuntu: `sudo apt-get install python3-tk`
7. **Run the GUI:**
   ```bash
   python gui/main.py
   ```
8. **Run a test analysis:**
   ```bash
   python analyze.py sample.jpg --pixel-size 0.1
   ```
9. **Run tests:**
   ```bash
   pytest
   ```
10. **(Optional) Set up pre-commit hooks:**
    ```bash
    pre-commit install
    ```

---

If you encounter issues, see the README or open an issue.
