import PySimpleGUI as sg
from pathlib import Path
from pydub import AudioSegment
import simpleaudio as sa
import text_to_speech_v1 as jm


def synthesizeSpeech(text, output_path="output.wav"):
    print(f"Synthesizing: '{text}' to {output_path}")
    
    #Take and sanitize user text input
    userInput = jm.sanitize_user_input(text)
    #Break user input into sylables and phonemes
    sylList = jm.syllableize(userInput)
    #From sylables and phonemes, select list of diphones
    jm.diphonize(sylList)
    #Concatenate list of diphones and corresponding .wav files into output .wav file

    # For now, generate a short dummy sine wave sound.
    tone = jm.concatenate_syllable_dicts(sylList, 160, output_path)

    tone.export("./wavs/"+output_path, format="wav")
    return output_path

def synthesizeSong(text, midi, output_path="output.wav"):
    print(f"Synthesizing: '{text}' from '{midi}' to {output_path}")
    
    userInput = jm.sanitize_user_input(text)
    #Break user input into sylables and phonemes
    syllables = jm.syllableize(userInput)
    #From sylables and phonemes, select list of diphones
    jm.diphonize(syllables)
    notes = jm.get_melody_notes(midi)
    syllables = jm.apply_midi_to_syllables(syllables,notes)
    jm.concatenate_syllable_dicts_midi(syllables,notes,150,output_path)

    return output_path


def sing(text,midi_file,output_path):
    window["STATUS"].update("Synthesizing...")
    window.refresh()

    try:
        result_path = synthesizeSong(text, midi_file, output_path)
        window["STATUS"].update("Playback starting...")
        
        window["STATUS"].update(f"Done! Audio saved to {result_path}")
    except Exception as e:
        window["STATUS"].update("An error occurred.")
        sg.popup_error(f"Error: {e}")

def speak(text, output_path="test.wav"):
    window["STATUS"].update("Synthesizing...")
    window.refresh()

    try:
        result_path = synthesizeSpeech(text, output_path)
        window["STATUS"].update("Playback starting...")
        window["STATUS"].update(f"Done! Audio saved to {result_path}")
    except Exception as e:
        window["STATUS"].update("An error occurred.")
        sg.popup_error(f"Error: {e}")

# === GUI Layout ===
layout = [
    [sg.Text("Enter lyrics:"), sg.InputText(key="TEXT")],
    [sg.Text("Select MIDI file:"), sg.Input(key="MIDI"), sg.FileBrowse(file_types=(("MIDI Files", "*.mid"),))],
    [sg.Text("Select output filename"), sg.Input(key="OUTPUT")],
    [sg.Button("Synthesize"), sg.Button("Exit")],
    [sg.Text("", key="STATUS", size=(50, 1))]
]

window = sg.Window("Hatsune Miguela Synth", layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
    elif event == "Synthesize":
        text = values["TEXT"]
        midi_file = values["MIDI"]
        output_file = values["OUTPUT"]
        if not text.strip():
            sg.popup_error("Please enter lyrics.")
            continue
        if not Path(midi_file).exists():
            sg.pop_error("Not a valid midi file.")
            continue
        if midi_file:
            sing(text,midi_file,output_file)
        else:
            speak(text,output_file)


        

window.close()
