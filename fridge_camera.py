from picamera2 import Picamera2, Preview
from PIL import Image
from time import sleep, strftime

# Initialize the camera
camera = Picamera2()

# Set camera resolution (adjust as needed)
camera.resolution = (300, 300)

camera.start()
# Capture a frame
def capture_image():
    sleep(1)  # Adjust the sleep duration as needed to control frame rate
    camera.capture_file("fridge_image.jpg")
    image_path = "/home/danny/SmartFridge/fridge_image.jpg"
    rotate_image(image_path)
    sleep(2)
def rotate_image(image_path):
    with Image.open(image_path) as img:
        rotated_img = img.rotate(180)
        rotated_img.save(image_path)
