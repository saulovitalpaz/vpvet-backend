"""Simple script to run the VPVET server"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Run the app module
if __name__ == '__main__':
    os.system('python -m app')