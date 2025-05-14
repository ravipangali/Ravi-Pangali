#!/usr/bin/env python
"""
Script to specifically optimize the home.js file.
Home.js is quite large and needs special attention for optimization.
"""

import os
import re
from pathlib import Path

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent
HOME_JS_PATH = os.path.join(BASE_DIR, 'static', 'js', 'home.js')
HOME_JS_OPTIMIZED_PATH = os.path.join(BASE_DIR, 'static', 'js', 'home.min.js')

def read_file(file_path):
    """Read file content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    """Write content to file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def optimize_home_js():
    """Optimize home.js file."""
    print(f"Optimizing home.js file...")
    
    if not os.path.exists(HOME_JS_PATH):
        print(f"Error: {HOME_JS_PATH} not found!")
        return False
    
    # Read the file
    content = read_file(HOME_JS_PATH)
    original_size = len(content)
    
    # Create an optimized version
    # 1. Remove comments
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    
    # 2. Remove console.log statements
    content = re.sub(r'console\.log\(.*?\);', '', content)
    
    # 3. Remove unnecessary whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r';\s*;', ';', content)
    
    # 4. Remove whitespace around operators
    content = re.sub(r'\s*([{}:;,=+\-*\/])\s*', r'\1', content)
    
    # 5. Split back function declarations for readability
    content = re.sub(r'function', '\nfunction', content)
    
    # Write optimized file
    write_file(HOME_JS_OPTIMIZED_PATH, content)
    
    # Update the home.html to use the optimized version
    optimized_size = len(content)
    savings = original_size - optimized_size
    savings_kb = savings / 1024
    savings_percent = (savings / original_size) * 100
    
    print(f"  Original size: {original_size/1024:.2f} KB")
    print(f"  Optimized size: {optimized_size/1024:.2f} KB")
    print(f"  Saved: {savings_kb:.2f} KB ({savings_percent:.2f}%)")
    
    return True

def main():
    """Main function."""
    print("Starting home.js optimization...")
    
    if optimize_home_js():
        print("\nLinking optimized home.js in templates...")
        # Create update instructions for user
        print("\nTo use the optimized home.js, update templates/home.html:")
        print('Replace: <script src="/static/js/home.js" defer></script>')
        print('With: <script src="/static/js/home.min.js" defer></script>')
        
        print("\nhome.js optimization complete!")

if __name__ == "__main__":
    main() 