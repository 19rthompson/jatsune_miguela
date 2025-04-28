from phoneme_index import ipaToIndex, indexToIpa
import argparse
from syltippy import syllabize
import epitran
import sys
from pydub import AudioSegment
from pydub.effects import normalize
import librosa
import numpy as np
import soundfile as sf
import tempfile
import os
import pretty_midi


def sanitize_user_input(string:str):
    output = ""
    for char in string:
        if char.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ ., ÁÉÍÓÚÜÑ":
            output+=char
    return output

def syllableize(text):
    """return a list of lists, the first value in each inner list is the string with the ipa representation of the
    sylable. The second value is a boolean value represending whether the sylable is emphasized.
    """
    text = text.replace(","," , ").replace("."," . ").replace("?"," ? ").split()

    syl_list = []
    # break each word into syllables
    # add each sylable to a list of tuples with the sylable data and emphasis markers
    for word in text:
        syllables, stress = syllabize(word)
        index=0
        for syl in syllables:
            if stress == index:
                syl_list.append((syl,True))
                
            else:
                syl_list.append((syl,False))
            index+=1


    #Take the list of sylables and emphasis and transcribe each sylable to IPA, not acocunting for allophones
    epi = epitran.Epitran('spa-Latn')

    ipa_text=[]
    for syl in syl_list:
        ipa=epi.transliterate(syl[0]).replace("w", "u").replace("j","i").replace("t͡ʃ","tʃ")
        ipa_text.append({"ipa":ipa,"emphasis":syl[1]})

    return ipa_text

def syllIpaToIndex(ipaText):
    diphones = []
    if ipaText[0] in ".,?_":
        diphones.append("_____")
    elif len(ipaText)==1 and ipaText[0] in "aeiouwj":
        number = ipaToIndex(ipaText[0])
        diphones.append(number)
    elif len(ipaText) == 2:
        if ipaText[0] in "aeiouwj" or ipaText[1] in "aeiouwj":
            
            diphones.append(ipaToIndex(ipaText[0])+'_'+ipaToIndex(ipaText[1]))
    elif len(ipaText)==3:
        
        if ipaText[1] in "aeiouwj":
            diphones.append(ipaToIndex(ipaText[0])+'_'+ipaToIndex(ipaText[1]))
            diphones.append(ipaToIndex(ipaText[1])+'_'+ipaToIndex(ipaText[2]))
        elif ipaText[0] in "aeiouwj":
            diphones.append(ipaToIndex(ipaText[0])+'_'+ipaToIndex(ipaText[1:]))
        elif ipaText[2] in "aeiouwj":
            diphones.append(ipaToIndex(ipaText[:2])+'_'+ipaToIndex(ipaText[2]))
    elif len(ipaText)==4:
        if ipaText[1] in "jw":
            if ipaText[1] == "j":
                diphones.append(ipaToIndex(ipaText[0])+'_'+ipaToIndex("i"))
                diphones.append(ipaToIndex(ipaText[2]))+'_'+ipaToIndex(ipaText[3])
            if ipaText[1] == "w":
                diphones.append(ipaToIndex(ipaText[0])+'_'+ipaToIndex("u"))
                diphones.append(ipaToIndex(ipaText[2]))+'_'+ipaToIndex(ipaText[3])
            
        else:
            if ipaText[1] in "aeiouwj" and ipaText[2] in "aeiouwj":
                diphones.append(ipaToIndex(ipaText[0])+'_'+ipaToIndex(ipaText[1]))
                diphones.append(ipaToIndex(ipaText[1])+'_'+ipaToIndex(ipaText[2]))
                diphones.append(ipaToIndex(ipaText[2])+'_'+ipaToIndex(ipaText[3]))
            elif ipaText[1] in "aeiouwj":
                diphones.append(ipaToIndex(ipaText[0])+'_'+ipaToIndex(ipaText[1]))
                diphones.append(ipaToIndex(ipaText[1])+'_'+ipaToIndex(ipaText[2:]))
            elif ipaText[2] in "aeiouwj:":
                diphones.append(ipaToIndex(ipaText[:2])+'_'+ipaToIndex(ipaText[2]))
                diphones.append(ipaToIndex(ipaText[2])+'_'+ipaToIndex(ipaText[3]))
    elif len(ipaText)==5:
        diphones.append(ipaToIndex(ipaText[:2])+'_'+ipaToIndex(ipaText[2]))
        diphones.append(ipaToIndex(ipaText[3])+'_'+ipaToIndex(ipaText[4]))
    return diphones

from pydub import AudioSegment

