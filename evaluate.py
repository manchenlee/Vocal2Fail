import argparse
import os
import glob
import json
import librosa
from dtw import *
import pandas as pd
import parselmouth
from tqdm import tqdm
from utils import get_normalized_pitch, THRESHOLD

def get_pitch(filename, metrics = "dtw"):
    df = pd.read_csv(filename)
    pitch = librosa.hz_to_midi(df['frequency'])
    if metrics == "dtw": 
        pitch = get_normalized_pitch(pitch, df['confidence'])
    elif metrics == "l1":
        pitch = [p - (12 * (p // 12)) for p in pitch]
    return pitch, df

def pitch_class_l1(src_files, synth_files):
    l1_total = 0.
    for i in tqdm(range(len(synth_files))):
            pitch_src, df_src = get_pitch(src_files[i], "l1")
            pitch_synth, df_synth = get_pitch(synth_files[i], "l1")
            l1 = 0.0
            count = 0
            for p in range(len(pitch_src)):
                try:
                    if df_src['confidence'][p] >= THRESHOLD and df_synth['confidence'][p] >= THRESHOLD:
                        diff = abs(pitch_src[p] - pitch_synth[p])
                        if diff > 6:
                            diff = 12 - diff
                        l1 += diff
                        count += 1
                except:
                    break
            l1 = l1 / count
            l1_total += l1
    return l1_total / len(synth_files)

def dtw_dist(src_files, synth_files):
    total_dist = 0.0
    for i in tqdm(range(len(synth_files))):
            pitch_src, _ = get_pitch(src_files[i], "dtw")
            pitch_synth, _ = get_pitch(synth_files[i], "dtw")
            try:
                result = dtw(pitch_synth, pitch_src, step_pattern='typeIId', distance_only=True)
            except:
                result = dtw(pitch_synth, pitch_src, step_pattern='symmetric2', distance_only=True)
            dist = result.normalizedDistance
            total_dist += dist
    return total_dist / len(synth_files)

def hnr(wav_files):
    sf_sum = 0.0
    sf_len = 0
    for file in tqdm(wav_files):
        s = parselmouth.Sound(file)
        s.pre_emphasize()
        hnr = s.to_harmonicity()
        result = hnr.values[hnr.values != -200].mean()
        sf_sum += result
        sf_len += 1
    return sf_sum / sf_len
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src_dir', type=str, help="path to f0 (.f0.csv) of source audio")
    parser.add_argument('--synth_dir', type=str, help='path to f0 (.f0.csv) of generated audio')
    parser.add_argument('--wav_dir', type=str, help='path to wav files of generated audio')
    parser.add_argument('--exp', type=str, default="test", help='exp name')
    a = parser.parse_args()

    src_files = glob.glob(os.path.join(a.src_dir, "*.csv"))
    synth_files = glob.glob(os.path.join(a.synth_dir, "*.csv"))
    wav_files = glob.glob(os.path.join(a.wav_dir, "*.wav"))

    assert len(src_files) == len(synth_files)
    result = {}

    print("--- calculate Pitch Class L1 ---")
    result['pitch_class_l1'] = pitch_class_l1(src_files, synth_files)
    
    print("--- calculate DTW distance ---")
    result['dtw_dist'] = dtw_dist(src_files, synth_files)
    
    print("--- calculate HNR ---")
    result['hnr'] = hnr(wav_files)

    print('Pitch Class L1: {:.2f}'.format(result['pitch_class_l1']))
    print('DTW distance: {:.2f}'.format(result['dtw_dist']))
    print('Harmonicity: {:.2f}'.format(result['hnr']))

    with open(f'objEval_{a.exp}.txt', 'w') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

    print('Objective evaluation (Pitch Class L1, DTW distance, HNR) completed.')
