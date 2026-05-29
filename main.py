"""
POE2 Overlay Timer – entry point

Usage:
    python main.py                          normal run
    python main.py --debug                  always show overlay + print events
    python main.py --test-map "Riverbank"   show overlay with notes for that map
    python main.py --list-notes             list all parsed note entries and exit
"""
import sys
import os
import argparse

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import App

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='POE2 Overlay Timer')
    parser.add_argument('--debug',     action='store_true',
                        help='Always show overlay; print events to console')
    parser.add_argument('--test-map',  metavar='MAP_NAME', default=None,
                        help='Immediately load notes for MAP_NAME (implies --debug)')
    parser.add_argument('--list-notes', action='store_true',
                        help='Print all parsed note entries and exit')
    args = parser.parse_args()

    App(
        debug=args.debug or (args.test_map is not None),
        test_map=args.test_map,
        list_notes=args.list_notes,
    ).run()

