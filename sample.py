import heapq

from matplotlib.pyplot import imshow
from mido import Message, MidiFile, MidiTrack
from PIL import Image

import numpy as np

from my_midi import load_from_midi, SUBDIVISIONS, LOWEST_MIDI_NOTE, TICKS_PER_BEAT

def plays_at_to_offset_length(array):
    out = []
    last = None
    for val in array:
        if last is None:
            offset = val
            length = 1
        elif val - 1 == last:
            length += 1
        else:
            out.append((offset, length))
            offset = val
            length = 1
        last = val
    out.append((offset, length))
    return out

class Sample:
    def __init__(self, data):
        self.data = data
    
    def save_image(self, name="out.jpg"):
        img = Image.fromarray(255 - self.data * 255)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img.convert('RGB').save(name)
    
    def show_image(self):
        #%matplotlib inline
        imshow(self.data * 255, cmap='Greys',  interpolation='none',aspect="auto", origin="lower")
        
    def save_midi(self, filename="out.midi", thresh=0.5):
        notes = []
        for pitch in range(self.data.shape[0]):
            if (self.data[pitch] >= thresh).any():
                plays_at = np.where(self.data[pitch] >= thresh)[0]
                notes.extend(map(lambda x: (pitch + LOWEST_MIDI_NOTE, (int(round(x[0] * TICKS_PER_BEAT / SUBDIVISIONS)), int(round(x[1] * TICKS_PER_BEAT / SUBDIVISIONS)))), plays_at_to_offset_length(plays_at)))
        
        notes.sort(key=lambda x: x[1])

        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        
        last_time = 0
        note_offs = []
        for note, (offset, length) in notes:
            if len(note_offs) > 0:
                while note_offs[0][0] < offset:
                    t, n = heapq.heappop(note_offs)
                    track.append(Message("note_off", note=n, velocity=100, time=t-last_time))
                    last_time = t
                    if len(note_offs) == 0:
                        break
            track.append(Message("note_on", note=note, velocity=100, time=offset-last_time))
            heapq.heappush(note_offs, (offset + length, note))
            last_time = offset

        while len(note_offs) > 0:
            time, note = heapq.heappop(note_offs)
            track.append(Message("note_off", note=note, velocity=100, time=time-last_time))
            last_time = time

        mid.save(filename)
    
    @staticmethod
    def from_midi(file_path):
        return Sample(load_from_midi(file_path))
    
    @staticmethod
    def from_image(file_path):
        img = Image.open(file_path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        return Sample(1 - np.array(img)[:,:,0] / 255)
        