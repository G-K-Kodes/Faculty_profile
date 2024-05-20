#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess
import threading
import time

def start_scheduler():
    """Start the scheduler command at regular intervals."""
    while True:
        subprocess.run(['python', 'manage.py', 'scheduler'])
        time.sleep(30) 

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faculty.settings")
    try:
        from django.core.management import execute_from_command_line
        
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    else:
        scheduler_thread = threading.Thread(target=start_scheduler)
        scheduler_thread.start()
        execute_from_command_line(sys.argv)



if __name__ == "__main__":
    main()
