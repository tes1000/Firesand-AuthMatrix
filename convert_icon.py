"""Convert favicon.png to favicon.ico for use with PyInstaller"""
from PIL import Image

# Open the PNG file
img = Image.open('UI/assets/favicon.png')

# Convert to ICO with multiple sizes for better compatibility
# Common sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# Save as ICO
img.save('UI/assets/favicon.ico', format='ICO', sizes=icon_sizes)
print("Successfully converted favicon.png to favicon.ico")