def diphonize(syl_list):
    """
    Returns a list of syllables, with each syllable containing audio filenames and their respective durations.
    Each syllable is a dictionary with diphone indexes and their audio filenames.
    """
    for entry in syl_list:
        ipa = entry["ipa"]
        entry["diphone_indexes"] = syllIpaToIndex(ipa)
        filenames = []
        for diphone in entry["diphone_indexes"]:
            filenames.append(f"./voicebank_reg/{diphone}.wav")
        entry["filenames"] = filenames

        # Get duration of syllable based on its audio file
        syllable_audio = AudioSegment.empty()
        for filename in entry["filenames"]:
            audio = AudioSegment.from_wav(filename)
            syllable_audio += audio  # Concatenate all diphones for this syllable
        entry["duration"] = syllable_audio.duration_seconds  # Store the syllable duration in seconds

    

def pitch_shift_and_stretch(filename, pitch_semitones=0, time_stretch=1.0):
    y, sr = librosa.load(filename, sr=None)
    if pitch_semitones != 0:
        y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_semitones)
    if time_stretch != 1.0:
        y = librosa.effects.time_stretch(y, rate=1.0 / time_stretch)

    # Write to temp WAV file to re-load with pydub
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sf.write(tmp.name, y, sr)
        temp_path = tmp.name

    return AudioSegment.from_wav(temp_path), temp_path


import librosa
import tempfile
import soundfile as sf
from pydub import AudioSegment

def pitch_shift_and_stretch_midi(filename, pitch_semitones=0, time_stretch=1.0):
    """
    Apply pitch shifting and time stretching to an audio file.
    
    :param filename: Path to the audio file
    :param pitch_semitones: Number of semitones to shift the pitch (positive or negative)
    :param time_stretch: Factor by which to stretch the audio time (1.0 means no change)
    :return: Processed audio as a PyDub AudioSegment and temporary file path
    """
    # Load audio file using librosa
    y, sr = librosa.load(filename, sr=None)
    
    
    # Apply pitch shift if necessary
    if pitch_semitones != 0:
        y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_semitones)
    
    # Apply time-stretching if necessary
    if time_stretch != 1.0:
        y = librosa.effects.time_stretch(y, rate=time_stretch)

    # Write to temporary WAV file for use with PyDub
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sf.write(tmp.name, y, sr)
        temp_path = tmp.name

    # Load the WAV file into a PyDub AudioSegment
    return AudioSegment.from_wav(temp_path), temp_path


def concatenate_syllable_dicts(syllables, crossfade_ms=10, output_filename="output.wav"):
    """
    Concatenates diphones from syllable dictionaries with effects for emphasis.
    """
    full_audio = AudioSegment.silent(duration=0)
    temp_files = []  # for cleanup

    for syllable in syllables:
        filenames = syllable.get("filenames", [])
        emphasis = syllable.get("emphasis", False)

        if not filenames:
            continue

        # Effects if emphasized
        pitch = 1 if emphasis else 0
        stretch = 1 if emphasis else .9
        gain_db = 3 if emphasis else 0

        # Process first file
        audio, tmp = pitch_shift_and_stretch(filenames[0], pitch, stretch)
        temp_files.append(tmp)
        syllable_audio = audio + gain_db

        # Process remaining diphones
        for fname in filenames[1:]:
            audio, tmp = pitch_shift_and_stretch(fname, pitch, stretch)
            temp_files.append(tmp)
            syllable_audio = syllable_audio.append(audio + gain_db, crossfade=crossfade_ms)

        # Append syllable to full output (no crossfade between syllables)
        full_audio += syllable_audio

    # Export and clean up
   
    for f in temp_files:
        os.remove(f)
    return full_audio
    print(f"Synthesized audio saved as {output_filename}")


    

def get_melody_notes(midi_path):
    pm = pretty_midi.PrettyMIDI(midi_path)

    # Find the first instrument with notes (excluding drums)
    melody = next(inst for inst in pm.instruments if not inst.is_drum)

    notes = []
    for note in melody.notes:
        notes.append({
            "pitch": note.pitch,                   # MIDI pitch (60 = middle C)
            "start": note.start,                   # start time in seconds
            "end": note.end,
            "duration": note.end - note.start
        })

    return notes



from pydub import AudioSegment
import os

