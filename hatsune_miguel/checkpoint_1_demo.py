from syltippy import syllabize
import epitran

def prepare(text):
    return text.replace(", "," , ").replace(". "," . ").replace("? "," ? ").split()

def toPhonemes(text):
    text = prepare(text)

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
        ipa=epi.transliterate(syl[0])
        ipa_text.append([ipa,syl[1]])
    return ipa_text


helloWorld = "Hola, mundo"
lorumIpsum = """este es el texto que vamos a poner en sílabas."""

helloWorldPhonemes = toPhonemes(helloWorld)
lorumIpsumPhonemes = toPhonemes(lorumIpsum)


print("Hello world Syllables and Stress:")
for syl in helloWorldPhonemes:
    print(syl[0],syl[1])


print("\nLorum Ipsum Syllables:")
for syl in lorumIpsumPhonemes:
    print(syl[0],end=' ')
print()