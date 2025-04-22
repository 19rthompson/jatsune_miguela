import PySimpleGUI as sg
from pathlib import Path
from pydub import AudioSegment
import simpleaudio as sa

# === Replace this with your real synthesis function ===
def synthesize(text, midi_path, output_path="output.wav"):
    print(f"Synthesizing: '{text}' to {output_path} with MIDI: {midi_path}")
    # This is where you'd call your actual pipeline.
    # For now, generate a short dummy sine wave sound.
    tone = AudioSegment.silent(duration=500) + AudioSegment.sine(440, duration=1000)
    tone.export(output_path, format="wav")
    return output_path

def play_audio(filepath):
    sound = AudioSegment.from_file(filepath)
    playback = sa.play_buffer(
        sound.raw_data,
        num_channels=sound.channels,
        bytes_per_sample=sound.sample_width,
        sample_rate=sound.frame_rate
    )
    playback.wait_done()

# === GUI Layout ===
layout = [
    [sg.Text("Enter lyrics:"), sg.InputText(key="TEXT")],
    [sg.Text("Select MIDI file:"), sg.Input(key="MIDI"), sg.FileBrowse(file_types=(("MIDI Files", "*.mid"),))],
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
        if not text.strip():
            sg.popup_error("Please enter lyrics.")
            continue
        if not Path(midi_file).exists():
            sg.popup_error("Please select a valid MIDI file.")
            continue

        output_path = "hatsune_miguela_output.wav"
        window["STATUS"].update("Synthesizing...")
        window.refresh()

        try:
            result_path = synthesize(text, midi_file, output_path)
            window["STATUS"].update("Playback starting...")
            play_audio(result_path)
            window["STATUS"].update(f"Done! Audio saved to {result_path}")
        except Exception as e:
            window["STATUS"].update("An error occurred.")
            sg.popup_error(f"Error: {e}")

window.close()