def concatenate_syllable_dicts_midi(syllables, midi_notes, crossfade_ms=120, output_filename="output.wav"):
    """
    Concatenates syllables, adjusting pitch and duration based on MIDI notes.
    :param syllables: List of syllable dictionaries with filenames and pitch/duration data
    :param midi_notes: List of MIDI note dictionaries with pitch and duration
    :param crossfade_ms: Crossfade duration (in milliseconds)
    :param output_filename: The name of the output .wav file
    """
    full_audio = AudioSegment.silent(duration=0)  # Start with an empty audio segment
    temp_files = []  # Temporary files for cleanup

    for i, syllable in enumerate(syllables):
        if i >= len(midi_notes):
            break  # If there are more syllables than MIDI notes, stop

        # Get corresponding MIDI note data
        midi_note = midi_notes[i]
        pitch = midi_note["pitch"]
        duration = midi_note["duration"]

        # Adjust pitch and duration for each syllable
        pitch_shift_amount = pitch - 60  # Middle C (MIDI note 60) as the base
        if syllable["duration"] < midi_note["duration"]:
                # Stretch the syllable if it's shorter than the MIDI note duration
                time_stretch_factor = midi_note["duration"] / syllable["duration"]
        else:
            # Compress the syllable if it's longer than the MIDI note duration
            time_stretch_factor = syllable["duration"] / midi_note["duration"]  # Time stretch based on the MIDI note duration
        gain_db = 3 if syllable.get("emphasis", False) else 0  # Boost volume if emphasized

        # Apply pitch shifting and time-stretching to the syllable's audio
        audio, tmp = pitch_shift_and_stretch_midi(syllable["filenames"][0], pitch_semitones=pitch_shift_amount, time_stretch=time_stretch_factor)
        temp_files.append(tmp)  # Keep track of temporary files for cleanup

        # Apply volume boost for emphasized syllables
        syllable_audio = audio + gain_db

        # Concatenate additional diphones for the syllable (if any)
        for filename in syllable["filenames"][1:]:
            next_audio, tmp = pitch_shift_and_stretch(filename, pitch_semitones=pitch_shift_amount, time_stretch=time_stretch_factor)
            temp_files.append(tmp)
            syllable_audio = syllable_audio.append(next_audio + gain_db, crossfade=crossfade_ms)

        # Append the final syllable audio to the full audio
        full_audio += syllable_audio

    # Export the concatenated audio to a file
    full_audio.export(output_filename, format="wav")
    
    # Clean up temporary files
    for f in temp_files:
        os.remove(f)

    print(f"Synthesized audio saved as {output_filename}")



def get_pitch(filename):
    # Load audio file
    y, sr = librosa.load(filename)
    
    # Estimate the pitch using librosa's piptrack
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    pitches, magnitudes = librosa.core.piptrack(S=D, sr=sr)
    
    # Get the pitch with the highest magnitude (most dominant pitch)
    index = magnitudes.argmax()
    pitch_hz = pitches[index]
    pitch_semitones = librosa.hz_to_midi(pitch_hz)  # Convert to MIDI pitch
    
    return pitch_semitones






def apply_midi_to_syllables(syllables, midi_notes):
    for i, syllable in enumerate(syllables):
        if i < len(midi_notes):
            midi_note = midi_notes[i]
            syllable["pitch"] = midi_note["pitch"]
            syllable["duration"] = midi_note["duration"]

            # Get the syllable's actual audio duration
            syllable_duration = syllable["duration"]

            # Pitch adjustment relative to MIDI note (Middle C is 60)
            pitch_shift_amount = midi_note["pitch"] - 60

            # Calculate time stretch factor to match the syllable's duration to the MIDI note duration
            if syllable_duration < midi_note["duration"]:
                # Stretch the syllable if it's shorter than the MIDI note duration
                time_stretch_factor = midi_note["duration"] / syllable_duration
            else:
                # Compress the syllable if it's longer than the MIDI note duration
                time_stretch_factor = syllable_duration / midi_note["duration"]

            # Apply pitch shift and time stretch
            audio, tmp = pitch_shift_and_stretch(syllable["filenames"][0], pitch_semitones=pitch_shift_amount, time_stretch=time_stretch_factor)
            syllable["audio"] = audio  # Store processed audio for further concatenation

    return syllables











def parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0],
                                     description='Take text input from user, output wav file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('action', default='speak',
                        choices=[ "speak", "midi" ], 
                        nargs='?', help="desired action")
    parser.add_argument('--input', '-i', default="Bidi bidi bam bam", type=str, help="the text you want spoken")
    parser.add_argument('--output_filename', '-o', default = "output.wav",type = str, help = "name for the output file")
    parser.add_argument("--MIDI_filename", "-m", default = "", type = str, help = "name of MIDI file")

    my_args = parser.parse_args(argv[1:])
    return my_args
    
    

def main(argv):
    print("Hatsune Miguel prototype v0.1\n\n")
    my_args = parse_args(argv)
    if my_args.action == "speak":
        #Take and sanitize user text input
        userInput = sanitize_user_input(my_args.input)
        #Break user input into sylables and phonemes
        sylList = syllableize(userInput)
        #From sylables and phonemes, select list of diphones
        diphonize(sylList)
        #Concatenate list of diphones and corresponding .wav files into output .wav file
        concatenate_syllable_dicts(sylList, 160, my_args.output_filename)
    elif my_args.action == "midi":
        userInput = sanitize_user_input(my_args.input)
        #Break user input into sylables and phonemes
        syllables = syllableize(userInput)
        #From sylables and phonemes, select list of diphones
        diphonize(syllables)
        notes = get_melody_notes(my_args.MIDI_filename)
        syllables = apply_midi_to_syllables(syllables,notes)
        concatenate_syllable_dicts_midi(syllables,notes,150,my_args.output_filename)


if __name__ == "__main__":
    main(sys.argv)