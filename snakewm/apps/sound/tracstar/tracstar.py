"""
tracstar: play tracker modules + audio files
enjoy music anywhere

MIT License

(c) 2020 Luís Gonçalo
https://github.com/lmagoncalo

(c) 2023 Asa Durkee
https://github.com/hack-shack
"""
import os
from pathlib import Path
from subprocess import check_output
import time
import i18n
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton
from pygame_gui.elements import UIHorizontalSlider
from pygame_gui.elements import UIImage
from pygame_gui.elements import UISelectionList
from tinytag import TinyTag
from .mixer import Mixer

class Tracstar(pygame_gui.elements.UIPanel):
    """ A panel containing the tracstar music player. """
    DIMS = (400,240)

    def __init__(self, pos, manager):
        """ Create a window for the tracstar music player interface. """
        super().__init__(
            pygame.Rect(pos, self.DIMS),
            manager=manager,
            object_id=ObjectID(class_id="@tracstar_panel",
                               object_id="#tracstar"
            )
        )

        i18n.load_path.append(os.path.join(os.path.dirname(__file__),"data/translations"))

        # Create mixer object
        self.mixer = Mixer()

        # Set state: paused
        self.is_paused: bool = False

        # Key for playing track
        self.playing_track: str = None

        self.volume: float = 0.1
        self.volume_levels: list = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1.0]  # volume levels are not linear, for better experience
        self.volume_index: int = 2  # start with this volume level index from the list

        # Initialize close button.
        self.button_close = UIButton(
            relative_rect=pygame.Rect(376,0,24,24),
            text='',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_button",
                               object_id="#tracstar_button_close"
            )
        )

        # Initialize 5 button playback cluster.
        self.button_last = UIButton(
            relative_rect=pygame.Rect(0,210,80,30),
            text=i18n.t("last"),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_button",
                               object_id="#op-lastbtn"
            )
        )

        self.button_vol_decrease = UIButton(
            relative_rect=pygame.Rect(80,210,80,30),
            text=i18n.t("vol-"),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_button",
                               object_id="#op-vol-btn"
            )
        )

        self.button_play = UIButton(
            relative_rect=pygame.Rect(160,210,80,30),
            text=i18n.t("play"),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_button",
                               object_id="#op-playbtn"
            )
        )

        self.button_vol_increase = UIButton(
            relative_rect=pygame.Rect(240,210,80,30),
            text=i18n.t("vol+"),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_button",
                               object_id="#op-vol+btn"
            )
        )

        self.button_next = UIButton(
            relative_rect=pygame.Rect(320,210,80,30),
            text=i18n.t("next"),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_button",
                               object_id="#op-nextbtn"
            )
        )

        # Initialize slider to show current playback status in track.
        self.slider_current_track = UIHorizontalSlider(
            relative_rect = pygame.Rect(1,183,398,26),
            start_value=0.0,
            value_range=(0.0,1.0),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@tracstar_slider",
                               object_id="#tracstar_slider_current_track"
            ),
        )

        # Initialize magnetic tape "tractape."
        self.animate_magbar : bool = False
        self.animation_magbar_frames : list = []
        self.animation_magbar_max : int = 10
        self.animation_magbar_counter : int = 0
        animations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/animations')
        for each_frame in range(self.animation_magbar_max):
            frame = pygame.image.load(animations_path + "/tractape" + str(each_frame) + ".png")
            frame = frame.convert()
            self.animation_magbar_frames.append(frame)
        self.surface_magbar = pygame.image.load(os.path.join(animations_path,'tractape0.png'))
        self.surface_magbar_white = pygame.image.load(os.path.join(animations_path,'tractapew.png'))

        self.magbar = UIImage(
            relative_rect=pygame.Rect(10,184,380,24),
            image_surface=self.surface_magbar,
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@tracstar_image",
                               object_id="#tracstar_magbar"
            )
        )

        # Initialize GUI playlist.
        self.music_list = UISelectionList(
            relative_rect=pygame.Rect((0,20), (self.DIMS[0], 162)),
            item_list=[],
            manager=manager,
            allow_multi_select=False,
            allow_double_clicks=True,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_selectionlist",
                               object_id="#tracstar_playlist"
            )
        )

        # Scan music directory for audio files.
        if os.geteuid() == 0:
            print('Running as root.')
            self.pwd = Path(check_output('pwd').decode('utf-8'))
            self.musicdir = os.path.join(self.pwd.parent,'music')
        else:
            self.musicdir = os.path.join(Path("~").expanduser(),"music")
        # Create music dictionary and populate it with song info.
        self.music_dict = self.scan_music_folder(dirname=self.musicdir)
        # Clean up song info.
        for abspath,metadata in self.music_dict.items():
            if 'title' in metadata:
                if metadata['title'] == None:
                    print('No title found. Using filename: ' + str(metadata['filename']))
                    metadata['title'] = metadata['filename']
                try:
                    if metadata['artist'] == None:
                        print('No artist found. Using blank string as artist for: ' + str(metadata['filename']))
                        metadata['artist'] = ''
                except:
                    print('No artist found. Using blank string as artist for: ' + str(metadata['filename']))
                    metadata['artist'] = ''

        # Create a sorted dictionary for the playlist.
        self.sorted_dict = {index:(key) for index,(key) in enumerate(self.music_dict)}

        # Populate GUI playlist with all detected files.
        print('DEBUG: Populating GUI playlist.')
        for index,key in self.sorted_dict.items():
            title = self.music_dict[key]['title']
            oid = str(f'{key}')
            self.music_list.add_items([(title,oid)])

        # Select the first track in the GUI list.
        # Discussion about programmatic selection: https://github.com/MyreMylar/pygame_gui/discussions/218
        # I access private objects to work around the limitation. ~asa
        if len(self.music_list.item_list) == 0:
            print('DEBUG: Music list empty.')
        else:
            first_track_key = next(key for index,key in self.sorted_dict.items() if index == 0)
            first_track_title = self.music_dict[first_track_key]['title']
            self.music_list._default_selection = (first_track_title, first_track_key)
            self.music_list._set_default_selection()

        # Animation for magbar
        self.last_time = 0

    def scan_music_folder(self,dirname):
        """ Scan music directory for audio files and tracker modules. """
        # Extension list for audio codecs.
        audio_extensions: list = ['flac','mp3','ogg','wav']  # TODO: add ffmpeg decoder for m4a files
        # Extension list for music tracker modules.
        mod_extensions: list = ['667','669','amf','ams','c67','dbm','digi','dmf','dsm','dsym','dtm','far','fmt','gdm','gtk','gt2','ice','imf','it','itp','j2b','m15','mdl','med','mid','mms','mo3','mod','mptm','mt2','mtm','mus','okt','oxm','plm','psm','pt36','ptm','s3m','sfx','sfx2','st26','stk','stm','stp','stx','symmod','ult','umx','wow','xm','xmf']

        track_files = {}

        # Read basic file metadata.
        if os.path.isdir(dirname):
            for root,dirs,files in os.walk(dirname):
                for filename in files:
                    for extension in audio_extensions + mod_extensions:
                        if os.path.splitext(filename)[1] == ("." + extension):
                            abspath = os.path.abspath(os.path.join(dirname,filename))
                            nameonly = os.path.splitext(filename)[0]  # filename without extension
                            track_files[abspath] = {
                                'abspath'    :   abspath,
                                'filename'   :   filename,
                                'nameonly'   :   nameonly,
                                'extension'  :   extension,
                                'mtime'      :   os.path.getmtime(abspath)
                            }

        # Read track metadata.
        for abspath,metadata in track_files.items():
            if metadata['extension'] in audio_extensions:
                tag = TinyTag.get(abspath)
                track_files[abspath].update({
                    'album'  : tag.album,
                    'artist' : tag.artist,
                    'bitrate' : tag.bitrate,
                    'duration' : tag.duration,
                    'samplerate' : tag.samplerate,
                    'title' : tag.title,
                    'track' : tag.track,
                    'track_total' : tag.track_total
                })
            elif metadata['extension'] in mod_extensions:
                title_string = metadata['filename'].rstrip("." + metadata['extension']).replace("_"," ")
                track_files[abspath].update({
                    'title' : title_string
                })

        return track_files

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_object_id == "#tracstar.#tracstar_button_close":
                    self.kill()
                if event.ui_object_id == "#tracstar.#op-playbtn":
                    selected_track = self.music_list.get_single_selection()
                    # Is a track selected in the playlist?
                    if selected_track is None:
                        pass
                    else:
                        for t in self.music_list._raw_item_list:
                            if t[0] == selected_track:
                                music_path = str(t[1])
                        # Is a track currently playing?
                        if self.mixer.get_busy() == True:
                            print('DEBUG: is_busy')
                            # Is a different track selected than the one playing?
                            if self.playing_track is not None:
                                if self.playing_track == music_path:
                                    print('DEBUG: selected and playing tracks are identical.')
                                    self.mixer.pause()
                                    self.is_paused = True
                                    self.button_play.set_text(i18n.t("play"))
                                else:
                                    print('DEBUG: selected and playing tracks are different.')
                                    self.mixer.stop()
                                    self.mixer.load(music_path)
                                    print('DEBUG: Playing different track.')
                                    self.playing_track = music_path
                                    self.mixer.play()
                                    self.is_paused = False
                                    self.button_play.set_text(i18n.t("pause"))
                        # If music is paused, resume music. Else load and play.
                        elif self.mixer.get_busy() == False:
                            # Is a different track selected than the one playing?
                            if self.playing_track is not None:
                                if self.playing_track == music_path:
                                    print('DEBUG: selected and playing tracks are identical.')
                                    self.mixer.resume()
                                    self.is_paused = False
                                    self.button_play.set_text(i18n.t("pause"))
                                else:
                                    print('DEBUG: selected and playing tracks are different.')
                                    self.mixer.stop()
                                    self.mixer.load(music_path)
                                    self.playing_track = music_path
                                    self.mixer.play()
                                    self.is_paused = False
                                    self.button_play.set_text(i18n.t("pause"))
                            elif self.playing_track is None:
                                self.mixer.load(music_path)
                                self.playing_track = music_path
                                self.mixer.play()
                                self.is_paused = False
                                self.button_play.set_text(i18n.t("pause"))
                elif event.ui_object_id == "#tracstar.#op-vol+btn":
                    # Volume +
                    volume = min((self.mixer.get_volume() + 0.1), 1.0)
                    self.mixer.set_volume(value=volume)
                elif event.ui_object_id == "#tracstar.#op-vol-btn":
                    # Volume -
                    volume = max((self.mixer.get_volume() - 0.1), 0.0)
                    self.mixer.set_volume(value=volume)
                elif event.ui_object_id == "#tracstar.#op-nextbtn":
                    # search the pygame_gui selection list for the highlighted song
                    index_selected_track = next((index for index,track in enumerate(self.music_list.item_list) if track.get('selected') is True), None)
                    if index_selected_track is not None:
                        selected_track = self.music_list.item_list[index_selected_track]
                        print('Selected song is: ')
                        print(selected_track)
                        print('Index of it is  : ' + str(index_selected_track))
                        if (index_selected_track + 1) >= len(self.music_list.item_list):
                            print('DEBUG: Wrapping around to beginning.')
                            next_track_index = 0
                        elif (index_selected_track + 1) < len(self.sorted_dict):
                            print('DEBUG: Parameter within list length.')
                            next_track_index = index_selected_track + 1
                        print('next track index:')
                        print(next_track_index)
                        next_track_key = self.sorted_dict.get(next_track_index)  # sorted_dict : GUI view
                        print('next track key')
                        print(next_track_key)
                        next_track_title = self.music_dict[next_track_key]['title']  # music_dict: model, source of truth
                        print('next track title')
                        print(next_track_title)

                        self.music_list.set_item_list([])
                        # Populate GUI playlist with all detected files.
                        print('DEBUG: Populating GUI playlist.')
                        for index,key in self.sorted_dict.items():
                            title = self.music_dict[key]['title']
                            oid = str(f'{key}')
                            self.music_list.add_items([(title,oid)])
                        # Set default selection to next item.
                        self.music_list._default_selection = (str(next_track_title),str(next_track_key))
                        print('single selection:')
                        print(self.music_list.get_single_selection())
                        self.music_list._set_default_selection()

                    else:
                        print('No track is selected.')

                    if self.playing_track is not None:
                        last_played = self.playing_track
                        if self.mixer.get_busy() is True:
                            self.mixer.stop()
                            # music list, identify current playing track
                            for sort_number,key in self.sorted_dict.items():
                                if last_played == key:
                                    if sort_number+1 == len(self.sorted_dict.items()):
                                        next_track_index = 0
                                    elif sort_number+1 < len(self.sorted_dict.items()):
                                        next_track_index = sort_number+1
                            for sort_number,key in self.sorted_dict.items():
                                if next_track_index == sort_number:
                                    play_next = key
                            self.mixer.load(play_next)
                            # music list, go to next item in list
                            self.mixer.play()
                        selected_track = self.music_list.get_single_selection()
                        # Is a track selected in the playlist?
                    if selected_track is None:
                        pass
                    else:
                        for t in self.music_list._raw_item_list:
                            if t[0] == selected_track:
                                music_path = str(t[1])
                elif event.ui_object_id == "#tracstar.#op-lastbtn":
                    # TODO: Add last-track function once next-track works.
                    raise NotImplementedError
                return True

    def update(self, delta):
        super().update(delta)
        # limit frame rate to 4 FPS
        if time.time() - self.last_time > 0.1: #0.25:
            #if self.animate_magbar is True:
            if self.mixer.get_busy() == True:
                if 0 <= self.animation_magbar_counter < self.animation_magbar_max:
                    self.surface_magbar.blit(self.animation_magbar_frames[self.animation_magbar_counter], (0, 0))
                    self.animation_magbar_counter += 1
                else:
                    self.animation_magbar_counter = 0
                self.magbar.set_image(self.surface_magbar_white)
                self.magbar.set_image(self.surface_magbar)
                self.last_time = time.time()

    def kill(self):
        self.mixer.stop()
        super().kill()
