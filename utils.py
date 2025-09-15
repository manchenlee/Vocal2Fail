import numpy as np

THRESHOLD = 0.85
HOP_SIZE = 0.032
DURATION = 250 # 8s = 0.032s * 250
QBSH_HOP_SIZE = 50 # 1.6s

def fill_rest(pitches, confidence):
    pitches_reduced = []
    isBegin = True
    prev = -1
    for i in range(len(pitches)):
        if confidence[i] >= THRESHOLD:
            pitches_reduced.append(pitches[i])
            if i > 0:
                isBegin = False
            prev = pitches[i]
        elif confidence[i] < THRESHOLD and not isBegin:
            pitches_reduced.append(prev)
    pitches_reduced = np.array(pitches_reduced)
    return pitches_reduced


def get_normalized_pitch(pitches, confidence=None):
    pitches_reduced = fill_rest(pitches, confidence)
    m = pitches_reduced.mean()
    for i in range(len(pitches_reduced)):
        pitches_reduced[i] = pitches_reduced[i] - m
    return pitches_reduced