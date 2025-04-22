import librosa
import numpy as np
import soundfile as sf
import librosa


def get_pitch_at_time(audio_file, target_time):
    # Load audio file
    
    y, sr = librosa.load(audio_file, sr=None)
    
    # Extract pitch (F0) using pYIN (probabilistic Yin)
    f0, voiced_flag, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    
    # Create time axis
    times = librosa.times_like(f0, sr=sr)
    
    # Find the closest index to the target time
    idx = np.argmin(np.abs(times - target_time))
    
    # Get the pitch at that time
    pitch = f0[idx] if voiced_flag[idx] else None  # None means unvoiced (silence/no pitch)
    
    return pitch
'''
# Example usage: Check pitch at 2.5 seconds
audio_file = "./voicebank/b_a.wav"
target_time = 3  # seconds
pitch2 = get_pitch_at_time(audio_file, target_time)
pitch1 = get_pitch_at_time(audio_file, 0.009)

if pitch1 and pitch2:
    print(f"Pitch at 0 sec: {pitch1:.2f} Hz")
    print(f"Pitch at 1 sec: {pitch2:.2f} Hz")
else:
    print(f"No pitch detected at {target_time} sec (possibly silence or noise).")
'''

def make_constant_pitch(input_file, output_file, target_pitch_hz):
    # Load audio file
    y, sr = librosa.load(input_file, sr=None)

    # Extract pitch (F0) using pYIN
    f0, voiced_flag, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    # Compute the average detected pitch (ignore NaN values)
    f0_mean = np.nanmean(f0)
    
    if np.isnan(f0_mean):  # Handle case where no pitch is detected
        print("No pitch detected in the input file.")
        return
    
    # Compute the semitone shift needed to match target pitch
    n_steps = librosa.hz_to_midi(target_pitch_hz) - librosa.hz_to_midi(f0_mean)

    # Apply pitch shift correctly
    y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=n_steps)

    # Save output file
    sf.write(output_file, y_shifted, sr)
    print(f"Saved output to {output_file}")

import librosa
import numpy as np
import soundfile as sf
import scipy.signal

def make_pitch_uniform(input_file, output_file, target_pitch_hz):
    # Load audio file
    y, sr = librosa.load(input_file, sr=None)

    # Extract pitch (F0) using pYIN
    f0, voiced_flag, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    # Create time axis
    times = librosa.times_like(f0, sr=sr)

    # Replace NaN (unvoiced/silent parts) with the previous valid pitch
    valid_f0 = np.where(np.isnan(f0), np.interp(np.flatnonzero(np.isnan(f0)), np.flatnonzero(~np.isnan(f0)), f0[~np.isnan(f0)]), f0)

    # Compute the semitone shift at each time step
    pitch_shift_steps = librosa.hz_to_midi(target_pitch_hz) - librosa.hz_to_midi(valid_f0)

    # Smooth pitch shift values to reduce abrupt changes
    pitch_shift_steps = scipy.signal.medfilt(pitch_shift_steps, kernel_size=5)

    # Apply pitch shift dynamically
    y_fixed = np.zeros_like(y)

    frame_length = 1024  # Default frame size
    hop_length = 512  # Step size
    for i, step in enumerate(pitch_shift_steps):
        start = i * hop_length
        end = min(start + frame_length, len(y))
        
        # Dynamically adjust n_fft if the frame is smaller than frame_length
        n_fft = min(frame_length, end - start)

        # Apply pitch shift with adjusted n_fft
        y_fixed[start:end] += librosa.effects.pitch_shift(y[start:end], sr=sr, n_steps=step, n_fft=n_fft)

    # Save the output audio
    sf.write(output_file, y_fixed, sr)
    print(f"Saved pitch-uniform audio to {output_file}")

# Example usage: Force the entire audio to 220 Hz (A3)
#make_pitch_uniform("output.wav", "uniform.wav", target_pitch_hz=110)


# Example usage: Convert voice to a constant 220 Hz (A3)


"""for i in range(36):
    if i <= 4:
        for j in range(24):
            phoneme1 = str(i)
            phoneme2 = str(j)
            if len(phoneme1)<2:
                phoneme1 = "0"+phoneme1
            if len(phoneme2)<2:
                phoneme2 = "0"+phoneme2

            input_filename = "./voicebank_raw/"+phoneme1 + '_' + phoneme2 + '.wav'
            output_filename = "./voicebank_reg/"+phoneme1 + '_' + phoneme2 + '.wav'
            make_constant_pitch(input_filename, output_filename, target_pitch_hz=110)
    else:
        for j in range(5):
            phoneme1 = str(i)
            phoneme2 = str(j)
            if len(phoneme1)<2:
                phoneme1 = "0"+phoneme1
            if len(phoneme2)<2:
                phoneme2 = "0"+phoneme2

            input_filename = "./voicebank_raw/"+phoneme1 + '_' + phoneme2 + '.wav'
            output_filename = "./voicebank_reg/"+phoneme1 + '_' + phoneme2 + '.wav'
            make_constant_pitch(input_filename, output_filename, target_pitch_hz=110)"""

for i in range(5):
    input_filename = f"./voicebank_reg/0{i}.wav"
    output_filename = f"./voicebank_reg/0{i}.wav"
    make_constant_pitch(input_filename, output_filename, target_pitch_hz=110)


