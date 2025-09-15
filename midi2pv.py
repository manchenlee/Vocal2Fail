import argparse
import os
import glob
import mido
import numpy as np
from tqdm import tqdm
from utils import HOP_SIZE

def midi_to_pitch_vector(midi_file_path, hop_size=HOP_SIZE):
    """
    Extracts a pitch vector from a MIDI file using a specified hop size.

    Parameters:
    - midi_file_path: str, path to the MIDI file.
    - hop_size: float, time step in seconds for the pitch vector.

    Returns:
    - pitch_vector: list of active pitches (MIDI note numbers) at each time step.
    """
    mid = mido.MidiFile(midi_file_path)
    ticks_per_beat = mid.ticks_per_beat

    # Default tempo in microseconds per beat (if not specified in the file)
    tempo = 500000  # 120 BPM

    # Parse tempo changes (if present)
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
    # Calculate ticks per second
    tempo = tempo / 1000000
    # Generate time grid
    total_time = mid.length
    # Extract note-on and note-off events
    events = []
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on' or msg.type == 'note_off':
                events.append(msg)
    notes = []
    for i in range(0, len(events), 2):
        try:
            if events[i].time > 0:
                notes.append((0, events[i].time))
                notes.append((events[i].note, events[i+1].time))
            else:
                notes.append((events[i].note, events[i+1].time))
        except:
            break
    
    frame = int(total_time // hop_size)
    pv = []
    for n in notes:
        if len(pv) >= frame:
            break
        t = (n[1] / ticks_per_beat) * tempo
        num = int(t // hop_size)
        for i in range(num):
            pv.append(float(n[0]))
    return np.array(pv[:frame])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--midi_dir', type=str, help="path to midi (.mid) input")
    parser.add_argument('--pv_dir', type=str, help='path to pv (.npy) output')
    a = parser.parse_args()

    os.makedirs(a.pv_dir, exist_ok=True)

    midi = glob.glob(os.path.join(a.midi_dir, "*.mid"))
    print("--- start midi to pitch vector ---")
    for m in tqdm(midi):
        pv = midi_to_pitch_vector(m)
        pvName = os.path.basename(m)[:-4] + '.npy'
        np.save(os.path.join(a.pv_dir, pvName), pv)
    print('midi to pitch vector completed.')