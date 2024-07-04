
# bmpfont.py
"""
pygame support for bitmapped fonts.

License: Freeware
Original author: Paul Sidorsky, 2001. paulsid@home.com
Licenses for bitmap fonts:
    * Carton and Gemma designed by Damien Guard.
    * DansSans and Minigage designed by Asa Durkee. Public domain.
    * Unscii and Unscii8Tall designed by Viznut. Public domain.

A simple class for bitmapped fonts in pygame.
A bitmapped font is simply a font specified as a bitmap.
Bitmapped fonts are easy to use and fast.
The characters are all the same size, so it's easy
to treat the screen as a matrix of character cells,
as if you were in text mode (e.g. for a status screen
between levels).
Drawbacks are that you must of course draw the font yourself,
you can't change the colour, and you don't get special effects
like bold, italics, etc.

Font Index File Descrption

bmpfont lets you define where each character is within the bitmap,
along with some other options.	This lets you use a bitmap of any
dimension with characters of any size.	The file where the position
of each character is defined is called the font index file.  It is
a simple text file that may contain the lines listed below.
Whitespace is ignored, but the keywords are case-sensitive.
NOTE:  Blank lines and comments are not allowed.

bmpfile filename
- filename is the full name (with optional path) of the bitmap file
  to use.  The file can be of any type supported by pygame.image.
  Defaults to font.bmp with no path if omitted.

width x
height y
- Specifies the dimensions of a character, in pixels.  Each
  character must be of the same width and height.  width defaults
  to 8 and height to 8 if omitted.

transrgb r g b
- Specifies the colour being used to indicate transparency.  If you
  don't wish to use transparency, set this to an unused colour.
  Defaults to black (0, 0, 0) if omitted.

alluppercase
- If present, indicates the font only has one case of letters which
  are specified in the index using upper case letters.	Strings
  rendered with BmpFont.blit() will be converted automatically.  If
  omitted, the font is assumed to have both cases of letters.

- All other lines are treated as character index specifiers with
  the following format:

  char x y

  - char is the character whose position is being specified.  It
	can also be "space" (without quotes) to define a position for
	the space character.
  - x is the column number where char is located.  The position
	within the bitmap will be x * width (where width is specified
	above).
  - y is the row number where char is located.	The position will
	be y * height.
"""
import os
import pygame.image
from pygame.locals import *

CWD       = os.path.dirname(__file__)
FONTDIR   = os.path.join(os.path.abspath(os.path.join(CWD, os.pardir)),"fonts")

__all__ = ["BmpFont"]

class BmpFont:
	"""Provides an object for treating a bitmap as a font."""

	# Constructor - creates a BmpFont object.
	# Parameters:  idxfile - Name of the font index file.
	def __init__(self, idxfile = os.path.join(FONTDIR,"Exupery/Exupery.idx")):
		# Setup default values.
		self.alluppercase = 0
		self.chartable = {}
		self.bmpfile = os.path.join(FONTDIR,"Exupery/Exupery.png")
		self.width = 10
		self.height = 12
		self.transrgb = (0, 0, 0)

		# Read the font index.	File errors will bubble up to caller.
		f = open(idxfile, "r")

		for x in f.readlines():
			# Remove EOL, if any.
			if x[-1] == '\n': x = x[:-1]
			words = x.split()

			# Handle keywords.
			if words[0] == "bmpfile":
				self.bmpfile = x.split(None, 1)[1]
			elif words[0] == "alluppercase":
				self.alluppercase = 1
			elif words[0] == "width":
				self.width = int(words[1])
			elif words[0] == "height":
				self.height = int(words[1])
			elif words[0] == "transrgb":
				self.transrgb = (int(words[1]), int(words[2]),
								 int(words[3]))
			else:  # Default to index entry.
				if words[0] == "space": words[0] = ' '
				if self.alluppercase: words[0] = words[0].upper()
				self.chartable[words[0]] = (int(words[1]) * self.width,
											int(words[2]) * self.height)
		f.close()

		# Setup the actual bitmap that holds the font graphics.
		self.surface = pygame.image.load(os.path.join(os.path.dirname(idxfile),self.bmpfile))
		self.surface.set_colorkey(self.transrgb, RLEACCEL)

	# blit() - Copies a string to a surface using the bitmap font.
	# Parameters:  string	 - The message to render.  All characters
	#						   must have font index entries or a
	#						   KeyError will occur.
	#			   surf 	 - The pygame surface to blit string to.
	#			   pos		 - (x, y) location specifying location
	#						   to copy to (within surf).  Meaning
	#						   depends on usetextxy parameter.
	#			   usetextxy - If true, pos refers to a character cell
	#						   location.  For example, the upper-left
	#						   character is (0, 0), the next is (0, 1),
	#						   etc.  This is useful for screens with
	#						   lots of text.  Cell size depends on the
	#						   font width and height.  If false, pos is
	#						   specified in pixels, allowing for precise
	#						   text positioning.
	def blit(self, string, surf, pos = (0, 0), usetextxy = 1):
		"""Draw a string to a surface using the bitmapped font."""
		x, y = pos
		if usetextxy:
			x *= self.width
			y *= self.height
		surfwidth, surfheight = surf.get_size()
		fontsurf = self.surface.convert(surf)

		if self.alluppercase: string = string.upper()

		# Render the font.
		for c in string:
			# Perform automatic wrapping if we run off the edge of the
			# surface.
			if x >= surfwidth:
				x -= surfwidth
				y += self.height
				if y >= surfheight:
					y -= surfheight

			surf.blit(fontsurf, (x, y),
					 (self.chartable[c], (self.width, self.height)))
			x += self.width

# Example code.  Run this file as a script to activate.
if __name__ == "__main__":
	selected = "quote_big"  # quote_big, quote_tiny
	import pygame
	pygame.init()
	screen = pygame.display.set_mode((400, 240),depth=1)
	screen.fill((255,255,255))
	font_small1 = BmpFont(os.path.join(FONTDIR,"Minigage/minigage.idx"))
	font_small2 = BmpFont(os.path.join(FONTDIR,"Gemma/Gemma.idx"))
	font_narrow  = BmpFont(os.path.join(FONTDIR,"SHPinscher_png/SHPinscher.idx"))
	font_tiny  = BmpFont(os.path.join(FONTDIR,"Carton/Carton.idx"))
	font_big = BmpFont(os.path.join(FONTDIR,"DansSans/DansSans.idx"))
	charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"\
		  "0123456789 !@#$%^&*()-=_+\|[]{};:'\",.<>/?`~" * 5

	if selected == "quote_tiny":
		quote = ["If you want to change the future,","start living as if","you're already there.","","                     ~ Lynn Conway"]
		for count, line in enumerate(quote):
			font_small1.blit(line, screen, (3, 5 + (count * 2)))

	if selected == "quote_big":
		quote = ["If you want to","change the future,","start living as if","you're already there.","","         ~ Lynn Conway"]
		for count, line in enumerate(quote):
			font_big.blit(line, screen, (2, 1 + count))


	pygame.display.update()
	while pygame.event.poll().type != QUIT: pass

# End of file bmpfont.py
