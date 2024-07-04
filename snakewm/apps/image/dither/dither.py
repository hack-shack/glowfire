"""
Takes an input image, scales it to no larger than the beepy screen,
and converts it to black-and-white (1-bit) with several diffusion methods.

Requires https://github.com/hbldh/hitherdither
pip install git+https://www.github.com/hbldh/hitherdither

Only accepts .jpg without errors.
.png image will cause numpy error.
"""

from PIL import Image

def hdither(image, diffusion_method):
    import hitherdither
    #palette1 = hitherdither.palette.Palette.create_by_median_cut(image)
    monochrome = hitherdither.palette.Palette([(0,0,0),(255,255,255)])
    dithered = hitherdither.diffusion.error_diffusion_dithering(image, palette=monochrome, method=diffusion_method, order=1)
    return dithered

maxsize = (400, 400)
image = Image.open("image.jpg")  # must be JPG format; PNG fails
image.thumbnail(maxsize, Image.LANCZOS)  # sometimes Image.Resampling.LANCZOS depending on Pillow version

"""
dither the image every way possible
my quality rankings (choose the appropriate one for your source images):
1 - stucki : best compromise between gradiation and sharp edges
2 - PIL's Floyd-Steinberg: best for gradiation; does not do sharp edges well
3 - atkinson : higher contrast, dramatic shadows and highlights, sharp edges
4 - sierra-2-4a : renders fine detail depending on the source image
"""
def all_ditherings():
    # Built-in PIL Floyd_Steinberg diffusion method
    dithered_fs_image = image.convert(mode='1', dither=Image.FLOYDSTEINBERG)
    dithered_fs_image.save('output_floyd-steinberg-pil.png')

    # hitherdither diffusion methods
    diffusion_maps = ["stucki","atkinson","burkes","floyd-steinberg","jarvis-judice-ninke","sierra3","sierra2","sierra-2-4a"]
    for diffusion_map in diffusion_maps:
        dithered_image = hdither(image, diffusion_method=diffusion_map)
        dithered_image.save("output_" + diffusion_map + ".png")

# Dither a single image with a single diffusion method.
#dithered_image = hdither(image, diffusion_method="stucki")
#dithered_image.save("output.png")

all_ditherings()