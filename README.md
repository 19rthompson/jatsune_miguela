# Jatsune Miguela

A proof-of-concept text-to-singing-voice synthesizer based on phonetic diphone concatenation, designed for Spanish input.  
This project allows users to input Spanish lyrics and a simple MIDI melody to generate a synthetic singing voice.

---

## Features
- Accepts Spanish lyrics input
- Optional MIDI input to control pitch and timing
- Automatic syllable parsing and phoneme transcription
- Diphone-based audio synthesis with stress and pitch modulation
- Basic crossfading between diphones for smoother transitions
- Simple graphical user interface (GUI) using PySimpleGUI
- Output is a `.wav` audio file of the synthesized singing

---

## How to Use

The easiest way to get started is by running **`jatsune_miguela.py`**, which opens the graphical user interface (GUI).  
From there, you can input lyrics, select a MIDI file, and generate a synthesized song in just a few clicks.

### Basic Steps
1. Make sure you have Python 3.9+ installed.
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Required libraries include: `PySimpleGUI`, `pydub`, `librosa`, `pretty_midi`, `epitran`, `syltippy`)*
3. Run the user-friendly GUI:
    ```bash
    python3 jatsune_miguela.py
    ```
4. Enter your Spanish lyrics into the text box.
5. Optionally select a MIDI file to control pitch and duration.
6. Click "Synthesize" to generate the final `.wav` file.

---
## Notes
- **Voicebank**: Currently supports only Spanish phonemes.
- **MIDI input**: Only simple, monotonic MIDI melodies are recommended.
- **GUI**: Built using PySimpleGUI for ease of use.
- **Output file**: The synthesized song is saved as a `.wav` file.

---

## Future Improvements
- Expand voicebank for smoother phoneme transitions
- Support for other languages and phonetic systems
- Automatic alignment of lyrics to melody
- Real-time or DAW (VST) integration

---

## Acknowledgments
- Inspired by open-source phonetic resources and the field of computational linguistics.
- Thanks to Dr. Lucia Taylor (Utah Tech) for phonetics consultation.
- Libraries used: `pydub`, `librosa`, `epitran`, `pretty_midi`, `syltippy`, `PySimpleGUI`.

---