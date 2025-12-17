import crepe
import argparse
from scipy.io import wavfile
import pandas as pd
import os
def get_f0(dir, output, fpath):
    path = os.path.join(dir, fpath)
    
    sr, audio = wavfile.read(path)
    time, frequency, confidence, _ = crepe.predict(audio, sr, viterbi=True, step_size=32)
    df = pd.DataFrame({'time': time,
                   'frequency': frequency,
                   'confidence': confidence})
    os.makedirs('f0/'+output, exist_ok=True)
    df.to_csv('f0/{}/{}.f0.csv'.format(output, fpath.split('.')[0]), index=False) 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src_dir', type=str, help="path to audio input")
    parser.add_argument('--output', type=str, help="path to f0 output")
    a = parser.parse_args()
    src_dir = a.src_dir
    output = a.output
    synth_files = [file for file in os.listdir(src_dir) if file.endswith('.wav')]
    for f in synth_files:
        get_f0(src_dir, output, f)
