#!/usr/bin/env python3
"""
Startup script for the Trade Analysis Dashboard
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Start the Streamlit dashboard."""
    dashboard_script = Path(__file__).parent / "src" / "python" / "dashboard_app.py"
    
    if not dashboard_script.exists():
        print("❌ Dashboard script not found")
        sys.exit(1)
    
    print("🌍 Starting Trade Analysis Dashboard...")
    print("📱 Dashboard will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(dashboard_script)
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

if __name__ == "__main__":
    main() 