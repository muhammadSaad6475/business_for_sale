from PIL import Image
import requests
from io import BytesIO

# Function to resize image with padding to maintain aspect ratio
def resize_image_with_padding(img, target_width, target_height):
    original_width, original_height = img.size
    ratio = min(target_width/original_width, target_height/original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
    
    # Create a new image with the desired size and a black background
    new_img = Image.new("RGB", (target_width, target_height))
    # Paste the resized image onto the center of the new image
    new_img.paste(resized_img, ((target_width - new_width) // 2, (target_height - new_height) // 2))
    return new_img

# Provide the image URL
image_url = "https://publiclistingphotos.s3.amazonaws.com/3508567_BFS.png"

# Sizes you want to resize your image to
sizes = [(851, 420), (526, 240), (146, 202), (411, 243), (265, 146)]

# Fetch the image from the URL
response = requests.get(image_url)
if response.status_code == 200:
    img = Image.open(BytesIO(response.content))

    # Resize the image to each target size and process/save as needed
    for size in sizes:
        resized_image = resize_image_with_padding(img, size[0], size[1])
        # Save each resized image with a unique filename
        filename = f"resized_image_{size[0]}x{size[1]}.png"
        resized_image.save(fp=filename)
        print(f"Saved {filename}")
else:
    print(f"Failed to retrieve the image. Status code: {response.status_code}")

