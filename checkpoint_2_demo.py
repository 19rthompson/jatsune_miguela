from pydub import AudioSegment
import librosa
import numpy as np
import soundfile as sf


"""
# List of WAV files to concatenate
wav_files = ["ba_constant.wav","na_constant.wav","na_constant.wav"]
wav_files = ["ba_constant.wav","an_constant.wav","na_constant.wav","an_constant.wav","na_constant.wav"]

# Load the first file
combined = AudioSegment.from_wav(wav_files[0])

# Append the rest of the files
for wav in wav_files[1:]:
    sound = AudioSegment.from_wav(wav)
    combined += sound  # Concatenate

# Export the final concatenated file
combined.export("output.wav", format="wav")

print("Concatenation complete. Saved as output.wav")
"""




def crossfade_audio(file_list, output_file, crossfade_duration=0.1):
    """
    Concatenates multiple audio files smoothly with a crossfade.
    
    Parameters:
        file_list (list): List of WAV file paths to concatenate.
        output_file (str): Path to save the final output.
        crossfade_duration (float): Duration (in seconds) for crossfading between files.
    """
    audio_data = []
    sample_rates = []

    # Load all files and store data
    for file in file_list:
        y, sr = librosa.load(file, sr=None)
        audio_data.append(y)
        sample_rates.append(sr)

    # Ensure all files have the same sample rate
    if len(set(sample_rates)) > 1:
        raise ValueError("All files must have the same sample rate for smooth concatenation.")

    sr = sample_rates[0]  # Use the sample rate of the first file
    crossfade_samples = int(crossfade_duration * sr)  # Convert crossfade duration to samples

    final_audio = audio_data[0]  # Start with the first file's audio

    for i in range(1, len(audio_data)):
        prev_audio = final_audio
        next_audio = audio_data[i]

        # Apply crossfade
        fade_out = np.linspace(1, 0, crossfade_samples)  # Fade-out curve
        fade_in = np.linspace(0, 1, crossfade_samples)   # Fade-in curve

        # Ensure both clips are long enough for crossfade
        min_len = min(len(prev_audio), len(next_audio))
        if min_len < crossfade_samples:
            crossfade_samples = min_len  # Adjust crossfade if needed

        prev_audio[-crossfade_samples:] *= fade_out  # Apply fade-out to the last part of previous audio
        next_audio[:crossfade_samples] *= fade_in    # Apply fade-in to the first part of next audio

        # Concatenate with overlapping crossfade
        crossfade_segment = prev_audio[-crossfade_samples:] + next_audio[:crossfade_samples]
        final_audio = np.concatenate((prev_audio[:-crossfade_samples], crossfade_segment, next_audio[crossfade_samples:]))

    # Save the final smooth audio
    sf.write(output_file, final_audio, sr)
    print(f"Saved smoothly concatenated audio to {output_file}")

# Example usage
files_to_merge = ["./voicebank_raw/05_02.wav","./voicebank_raw/06_02.wav","./voicebank_raw/05_02.wav","./voicebank_raw/06_02.wav","./voicebank_raw/05_00.wav","./voicebank_raw/00_14.wav","./voicebank_raw/05_00.wav","./voicebank_raw/00_14.wav"]

crossfade_audio(files_to_merge, "smooth_output.wav", crossfade_duration=0.1)  # 200ms crossfade

