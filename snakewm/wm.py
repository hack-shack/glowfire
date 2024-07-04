#!/usr/bin/python3

"""
snakewm: snakeware window manager
An overlapping window manager for pygame.
This is the glowfire fork for the SQFMI beepy.
"""

TESTMODE = __name__ == "__main__"

# IMPORTS 1 - These modules run on desktops and Pi Zero
# =====================================================
# Standard library imports
import io
import os
import pwd
import sys
import importlib

# Third party imports
import pygame
import pygame_gui

# HARDWARE DETECTION - determine if running on Pi or desktop
# ==========================================================
def is_raspi():
# Determine if we're on Raspi hardware, or a desktop computer (simulator).
# Disable certain hardware-related functions if in simulator.
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if "raspberry pi" in m.read().lower():
                print("INFO : Firmware detected as raspi.")
                SYSTEM = "raspi"
                return True
    except Exception:
        print('DEBUG: raspi_detection:')
        print(Exception)
    return False

# GLOBAL VARIABLES
# ================
REAL_PI = is_raspi()

# IMPORTS 2 - These modules require actual hardware (Pi Zero only)
# ================================================================
if REAL_PI == True:
    print('DEBUG: Running on raspi hardware.')
    import gpiozero  # for beepy sidebutton (GPIO 17 -> GND)
    SIDEBUTN = gpiozero.Button(17)
    # TODO: Make a mock pin for desktops, and map it to the tilde key
    # https://gpiozero.readthedocs.io/en/stable/api_pins.html#mock-pins
if REAL_PI == False:
    print('DEBUG: Not running on raspi hardware.')
    print('DEBUG: GPIO functions will not work.')
    try:
        print('DEBUG: Attempting to import gpiozero module.')
        import gpiozero
        print('DEBUG: Imported gpiozero. Attempting to import mock pin factory.')
        from gpiozero.pins.mock import MockFactory
        print('DEBUG: gpiozero.pins.mock.MockFactory successfully imported.')
    except:
        print('ERROR: Could not import gpiozero module.')
        print('ERROR: To fix, "python3 -m pip install gpiozero"')
    gpiozero.Device.pin_factory = MockFactory()
    print('DEBUG: Built mock pin factory.')

# establish PYTHONPATH - needed for local application imports
if 'PYTHONPATH' not in os.environ:
    print('ERROR: PYTHONPATH empty. Attempting to create.')
    PYTHONPATH = os.path.join(os.getcwd(), 'snakewm')
    sys.path.insert(0, PYTHONPATH)
    try:
        os.environ['PYTHONPATH'] = PYTHONPATH
    except:
        raise
    print('PYTHONPATH = ' + os.getenv('PYTHONPATH'))

if TESTMODE:
    print('DEBUG: wm.py: Test mode is active.')
    try:
        print('DEBUG: wm.py: PYTHONPATH = ' + os.environ['PYTHONPATH'])
    except:
        raise
    from appmenu.appmenupanel import AppMenuPanel
    from snapper import Snapper

    from snakebg.bg import SnakeBG
    from snakebg.bgmenu import SnakeBGMenu
else:
    print('DEBUG: wm.py: Test mode is deactivated.')
    from appmenu.appmenupanel import AppMenuPanel
    from snapper import Snapper

    from snakewm.snakebg.bg import SnakeBG
    from snakewm.snakebg.bgmenu import SnakeBGMenu

LAUNCHDIR = os.getcwd()
print('DEBUG: LAUNCHDIR = ' + LAUNCHDIR)
WM_DIR = os.path.join(LAUNCHDIR,'snakewm')

