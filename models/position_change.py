from PIL import Image

# Open the image
image_path = "/templates/floorplan.png"
image = Image.open(image_path)

# Open the icon image
icon_path = "your_icon.png"
icon = Image.open(icon_path)

# Define the position where you want to place the icon (x, y)
position = (100, 100)

# Paste the icon onto the image at the specified position
image.paste(icon, position, icon)

# Save the modified image
output_path = "output_image.jpg"
image.save(output_path)

# Display the modified image
image.show()
