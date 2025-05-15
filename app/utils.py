from PIL import Image
import os
from django.conf import settings
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def optimize_image(image_field):
    """
    Optimize image by:
    1. Converting to WebP format
    2. Resizing if too large
    3. Compressing quality
    
    Returns a new InMemoryUploadedFile with optimized image
    """
    if not image_field:
        return None
    
    # Open image
    img = Image.open(image_field)
    
    # Convert to RGB if needed (for PNG with transparency)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Define max dimensions for thumbnail
    max_width = 1200
    max_height = 1200
    
    # Resize if needed
    if img.width > max_width or img.height > max_height:
        # Calculate new dimensions while preserving aspect ratio
        if img.width > img.height:
            new_width = max_width
            new_height = int(max_width * img.height / img.width)
        else:
            new_height = max_height
            new_width = int(max_height * img.width / img.height)
        
        img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Save as WebP with compression
    output = BytesIO()
    img.save(output, format='WEBP', quality=85, optimize=True)
    output.seek(0)
    
    # Return a new file object
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{os.path.splitext(os.path.basename(image_field.name))[0]}.webp",
        'image/webp',
        sys.getsizeof(output),
        None
    ) 