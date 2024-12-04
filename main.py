#!/usr/bin/env python3
"""
Service Schedule Optimizer Application
Main entry point for the application.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure environment
os.environ["PYTHONPATH"] = str(project_root)

from scripts.ServiceScheduleOptimizer import CalendarApp


def main():
    """Initialize and run the calendar application."""
    try:
        app = CalendarApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
