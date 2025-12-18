# Vocal2Fail
This repository is for the paper "Vocal2Fail: Controllable Timbre Transfer and Evaluation for Failed Recorder Style".  
The demo page is available at [here](https://manchenlee.github.io/vocal2fail).  

## Datasets  

Our FR109-plus dataset is divided into two subsets: 
- consistent set (FR109 dataset)  
- inconsistent set (addtional segments)

The consistent set can be downloaded from [Zenodo](https://zenodo.org/records/14250703"), while the inconsistent set is available at [Google drive](https://drive.google.com/file/d/1q0yOEa77r8Ylol38bkkbutd6gdNzHhsn/view?usp=sharing).  

Additionally, for the QbSH-based evaluation, we manually transcribed the main melodies of all 20 songs in NUS48E as targets. The corresponding 20 MIDI files can be downloaded from [here](https://drive.google.com/file/d/1tgjfFxTjAmmUEGoTKGprhCg9FN8vE-Hs/view?usp=sharing).  

## Models

We adopt the [VAE-GAN](https://github.com/RussellSB/tt-vae-gan) framework proposed by Bonnici et al..  
Both the generator and discriminator were optimized using the Adam optimizer with a learning rate of $\eta = 10^{-4}$. The model was trained for 100 epochs with a batch size of 4.

## Usage

After training, please use [**CREPE**](https://github.com/marl/crepe) to extract the F0 from both the generated audio and the source audio (NUS48E).
```
python get_f0.py --src_dir [path/to/wav] --output [path/to/output/f0]
```

**Objective Metrics**  

This code computes **Pitch Class L1**, **DTW distance** and **HNR**.  
The DTW distance is computed in the pitch domain. We employed Type II (d) from the Rabiner-Myers step patterns for the DTW computation.  
As for FAD, We utilized the pre-trained **VGGish** model as the feature extractor. The test set of FR109-plus was used as the reference for real audio.
```
python evaluate.py --exp [expname] --src_dir [path/to/source/f0] --gen_dir [path/to/gen/f0] --wav_dir [path/to/gen/wav]
```
**QbSH Evaluation**  

The QbSH system uses a database consisting of MIDI files.  
First, convert the MIDI files into pitch vectors (`.npy`):  
```
python midi2pv.py --midi_dir [path/to/midi] --pv_dir [path/to/output/pv]
```
Then run QbSH evaluation:
```
python qbsh.py --exp [expname] --pv_dir [path/to/database/pv] --query_dir [path/to/query/f0]
```

