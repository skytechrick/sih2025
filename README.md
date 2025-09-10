# sih2025

# 🚀 Python Project Setup & Server Run Guide

This guide explains how to set up the Python environment, install dependencies, run scripts, and start the server.

---

## 📦 1. Create & Activate Virtual Environment

### Linux / Mac

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
Windows (PowerShell)
powershell
Copy code
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
📚 2. Install Dependencies
bash
Copy code
pip install -r requirements.txt
▶️ 3. Run Python File
bash
Copy code
python3 your_file_name.py   # Linux / Mac
python your_file_name.py    # Windows
Replace your_file_name.py with the actual script you want to execute.

🌐 4. Run FastAPI / Uvicorn Servers
Option 1: Run API server (port 8001)
bash
Copy code
uvicorn api:app --reload --host 0.0.0.0 --port 8001
Option 2: Run Server file (port 8000)
bash
Copy code
uvicorn server:app --reload --host 0.0.0.0 --port 8000
Explanation
api:app → runs the FastAPI app from api.py

server:app → runs the FastAPI app from server.py

--reload → auto-reloads on file changes (development mode)

--host 0.0.0.0 → accessible on your network

--port → specify port (default is 8000 if not given)

🛑 5. Deactivate Virtual Environment
When done working:

bash
Copy code
deactivate
✅ Quick Summary
Create virtual env → python3 -m venv venv

Activate env → source venv/bin/activate (Linux/Mac) or .\venv\Scripts\activate (Windows)

Install deps → pip install -r requirements.txt

Run script → python3 file.py (Linux/Mac) or python file.py (Windows)

Start server →

uvicorn api:app --reload --host 0.0.0.0 --port 8001

uvicorn server:app --reload --host 0.0.0.0 --port 8000
```
