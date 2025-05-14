#!/usr/bin/env python
"""
Manual CSS and JS minification script for Django project.
This script minifies all CSS and JS files in the static directory.
"""

import os
import re
import shutil
from pathlib import Path
import subprocess

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIR = os.path.join(BASE_DIR, 'staticfiles')

def ensure_dir(directory):
    """Make sure a directory exists."""
    os.makedirs(directory, exist_ok=True)

def basic_css_minify(css_content):
    """Basic CSS minification."""
    # Remove comments
    css_content = re.sub(r'/\*[\s\S]*?\*/', '', css_content)
    # Remove whitespace around special characters
    css_content = re.sub(r'\s*([{};:,])\s*', r'\1', css_content)
    # Remove leading and trailing whitespace
    css_content = re.sub(r'^\s+', '', css_content)
    css_content = re.sub(r'\s+$', '', css_content)
    # Remove line breaks
    css_content = re.sub(r'\n', '', css_content)
    # Remove multiple spaces
    css_content = re.sub(r'\s+', ' ', css_content)
    return css_content

def basic_js_minify(js_content):
    """Basic JavaScript minification."""
    # Remove single-line comments
    js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
    # Remove multi-line comments
    js_content = re.sub(r'/\*[\s\S]*?\*/', '', js_content)
    # Remove whitespace around special characters
    js_content = re.sub(r'\s*([{};:,=\(\)])\s*', r'\1', js_content)
    # Remove leading and trailing whitespace
    js_content = re.sub(r'^\s+', '', js_content)
    js_content = re.sub(r'\s+$', '', js_content)
    # Remove multiple spaces
    js_content = re.sub(r'\s+', ' ', js_content)
    return js_content

def minify_file(source_path, dest_path, minify_function):
    """Minify a file and save it to destination."""
    print(f"Minifying: {source_path}")
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_path)
        ensure_dir(dest_dir)
        
        # Read the file
        with open(source_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Minify the content
        minified_content = minify_function(content)
        
        # Write the minified content
        with open(dest_path, 'w', encoding='utf-8') as file:
            file.write(minified_content)
        
        # Calculate reduction percentage
        original_size = os.path.getsize(source_path)
        minified_size = os.path.getsize(dest_path)
        reduction = ((original_size - minified_size) / original_size) * 100
        
        print(f"  Reduced by {reduction:.2f}% ({(original_size - minified_size) / 1024:.2f} KB)")
        return True
    except Exception as e:
        print(f"  Error minifying {source_path}: {e}")
        # Copy the file as is
        shutil.copy2(source_path, dest_path)
        return False

def process_static_files():
    """Process all static files in the static directory."""
    css_count = 0
    js_count = 0
    
    # Walk through all files in static directory
    for root, _, files in os.walk(STATIC_DIR):
        for file in files:
            # Get the full file path
            file_path = os.path.join(root, file)
            
            # Calculate the relative path
            rel_path = os.path.relpath(file_path, STATIC_DIR)
            
            # Create the destination path
            dest_path = os.path.join(STATICFILES_DIR, rel_path)
            
            # Process based on file extension
            _, extension = os.path.splitext(file)
            extension = extension.lower()
            
            if extension == '.css':
                if minify_file(file_path, dest_path, basic_css_minify):
                    css_count += 1
            elif extension == '.js':
                if minify_file(file_path, dest_path, basic_js_minify):
                    js_count += 1
            else:
                # Copy other static files as-is to the staticfiles directory
                dest_dir = os.path.dirname(dest_path)
                ensure_dir(dest_dir)
                shutil.copy2(file_path, dest_path)
    
    return css_count, js_count

def main():
    """Main function to process all static files."""
    print("Starting manual CSS and JS minification...")
    
    # Make sure the staticfiles directory exists
    ensure_dir(STATICFILES_DIR)
    
    # Process the files
    css_count, js_count = process_static_files()
    
    print(f"\nMinified {css_count} CSS files and {js_count} JS files.")
    print("Static file optimization complete!")

if __name__ == "__main__":
    main() 