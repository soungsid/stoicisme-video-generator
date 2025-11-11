"""
Configuration de MoviePy pour ImageMagick
"""
import os

def configure_moviepy():
    """
    Configure MoviePy pour utiliser ImageMagick correctement dans Docker
    """
    # Chemin vers le binaire ImageMagick
    imagemagick_binary = os.getenv('IMAGEMAGICK_BINARY', '/usr/bin/convert')
    
    # Configurer moviepy.config
    try:
        from moviepy.config import change_settings
        change_settings({"IMAGEMAGICK_BINARY": imagemagick_binary})
        print(f"✅ MoviePy configured with ImageMagick: {imagemagick_binary}")
    except Exception as e:
        print(f"⚠️  Could not configure MoviePy: {e}")
        print("   Trying alternative configuration...")
        
        # Configuration alternative via variable d'environnement
        os.environ['IMAGEMAGICK_BINARY'] = imagemagick_binary
        
    return imagemagick_binary

# Configurer automatiquement à l'import
IMAGEMAGICK_BINARY = configure_moviepy()
