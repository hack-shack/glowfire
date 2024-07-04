# Using fonts in glowfire

There are 3 main ways to use fonts in glowfire.


## Outline fonts

These are the majority of scalable vector fonts designed today (otf, ttf).
They antialias at the pixel level.
This produces a ragged look at < 24 pixels high,
but looks good at larger sizes > 36 pixels.


### Using outline fonts

To use an outline font,
add the font to the snakewm/data/fonts folder and
specify it in snakewm/theme_en.json.


## Bitmap strikes

This is the current preferred method.
It lets us render certain TrueType fonts as crisp bitmaps.

TTF font files can contain embedded "bitmap strikes."
This is a bitmap font included within the TrueType font.
The designer makes certain point sizes: 12, 14, 16.5, etc.

Examples are ProFontIIx.ttf and TerminusTTF.
Note: Bitmap strikes may be missing from other versions
of these fonts found on the internet.

### Using bitmap strikes

To use the bitmap strikes for a font,
add the font to the snakewm/data/fonts folder and
specify it in snakewm/theme_en.json.

Specify a point size that matches a known bitmap strike.
The type engine will preferentially render a bitmap
version of the TrueType font if it can find a bitmap
strike at the defined size.

Example from theme_en.json:
```
"font":{
            "name":"ProFontIIx",
            "size":"14",
            "regular_path":"snakewm/data/fonts/ProFontIIx/ProFontIIx.ttf"
        },
```

### Finding bitmap strikes

To identify which bitmap strike sizes are included in a font,
install FontForge and open the font. 
[FontForge](#using-fontforge-to-view-a-bitmap-font)

[FontForge showing pixel strike sizes in ProFontIIx.ttf](data/fontforge-load-bitmap-fonts.png)


### Using FontForge to view a bitmap font

  * Download from https://fontforge.org
  * Launch FontForge
  * Open the font, "ProFontIIx.ttf"
  * It will ask if you want to load bitmaps. It will display
    the point sizes for all available pixel strikes in the file.
  * Select all bitmap sizes and click OK.
  * A window of glyphs appears. Click the glyph for "A" to select it.
  * Click the Window menu > New Bitmap Window.
  * To switch between font sizes, click View > Bigger Pixel Size or Smaller Pixel Size.


## Bitmap fonts

This is not the preferred method.
The bmpfont library can be used to load fonts from PNG files.
Currently it is slower than FreeType, and has a very different API.
But it is good for making pixel-accurate fonts easily.

It is the most flexible, allowing owners to edit their font PNGs directly.

# Localization

## Japanese
pygame-gui doesn't render the kana or kanji from outlines in a TTF or OTF.
It will render whitespace or a square.
To work around this, use a Japanese font containing bitmap strikes.
Example included: KHDotFont.

# References

## Bitmap strikes

Overview of bitmap strikes
"Windows and ClearType vs. TTFs with Embedded Bitmaps"
  * https://int10h.org/blog/2016/01/windows-cleartype-truetype-fonts-embedded-bitmaps/

FontForge: how to create and edit bitmap strikes
  * https://fontforge.org/archive/editexample8.html

monobit: tools for working with monochrome bitmap fonts
  * https://github.com/robhagemans/monobit


# Experimental notes
Formats that do not seem to render properly:
otf, otb