class SnakeWM:
    """ The snakewm window manager. """
    SCREEN = None
    DIMS = None
    BG = None
    MANAGER = None

    BG_COLOR = ((255,)*3)

    # Language selection. Uncomment the language you want to use.
    LANGUAGE = 'en'  # us-EN, English, English
    #LANGUAGE = 'fr'  # fr-FR, French, français
    #LANGUAGE = 'ja'  # ja-JP, Japanese, 日本語

    # Import theme file for the UI manager.
    THEMEFILE = os.path.join(WM_DIR, 'data/themes/glowfire.json')
    print('DEBUG: THEMEFILE: ' + str(THEMEFILE))

    # Bitmap cursor image file.
    CURSORFILE = os.path.join(WM_DIR, 'data/cursors/cursor_24.png')

    # Wallpaper image file.
    WALLPAPER = os.path.join(WM_DIR, 'data/wallpaper/grayscreen.png')

    # background color paint properties
    PAINT = False  # TODO: Make this a toggle in snapper or in hardware.
    PAINT_RADIUS = 10

    # 2 color palette for painting
    PAINT_COLOR = 1
    PAINT_COLOR_LIST = [
        ((0,)  *3),
        ((255,)*3), ]

    # paint shapes
    PAINT_SHAPE = 0
    NUM_SHAPES = 3

    # reference to SnakeBG object for dynamic backgrounds
    DYNBG = None
    DYNBG_MENU = None

    # currently focused window
    FOCUS = None

    # dictionary that will contain the apps directory structure
    APPS = {}
    # reference to the root app menu object
    APPMENU = None
    # reference to the 'snapper' widget panel
    SNAPPER = None

    def __init__(self):
        # populate the apps tree
        apps_path = os.path.dirname(os.path.abspath(__file__)) + "/apps"
        print('DEBUG: apps_path: ' + str(apps_path))
        SnakeWM.iter_dir(self.APPS, apps_path)

        pygame.init()

        # Initialize the button events into pygame's event system.
        SIDEBUTN_DOWN = pygame.event.Event(pygame.USEREVENT+0)
        SIDEBUTN_UP   = pygame.event.Event(pygame.USEREVENT+1)
        # Hardware GPIO triggers gpiozero events for press and release.
        #SIDEBUTN.when_pressed  = pygame.event.post(SIDEBUTN_DOWN)
        #SIDEBUTN.when_released = pygame.event.post(SIDEBUTN_UP)

        # Initialize pygame to framebuffer.
        os.putenv("SDL_FBDEV", "/dev/fb1")
        pygame.display.init()

        # Get screen dimensions.
        #print(pygame.display.Info())
        #self.DIMS = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.DIMS = 400,240

        # Initialize display surface.
        self.SCREEN = pygame.display.set_mode(self.DIMS)

        # Initialize background.
        self.BG = pygame.Surface((self.DIMS))
        self.BG.fill(self.BG_COLOR)
        self.BRUSH_SURF = pygame.Surface((self.DIMS), flags=pygame.SRCALPHA)
        self.BRUSH_SURF.fill((0, 0, 0, 0))

        # Initialize UI Manager.
        self.MANAGER = pygame_gui.UIManager(window_resolution=self.DIMS,
                                            theme_path=self.THEMEFILE,
                                            starting_language=self.LANGUAGE,
                                            translation_directory_paths=['snakewm/appmenu/data/translations'])

        # Import additional themes. They will override earlier loaded themes, if keys are the same.
        self.MANAGER.get_theme().load_theme('snakewm/apps/image/wildbeast/theme.json')

        # Pre-load Latin fonts used for the UI and HTML styled elements.
        self.MANAGER.add_font_paths(font_name    = 'ProFont',
                                    regular_path = 'snakewm/data/fonts/ProFontIIx/ProFontIIx.ttf')
        self.MANAGER.preload_fonts([{'name':'ProFont', 'point_size':14}])
        self.MANAGER.add_font_paths(font_name    = 'ComputerModern',
                                    regular_path = 'snakewm/data/fonts/ComputerModern/cmunobx.ttf',
                                    bold_path    = 'snakewm/data/fonts/ComputerModern/cmunbx.ttf')
        self.MANAGER.preload_fonts([{'name':'ComputerModern','point_size':18,'style':'regular'}])
        self.MANAGER.preload_fonts([{'name':'ComputerModern','point_size':20,'style':'regular'}])
        self.MANAGER.preload_fonts([{'name':'ComputerModern','point_size':28,'style':'bold'}])

        if self.LANGUAGE == 'ja':
            # Pre-load Japanese fonts. For rendering, kana and kanji must be in 'bitmap strike' format.
            # Bitmap strike information: https://fontforge.org/archive/editexample8.html
            print('DEBUG: Loading Japanese fonts.')
            print('デバッグ： 日本語フォントの読み込み。')
            self.MANAGER.add_font_paths(font_name    = 'KH-Dot-Hibiya-24',
                                        regular_path = 'snakewm/data/fonts/KHDot/KH-Dot-Hibiya-24.ttf')
            self.MANAGER.add_font_paths(font_name    = 'KH-Dot-Hibiya-32',
                                        regular_path = 'snakewm/data/fonts/KHDot/KH-Dot-Hibiya-32.ttf')
            self.MANAGER.preload_fonts([{'name':'KH-Dot-Hibiya-24','point_size':24,'style':'regular'}])
            self.MANAGER.preload_fonts([{'name':'KH-Dot-Hibiya-32','point_size':32,'style':'regular'}])

        self.CURSOR_IMG = pygame.image.load(self.CURSORFILE).convert()

    def iter_dir(tree, path):
        """
        Static function that recursively populates dict 'tree' with the
        app directory structure starting at 'path'.
        """
        for f in os.listdir(path):
            if os.path.isfile(path + "/" + f + "/__init__.py"):
                tree[f] = None
            elif os.path.isdir(path + "/" + f):
                tree[f] = {}
                SnakeWM.iter_dir(tree[f], path + "/" + f)

    def loadapp(self, app, params=None):
        """
        Load and run a Python module as an app (example: "apps.test.HelloWorld").
        Apps are basically just Python packages. The loaded app package must contain an __init__.py with a load() function that accepts a UIManager parameter and a params list parameter.

        The load() function should create an instance of the app to load and add the app UI to the passed UIManager object. See existing apps for examples.
        """
        if not TESTMODE:
            app = "snakewm." + app

        _app = importlib.import_module(app)

        try:
            _app.load(self.MANAGER, params)
        except:
            #print('DEBUG: App quit.')
            raise
            pygame.quit()

    def appmenu_load(self, app):
        """
        This function is passed to AppMenuPanel objects to be called when
        an app is selected to be opened.
        The root app menu is destroyed, and the app is loaded.
        """
        if self.APPMENU is not None:
            self.APPMENU.destroy()
            self.APPMENU = None

        self.loadapp(app)

    def set_bg_color(self, color):
        """
        Set the wallpaper to 'color', where color is an RGB tuple.
        """
        self.BG = pygame.Surface((self.DIMS))
        self.BG_COLOR = color
        self.BG.fill(self.BG_COLOR)

    def set_bg_image(self, file):
        """
        Set the wallpaper to an image.
        """
        filename, file_extension = os.path.splitext(file)
        if file_extension == ".jpg" or file_extension == ".png":
            self.BG = pygame.transform.scale(pygame.image.load(file), self.DIMS).convert()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        self.CURSORIMAGE = pygame.image.load(self.CURSORFILE).convert_alpha()
        self.new_mouse_pos = (0,0)

        self.set_bg_image(self.WALLPAPER)

        while running:
            delta = clock.tick(60) / 1000.0
            pressed = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.APPMENU is None:
                            # open app menu
                            self.APPMENU = AppMenuPanel(
                                manager  = self.MANAGER,
                                pos      = (0,0),
                                path     = "apps",
                                elements = self.APPS,
                                loadfunc = self.appmenu_load
                            )
                            if self.SNAPPER is None:
                                # open snapper
                                self.SNAPPER = Snapper(self.MANAGER)
                        else:
                            self.APPMENU.destroy()
                            self.APPMENU = None
                            if self.SNAPPER is not None:
                                self.SNAPPER.destroy()
                                self.SNAPPER = None

                    elif event.key == pygame.K_b and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        print("DEBUG: Pressed power key.")
                        running = False
                        pygame.quit()
                        exit()

                    if pressed[pygame.K_LSHIFT]:
                        # TODO: Implement these features
                        if event.key == pygame.K_p:
                            # toggle paint mode
                            self.PAINT = not self.PAINT
                            self.BRUSH_SURF.fill((0, 0, 0, 0))
                        elif event.key == pygame.K_d:
                            # toggle dynamic background
                            if self.DYNBG is None and self.DYNBG_MENU is None:
                                print('DEBUG: toggle dynamic background ON')
                                self.DYNBG_MENU = SnakeBGMenu(self.MANAGER)
                            elif self.DYNBG is not None:
                                print('DEBUG: toggle dynamic background OFF')
                                del self.DYNBG
                                self.DYNBG = None

                # Workaround for lack of a mouse cursor.
                # Restrict coordinates to 400x240 Memory LCD.
                elif event.type == pygame.MOUSEMOTION:
                    #print('EventPos: ' + str(event.pos))
                    self.new_mouse_pos = [0,0]
                    if event.pos[0] < 0:
                        self.new_mouse_pos[0] = 0
                    elif event.pos[0] >= self.DIMS[0]:
                        self.new_mouse_pos[0] = self.DIMS[0]
                    elif event.pos[0] >= 0:
                        self.new_mouse_pos[0] = event.pos[0]
                    if event.pos[1] < 0:
                        self.new_mouse_pos[1] = 0
                    elif event.pos[1] >= self.DIMS[1]:
                        self.new_mouse_pos[1] = self.DIMS[1]
                    elif event.pos[1] >= 0:
                        self.new_mouse_pos[1] = event.pos[1]
                    #print('NewPos  : ' + str(self.new_mouse_pos[0]) + ', ' + str(self.new_mouse_pos[1]))
                    #pygame.mouse.set_pos(new_mouse_pos[0],new_mouse_pos[1])
                    #self.blit(self.CURSORIMAGE, self.SCREEN, dest=(new_mouse_pos[0],new_mouse_pos[1]))
                    #print(pygame.mouse.get_pos())

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        pass # here for expansion
                    if event.button == 2:  # Middle click
                        pass # here for expansion
                    if event.button == 3:  # Right click
                        if self.APPMENU is None:
                            # open app menu
                            self.APPMENU = AppMenuPanel(
                                manager  = self.MANAGER,
                                pos      = (0,0),
                                path     = "apps",
                                elements = self.APPS,
                                loadfunc = self.appmenu_load
                            )
                            if self.SNAPPER is None:
                                # open snapper
                                self.SNAPPER = Snapper(self.MANAGER)
                        else:
                            self.APPMENU.destroy()
                            self.APPMENU = None
                            if self.SNAPPER is not None:
                                self.SNAPPER.destroy()
                                self.SNAPPER = None

                    if self.PAINT:
                        if event.button == 4:
                            # mouse wheel up
                            if pressed[pygame.K_LALT]:
                                self.PAINT_COLOR = (self.PAINT_COLOR + 1) % len(
                                    self.PAINT_COLOR_LIST
                                )
                            elif pressed[pygame.K_LCTRL]:
                                self.PAINT_SHAPE = (
                                    self.PAINT_SHAPE + 1
                                ) % self.NUM_SHAPES
                            else:
                                self.PAINT_RADIUS += 2
                        elif event.button == 5:
                            # mouse wheel down
                            if pressed[pygame.K_LALT]:
                                self.PAINT_COLOR = (self.PAINT_COLOR - 1) % len(
                                    self.PAINT_COLOR_LIST
                                )
                            elif pressed[pygame.K_LCTRL]:
                                self.PAINT_SHAPE = (
                                    self.PAINT_SHAPE - 1
                                ) % self.NUM_SHAPES
                            else:
                                self.PAINT_RADIUS -= 2
                            if self.PAINT_RADIUS < 2:
                                self.PAINT_RADIUS = 2

                elif event.type == pygame.USEREVENT:
                    # Event Debugging: uncomment one or more of these to view UI events on stdout
                    #print("DEBUG: event.ui_object_id: " + str(event.ui_object_id))
                    #print("DEBUG: event.ui_element: " + str(event.ui_element))
                    #print("DEBUG: event.type: " + str(event.type))
                    #print(event.user_type)  # Note: will be removed in pygame-gui 0.8.0
                    if event.type == "window_selected":
                        # focus selected window
                        if self.FOCUS is not None:
                            self.FOCUS.unfocus()
                        self.FOCUS = event.ui_element
                        self.FOCUS.focus()

                    if event.ui_object_id == "#wallpaper_picker":
                        try:
                            if isinstance(event.text, str):
                                #print('DEBUG: image_path: ' + str(event.text))
                                self.set_bg_image(event.text)
                        except:
                            pass

                    if event.ui_object_id == "#appmenupanel":
                        # the app menu was closed. close the snapper too.
                        if self.SNAPPER is not None:
                            self.SNAPPER.kill()
                            self.SNAPPER = None

                    elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                        if "#bgmenu" in event.ui_object_id:
                            if "close_button" in event.ui_object_id:
                                self.DYNBG_MENU.kill()
                                del self.DYNBG_MENU
                                self.DYNBG_MENU = None
                            elif not "title_bar" in event.ui_object_id:
                                print('DEBUG: Dynamic background selected.')
                                selected_bg = event.ui_object_id.split(".")[1]
                                self.DYNBG = SnakeBG(selected_bg, TESTMODE)
                                self.DYNBG_MENU.kill()
                                del self.DYNBG_MENU
                                self.DYNBG_MENU = None

                                self.PAINT = False

                self.MANAGER.process_events(event)

            self.MANAGER.update(delta)

            # blit paintbrush/dynbg layer
            if self.DYNBG is not None:
                # update dynamic background
                self.DYNBG.draw(self.BRUSH_SURF)
                self.SCREEN.blit(self.BG, (0, 0))
                self.SCREEN.blit(self.BRUSH_SURF, (0, 0))
            elif self.PAINT:
                mpos = pygame.mouse.get_pos()

                # default drawing the brush to the temporary brush layer
                draw_surf = self.BRUSH_SURF

                if pygame.mouse.get_pressed()[0]:
                    # paint to the actual background
                    draw_surf = self.BG

                if self.PAINT_SHAPE == 0:
                    # circle
                    pygame.draw.circle(
                        draw_surf,
                        self.PAINT_COLOR_LIST[self.PAINT_COLOR],
                        mpos,
                        self.PAINT_RADIUS,
                    )
                elif self.PAINT_SHAPE == 1:
                    # square
                    pygame.draw.rect(
                        draw_surf,
                        self.PAINT_COLOR_LIST[self.PAINT_COLOR],
                        pygame.Rect(
                            (mpos[0] - self.PAINT_RADIUS, mpos[1] - self.PAINT_RADIUS),
                            (self.PAINT_RADIUS * 2, self.PAINT_RADIUS * 2),
                        ),
                    )
                elif self.PAINT_SHAPE == 2:
                    # triangle
                    pygame.draw.polygon(
                        draw_surf,
                        self.PAINT_COLOR_LIST[self.PAINT_COLOR],
                        (
                            (mpos[0] - self.PAINT_RADIUS, mpos[1] + self.PAINT_RADIUS),
                            (mpos[0] + self.PAINT_RADIUS, mpos[1] + self.PAINT_RADIUS),
                            (mpos[0], mpos[1] - self.PAINT_RADIUS),
                        ),
                    )

                self.SCREEN.blit(self.BG, (0, 0))
                self.SCREEN.blit(self.BRUSH_SURF, (0, 0))
                self.BRUSH_SURF.fill((0, 0, 0, 0))
            else:
                # not in paint mode, just blit background
                self.SCREEN.blit(self.BG, (0, 0))

            self.MANAGER.draw_ui(self.SCREEN)

            # Debug / failsafe code for mouse cursor issue
            # --------------------------------------------
            """ We run pygame without a window manager.
            Normally a WM would provide system cursors,
            window frames, and multitasking. We do all this
            in wm.py.
            It lacks a mouse pointer so we blit one in.
            The pointer coordinates can also run off-screen.
            We deal with that earlier in the script. """
            #print(str(self.new_mouse_pos[0]), str(self.new_mouse_pos[1]))
            self.SCREEN.blit(self.CURSORIMAGE, (self.new_mouse_pos[0], self.new_mouse_pos[1]))
            pygame.display.update()


if TESTMODE:
    wm = SnakeWM()
    wm.run()
