from mido import MidiFile
import numpy as np

TICKS_PER_BEAT = 480

LOWEST_MIDI_NOTE = 21
HIGHEST_MIDI_NOTE = 108
SUBDIVISIONS = 12

# class MidiLoader:
def __init__(self, filepath, subdivisions = 12):
    pass

def parse_midi_file(mid):
    pitch_on = {}
    pitch_off = {}
    sustain_on = []
    sustain_off = []

    for i, track in enumerate(mid.tracks):
        total_time = 0
        for msg in track:
            total_time += SUBDIVISIONS * msg.time / mid.ticks_per_beat
            if msg.type == "note_on":
                if msg.channel >= 9:
                    continue
                if msg.velocity != 0:
                    # NOTE ON
                    if msg.note not in pitch_on:
                        pitch_on[msg.note] = []
                        pitch_off[msg.note] = []
                    pitch_on[msg.note].append(round(total_time))
                else:
                    # NOTE OFF
                    if msg.note not in pitch_off:
                        pitch_on[msg.note] = []
                        pitch_off[msg.note] = []
                    pitch_off[msg.note].append(round(total_time))         
            elif msg.type == "note_off":
                if msg.channel >= 9:
                    continue
                if msg.note not in pitch_off:
                    pitch_on[msg.note] = []
                    pitch_off[msg.note] = []
                pitch_off[msg.note].append(round(total_time)) 
            elif msg.type == "set_tempo":
                pass
            elif msg.type == "time_signature":
                pass
            elif msg.type == "end_of_track":
                pass
            elif msg.type == "program_change":
                pass
            elif msg.type == "control_change":
                if msg.control == 64:
                    #sustain
                    if msg.value >= 64:
                        sustain_on.append(round(total_time))
                    else:
                        sustain_off.append(round(total_time))
                elif msg.control == 67:
                    #soft pedal
                    pass
                elif msg.control == 66:
                    #sostentuto - deal with this later
#                     print(msg)
#                     assert False
                    pass
                else:
                    pass
#                 else:
#                     print(msg)
#                     assert False
            elif msg.type == "track_name":
                pass
            elif "meta" in str(msg):
                pass
            elif msg.type == "pitchwheel":
                pass
            elif msg.type == "sysex":
                pass
            elif msg.type == "aftertouch":
                pass
            else:
                print(msg)
                assert False
    sustain_off.append(round(total_time))
    for p in pitch_on:
        pitch_on[p] = sorted(pitch_on[p])
    
    for p in pitch_off:
        pitch_off[p] = sorted(pitch_off[p])
    return pitch_on, pitch_off, sustain_on, sustain_off

def sustain_start_end(sustain_on, sustain_off):
    sustaining = []
#     print(sustain_on)
#     print(sustain_off)
    off = -1
    for on in sustain_on:
        if on <= off:
            continue
#         print(sustaining, on, off)
        if len(sustain_off) == 0:
            break
        off = sustain_off.pop(0)
        while len(sustain_off) > 0 and off <= on:
            off = sustain_off.pop(0)
        sustaining.append((on, off))

    return sustaining

def off_with_sustain(off_time, sustaining):
    for sus_range in sustaining:
        if sus_range[0] > off_time:
            return off_time
        if sus_range[0] <= off_time < sus_range[1]:
            return sus_range[1]
    return off_time

def sustain_note_endings(pitch_off, sustaining):
    for pitch in pitch_off:
        for i in range(len(pitch_off[pitch])):
            pitch_off[pitch][i] = off_with_sustain(pitch_off[pitch][i], sustaining)

def pitch_on_off(pitch_on, pitch_off):
    pitches = {}

    for p in pitch_on:
        on_idx = 0
        off_idx = 0
        on_off = []
        while on_idx < len(pitch_on[p]) and off_idx < len(pitch_off[p]):
            on_time = pitch_on[p][on_idx]
            off_time = pitch_off[p][off_idx]
            if off_time < on_time:
                # There was an off command when the note was already off
                off_idx += 1
                continue

            if on_idx + 1 < len(pitch_on[p]):
                next_on_time = pitch_on[p][on_idx + 1]

                while next_on_time < off_time:
                    # The note is played again before going off
                    on_off.append((on_time, next_on_time - 1))
                    on_time = next_on_time
                    on_idx += 1
                    if on_idx + 1 >= len(pitch_on[p]):
                        break
                    next_on_time = pitch_on[p][on_idx+1]
            on_off.append((on_time, off_time))
            on_idx += 1
            off_idx += 1
        pitches[p] = on_off
    return pitches

def load_from_midi(filepath):
    mid = MidiFile(filepath)

    pitch_on, pitch_off, sustain_on, sustain_off = parse_midi_file(mid)

    sustaining = sustain_start_end(sustain_on, sustain_off)
    sustain_note_endings(pitch_off, sustaining)
#     print(pitch_on)
#     print(pitch_off)
    pitches = pitch_on_off(pitch_on, pitch_off)

    last_time = max(map(lambda x:x[-1][-1], filter(lambda x: len(x) > 0, pitches.values())))
    output = np.zeros((HIGHEST_MIDI_NOTE - LOWEST_MIDI_NOTE + 1, last_time + 1), dtype=np.int16)

    for pitch in pitches:
        for start, end in pitches[pitch]:
            output[pitch - LOWEST_MIDI_NOTE][start:start+1] = 1
            
    output = output[:,np.min(np.where(output.any(axis=0))):]
    return output
