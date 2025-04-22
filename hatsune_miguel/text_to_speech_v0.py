from phoneme_index import ipaToIndex, indexToIpa
import argparse
from syltippy import syllabize
import epitran
import sys
from pydub import AudioSegment
import librosa
import numpy as np
import soundfile as sf


SYL_BREAK = "this is the sylable break"

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

def diphonize(syl_list):
    """
    Returns a list of sylables.
    Each sylable is a list of diphone indexes that still need file paths added to them
    """

    for entry in syl_list:
        ipa = entry["ipa"]
        entry["diphone_indexes"] = syllIpaToIndex(ipa)
        filenames = []
        for diphone in entry["diphone_indexes"]:
            filenames.append(f"./voicebank_reg/{diphone}.wav")
        entry["filenames"] = filenames
    





def concatenate_syllables(syllables, crossfade_ms=10, output_filename="output.wav"):
    print(syllables)
    """
    Concatenates a list of syllables, where each syllable is a list of filenames.
    Crossfades phonemes within a syllable but not between syllables.

    :param syllables: List of lists of filenames (each inner list is a syllable).
    :param crossfade_ms: Duration of crossfade in milliseconds (default 10ms).
    :param output_filename: Name of the output file (default "output.wav").
    :return: None
    """
    full_audio = AudioSegment.silent(duration=0)  # Start with empty audio

    for syllable in syllables:
        if not syllable:
            continue  # Skip empty syllables

        # Load and concatenate phonemes within a syllable with crossfade
        syllable_audio = AudioSegment.from_wav(syllable["filenames"][0])  # Start with the first phoneme
        for filename in syllable["filenames"][1:]:
            next_sound = AudioSegment.from_wav(filename)
            syllable_audio = syllable_audio.append(next_sound, crossfade=crossfade_ms)

        # Add the syllable to the full audio (no crossfade between syllables)
        full_audio += syllable_audio

    # Export the final result
    full_audio.export(output_filename, format="wav")
    print(f"Concatenated audio saved as {output_filename}")


def parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0],
                                     description='Take text input from user, output wav file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('action', default='speak',
                        choices=[ "speak" ], 
                        nargs='?', help="desired action")
    parser.add_argument('--input', '-i', default="Bidi bidi bam bam", type=str, help="the text you want spoken")
    parser.add_argument('--output_filename', '-o', default = "output.wav",type = str, help = "name for the output file")

    my_args = parser.parse_args(argv[1:])
    return my_args
    
    

def main(argv):
    print("Hatsune Miguel prototype v0.0\n\n")
    my_args = parse_args(argv)
    if my_args.action == "speak":
        #Take and sanitize user text input
        userInput = sanitize_user_input(my_args.input)
        #Break user input into sylables and phonemes
        sylList = syllableize(userInput)
        #From sylables and phonemes, select list of diphones
        diphonize(sylList)
        #Concatenate list of diphones and corresponding .wav files into output .wav file
        concatenate_syllables(sylList, 150, my_args.output_filename)


if __name__ == "__main__":
    main(sys.argv)