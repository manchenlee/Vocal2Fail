# Vocal2Fail
This repository is for the paper "Vocal2Fail: Controllable Timbre Transfer and Evaluation for Failed Recorder Style".  
The demo page is available at [here](https://manchenlee.github.io/vocal2fail).  

## Usage

After training, please use [**CREPE**](https://github.com/marl/crepe) to extract the F0 from both the generated audio and the [source audio](https://drive.google.com/file/d/1EQ_N8Vvp3j4VHp5qZRWgLdtBIYJEsdGV/view?usp=sharing).

**Objective Metrics**  
```
python evaluate.py --exp [expname] --src_dir [path/to/source/f0] --gen_dir [path/to/gen/f0] --wav_dir [path/to/gen/wav]
```
**QbSH Evaluation**  

The QbSH system uses a database consisting of [MIDI files](https://drive.google.com/file/d/1owhCIMoHuhXfWHI2eU4UDzZPGu0Kg7Nw/view).  
First, convert the MIDI files into pitch vectors (`.npy`):  
```
python midi2pv.py --midi_dir [path/to/midi] --pv_dir [path/to/output/pv]
```
Then run QbSH evaluation:
```
python qbsh.py --exp [expname] --pv_dir [path/to/database/pv] --query_dir [path/to/query/f0]
```

