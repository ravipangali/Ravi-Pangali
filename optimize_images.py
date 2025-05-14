#!/usr/bin/env python
"""
Image optimization script for Django project.
This script optimizes all images in the media and static directories.
"""

import os
import sys
from PIL import Image
from pathlib import Path

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Directories to scan for images
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
STATIC_IMG_DIR = os.path.join(BASE_DIR, 'static', 'img')

# Image file extensions to optimize
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# Quality settings (80% is usually a good balance)
JPEG_QUALITY = 80
PNG_COMPRESSION = 9

def optimize_image(filepath):
    """Optimize a single image file."""
    try:
        filename, extension = os.path.splitext(filepath)
        extension = extension.lower()
        
        # Only process supported image types
        if extension not in IMAGE_EXTENSIONS:
            return False
            
        # Create optimized filename
        if '_optimized' in filename:
            return False  # Skip already optimized images
            
        optimized_filename = f"{filename}_optimized{extension}"
        
        # Open and process the image
        with Image.open(filepath) as img:
            # Convert to RGB if RGBA for JPG
            if extension in ['.jpg', '.jpeg'] and img.mode == 'RGBA':
                img = img.convert('RGB')
                
            # Resize large images (optional)
            if max(img.size) > 2000:
                # Calculate new size while maintaining aspect ratio
                ratio = min(2000 / img.size[0], 2000 / img.size[1])
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Save optimized image
            if extension in ['.jpg', '.jpeg']:
                img.save(optimized_filename, quality=JPEG_QUALITY, optimize=True)
            elif extension == '.png':
                img.save(optimized_filename, optimize=True, compress_level=PNG_COMPRESSION)
            elif extension == '.webp':
                img.save(optimized_filename, quality=JPEG_QUALITY)
            
            # Get file sizes
            original_size = os.path.getsize(filepath)
            optimized_size = os.path.getsize(optimized_filename)
            
            # Replace original if optimized is smaller
            if optimized_size < original_size:
                os.replace(optimized_filename, filepath)
                print(f"Optimized: {filepath} - Reduced by {(original_size - optimized_size) / 1024:.2f} KB")
                return True
            else:
                # Delete optimized if not smaller
                os.remove(optimized_filename)
                print(f"Skipped: {filepath} - Already optimized")
                return False
                
    except Exception as e:
        print(f"Error optimizing {filepath}: {e}")
        return False

def scan_directory(directory):
    """Scan a directory recursively and optimize all images."""
    count = 0
    size_saved = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            _, extension = os.path.splitext(filepath)
            
            if extension.lower() in IMAGE_EXTENSIONS:
                # Get file size before optimization
                original_size = os.path.getsize(filepath)
                
                # Optimize the image
                if optimize_image(filepath):
                    # Calculate space saved
                    new_size = os.path.getsize(filepath)
                    saved = original_size - new_size
                    size_saved += saved
                    count += 1
    
    return count, size_saved

def main():
    """Main function to optimize all images."""
    print("Starting image optimization...")
    
    # Optimize media directory
    if os.path.exists(MEDIA_DIR):
        media_count, media_saved = scan_directory(MEDIA_DIR)
        print(f"\nOptimized {media_count} images in media directory.")
        print(f"Total saved: {media_saved / 1024 / 1024:.2f} MB")
    
    # Optimize static/img directory
    if os.path.exists(STATIC_IMG_DIR):
        static_count, static_saved = scan_directory(STATIC_IMG_DIR)
        print(f"\nOptimized {static_count} images in static/img directory.")
        print(f"Total saved: {static_saved / 1024 / 1024:.2f} MB")
    
    print("\nImage optimization complete!")

if __name__ == "__main__":
    main() 