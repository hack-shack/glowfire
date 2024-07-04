from picamera2 import Picamera2, Preview

from PIL import Image
maxsize = 240   # max size of image


picam2 = Picamera2()
print(picam2.sensor_modes)
config = picam2.create_still_configuration(main={"size": (640,480)},lores={"size": (320, 240)},display=None)
picam2.configure(config)
picam2.start()

image = picam2.capture_image("main")
image.save("test.jpg")


#picam2.start_preview(Preview.NULL)
#picam2.start_and_capture_file('test.jpg')
