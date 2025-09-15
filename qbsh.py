import argparse
import os
import glob
import json
import numpy as np
import librosa
from scipy.stats import wasserstein_distance
from tqdm import tqdm
import pandas as pd
from dtw import *
from utils import get_normalized_pitch, DURATION, QBSH_HOP_SIZE

def dtw_emd_qbsh(pv_dir, query_dir, duration=DURATION, hop_size=QBSH_HOP_SIZE):
    database = []
    database_names = glob.glob(os.path.join(pv_dir, "*.npy"))
    print('--- get database pitch ---')
    for m in tqdm(database_names):
        temp = {}
        pv = np.load(m)
        pname = os.path.basename(m)[:-4]
        temp['id'] = pname
        temp['pitch'] = pv
        database.append(temp)

    audio_names = glob.glob(os.path.join(query_dir, "*.f0.csv"))
    audio_names = audio_names[:10]
    audios = []
    print('--- get query pitch ---')
    
    total_wav = len(audio_names)
    for a in tqdm(audio_names):
        temp = {}
        df = pd.read_csv(a)
        pitches = librosa.hz_to_midi(df['frequency'])
        confidence = df['confidence']
        aname = os.path.basename(a)
        temp["id"] = aname.split('#')[1][:2]
        temp["pitch"] = get_normalized_pitch(pitches, confidence)
        audios.append(temp)
    
    top_1 = 0
    top_20 = 0
    mrr = 0.0
    
    print('--- calculate EMD/DTW score ---')
    for a in tqdm(audios): 
        temp_result_emd = []
        temp_result_score = []
        query_pv = a["pitch"]
        for g in database:
            pv = g['pitch']
            for i in range(0, len(pv), hop_size):
                if i+duration < len(pv):
                    temp_pv = pv[i:i+duration]
                elif i+duration >= len(pv):
                    if len(pv) < duration:
                        temp_pv = np.concatenate((pv, np.zeros(duration-len(pv))))
                    else:
                        temp_pv = pv[-(duration):]
                conf = [1. if temp_pv[ind] > 0 else 0. for ind in range(duration)]
                temp_pv = get_normalized_pitch(temp_pv, conf)
                emd = wasserstein_distance(temp_pv, query_pv)
                temp = {}
                temp['id'] = g['id']
                temp['pitch'] = temp_pv
                temp['emd'] = emd
                temp_result_emd.append(temp)
        survive_rate = 0.1
        num_of_survive = int(len(temp_result_emd) * survive_rate)
        arg_result_emd = sorted(temp_result_emd, key=lambda x: x['emd'])[:num_of_survive]

        for g in arg_result_emd:
            temp_pv = g['pitch']
            try:
                result = dtw(query_pv, temp_pv, step_pattern='typeIId', distance_only=True)
            except:
                result = dtw(query_pv, temp_pv, step_pattern='symmetric2', distance_only=True)
            dist = result.normalizedDistance
            score = 0.4 * g['emd'] + 0.6 * dist
            temp = {}
            temp['id'] = g['id']
            temp['score'] = score
            temp_result_score.append(temp)
        arg_result = sorted(temp_result_score, key=lambda x: x['score'])
        candidates = {}

        for item in arg_result:
            id = item['id']
            if id not in candidates or item['score'] < candidates[id]:
                candidates[id] = item['score']
        
        candidates = np.array(sorted(candidates, key=lambda x: candidates[x]))
        
        if a["id"] in candidates:
            ind = np.where(candidates == a["id"])[0][0] + 1
            mrr += (1 / ind)
        if a["id"] in candidates[:20]:
            top_20 += 1
        if a["id"] == candidates[0]:
            top_1 += 1
    return (top_1/total_wav)*100, (top_20/total_wav)*100, (mrr/total_wav)*100

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', type=str, help="exp name")
    parser.add_argument('--pv_dir', type=str, help='path to pitch vector (.npy) of database')
    parser.add_argument('--query_dir', type=str, help="path to f0 (.f0.csv) of query audio")
    a = parser.parse_args()
    result = {}
    result["top1"], result["top20"], result["mrr"] = dtw_emd_qbsh(a.pv_dir, a.query_dir)

    print('top-1: {:.2f}%'.format(result["top1"]))
    print('top-20: {:.2f}%'.format(result["top20"]))
    print('MRR: {:.2f}%'.format(result["mrr"]))

    with open(f'qbsh_{a.exp}.txt', 'w') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
    print('QbSH-based evaluation completed.')