# Learn pygame-gui
Our goal is not to write a complex app but to
internalize the Write -> Run -> Debug "loop."

Everything is written in Python.
Look at the main .py files for each app.

## Take apart apps
Take apart apps that you find interesting.
Find the parts you want to re-use.
Each app is made of fonts, rectangles, windows, panels, etc.
Find the parts that appeal to you, specifically.
We will examine an existing app, minitime.

### Take apart minitime.py
Open its launcher code first.
Open snakewm/apps/clocks/minitime/__init__.py.
* Find where it starts the window at a specific x,y coordinate.
* Modify these coordinates such that its window opens in a
  different place onscreen, without placing it outside
  the screen boundaries at the edges of the Memory LCD.
Open snakewm/apps/clocks/minitime/minitime.py.
* The main program code.
* See this image for guidance:
[minitime functions](data/minitime-functions.png')
* Examine these functions and their indentation.
* Use a Python linter plugin for VSCode to check your code style.
* Adjust one thing at a time, then re-run.

### Read pygame-gui source
You must know parts of the pygame-gui source if you are to program pygame-gui.
The pygame_gui source is at beepy-sdk/src/pygame_gui.
minitime.py is based around a UIWindow:
beepy-sdk/src/pygame_gui/ui_window.py


# References

## pygame-gui
Layout guide for pygame-gui
  * https://pygame-gui.readthedocs.io/en/latest/layout_guide.html