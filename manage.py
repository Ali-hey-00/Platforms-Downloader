#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    try:
        # Set default Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_downloader.settings')
        
        # Validate Python version
        if sys.version_info < (3, 9):
            raise RuntimeError(
                "This project requires Python 3.9 or higher. "
                f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
            )

        # Create required directories
        base_dir = Path(__file__).resolve().parent
        media_dir = base_dir / 'media' / 'downloads'
        media_dir.mkdir(parents=True, exist_ok=True)

        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc

        execute_from_command_line(sys.argv)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()