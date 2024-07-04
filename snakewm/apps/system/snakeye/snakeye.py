import platform
import time
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements.ui_image import UIImage
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_window import UIWindow

if platform.system() == 'Darwin':
    print('DEBUG: Running on macOS.')
    from .rammac import rammac as ram_check
    from .cpumac import cpumac as cpu_check
elif platform.system() == 'Linux':
    print('DEBUG: Running on Linux.')
    from .ramlin import ramlin as ram_check
    from .cpulin import cpulin as cpu_check
else:
    print('ERROR: Cannot detect platform. Maybe Windows?')
    exit

BLACK = ((0,)*3)
WHITE = ((255,)*3)

class Snakeye(UIWindow):
    DIMS = (100,180)
    LABELHEIGHT = 20
    GRAPHDIMS = (round(DIMS[0]/2),DIMS[1]-LABELHEIGHT)
    print('GRAPHDIMS: ' + str(GRAPHDIMS))

    def __init__(self, position, manager):
        super().__init__(
            #rect=pygame.Rect(position, self.DIMS),
            rect=pygame.Rect(position, (self.DIMS[0]+34,self.DIMS[1]+51)),
            manager=manager,
            window_display_title="snakeye",
            object_id=ObjectID(class_id="@snakeye_window",object_id="#snakeye_window"),
            resizable=False
        )

        self.label_cpu = UILabel(
            relative_rect=pygame.Rect(0,0,  self.DIMS[0]/2,self.LABELHEIGHT),
            text="cpu",
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snakeye_label",object_id="#snakeye_label_cpu")
        )

        self.label_ram = UILabel(
            relative_rect=pygame.Rect(self.DIMS[0]/2,0,  self.DIMS[0]/2,self.LABELHEIGHT),
            text="ram",
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snakeye_label",object_id="#snakeye_label_ram")
        )

        self.image_cpu = UIImage(
            relative_rect=pygame.Rect(0,self.LABELHEIGHT,
                                      self.DIMS[0]/2,self.DIMS[1]-self.LABELHEIGHT),
            image_surface=pygame.Surface((30,30)),
            #image_surface=pygame.Surface(pygame.Rect(self.DIMS[0]/2,self.DIMS[1]-24)).convert(),
            manager=manager,
            container=self,
            parent_element=self,
        )

        self.image_ram = UIImage(
            relative_rect=pygame.Rect(self.DIMS[0]/2+2,self.LABELHEIGHT,
                                      self.DIMS[0]/2,self.DIMS[1]-self.LABELHEIGHT),
            image_surface=pygame.Surface((30,30)),
            #image_surface=pygame.Surface(pygame.Rect(self.DIMS[0]/2,self.DIMS[1]-24)).convert(),
            manager=manager,
            container=self,
            parent_element=self,
        )

        self.cpu = pygame.Surface(self.GRAPHDIMS)
        self.cpu.fill(WHITE)
        self.ram = pygame.Surface(self.GRAPHDIMS)
        self.ram.fill(WHITE)
        self.last_time = 0

    def process_event(self, event):
        super().process_event(event)

    def update(self, delta):
        super().update(delta)
        # limit frame rate to 4 FPS
        if time.time() - self.last_time > 0.25:
            self.draw_cpu()
            self.draw_ram()
            self.image_cpu.image.blit(self.cpu, (0, 0))
            self.image_ram.image.blit(self.ram, (0, 0))
            self.last_time = time.time()

    def draw_cpu(self):
        """ Draw rolling graph for CPU. """
        cpu_percentage = cpu_check()
        #print("DEBUG: cpu_percentage: " + str(cpu_percentage) + " %")
        self.cpu.scroll(dy=1)
        # first, clear background to white
        pygame.draw.line(
            surface=self.cpu,
            color=WHITE,
            start_pos=(0,0),
            end_pos=(self.GRAPHDIMS[0],0)
        )
        # second, draw cpu usage
        pygame.draw.line(
            surface=self.cpu,
            color=BLACK,
            start_pos=((self.GRAPHDIMS[0],0)),
            end_pos=(self.GRAPHDIMS[0]-round(cpu_percentage * (self.GRAPHDIMS[0]/100)),0),
            width=1,
        )

    def draw_ram(self):
        """ Draw rolling graph for RAM. """
        ram_percentage = ram_check()
        self.ram.scroll(dy=1)
        # first, clear background to white
        pygame.draw.line(
            surface=self.ram,
            color=WHITE,
            start_pos=(10,0),
            end_pos=(20,0),
            width=1
            #end_pos=(self.GRAPHDIMS[0],0)
        )
        # second, draw ram consumption
        pygame.draw.line(
            surface=self.ram,
            color=BLACK,
            start_pos=(0,0),
            end_pos=(round(ram_percentage * (self.GRAPHDIMS[0]/100)),0),
            width=1,
        )
