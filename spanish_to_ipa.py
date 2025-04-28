class Phoneme:
    def __init__(self,char):
        self.char = char
        self.emphasis = False

def have_common_char(str1, str2):
  """Checks if two strings have any character in common.

  Args:
    str1: The first string.
    str2: The second string.

  Returns:
    True if the strings have at least one common character, False otherwise.
  """

  # Convert strings to sets for efficient membership testing
  set1 = set(str1)
  set2 = set(str2)

  # Check for intersection between the sets
  return bool(set1 & set2)

def accent(char):
    if char.upper() == "A":
        return "Á"
    if char.upper() == "E":
        return "É"
    if char.upper() == "I":
        return "Í"
    if char.upper() == "O":
        return "Ó"
    if char.upper() == "U":
        return "Ú"

def add_emphasis(text):
    text=text.split()

    for word in text:
        if have_common_char("ÁÉÍÓÚ",text.upper()):
            continue
        index = -1
        if word[index] in [",."]:
            index = -2
        
        if word[index].upper() in "AEIOUSN":
            pass
                

def text_to_ipa(text):
    text += " "
    text = text + " "
    
    ipa_string = []


    index = 0
    #process all characters into a list of phoneme objects, only worries about emphasis for accented vowels
    for char in text:
        
        char = char.upper()
        phoneme = ""

        #procesar los vocales con sus enfasises raros
        if char == 'A':
            phoneme = Phoneme("a")
        if char == 'Á':
            phoneme = Phoneme("a")
            phoneme.emphasis = True
        if char == 'E':
            phoneme = Phoneme("e")
        if char == 'É':
            phoneme = Phoneme("e")
            phoneme.emphasis = True
        if char == 'O':
            phoneme = Phoneme("o")
        if char == 'Ó':
            phoneme = Phoneme("o")
            phoneme.emphasis = True
        if char == 'I':
            if index < (len(text)-1) and text[index+1].upper() in "AEOU":
                phoneme = Phoneme("j")
            else: phoneme = Phoneme("i")
        if char == 'Í':
            phoneme = Phoneme("i")
            phoneme.emphasis = True
        if char == 'U':
            if text[index-1].upper() != "G":
                if text[index+1].upper() in "AEOI":
                    phoneme = Phoneme("w")
                else: phoneme = Phoneme("u")
        if char in 'Ú':
            phoneme = Phoneme("u")
            phoneme.emphasis = True
        if char in "Ü":
            phoneme = Phoneme("w")
        

        #process the consonants

        #petaka
        if char == 'P':
            phoneme = Phoneme("p")
        if char == 'T':
            phoneme = Phoneme("t")
        if char == 'K':
            phoneme = Phoneme("k")


        #bodega
        if char in 'BV':
            if index == 0 or (index>1 and text[index-2] in ",."):
                phoneme = Phoneme("b")
            elif text[index-1].upper() in "MNÑ":
                phoneme = Phoneme("b")
            elif text[index-1]==" "and text[index-2].upper() in "MNÑ":
                phoneme = Phoneme("b")
            else: phoneme = Phoneme("β")
        if char == 'D':
            if index == 0 or (index>1 and text[index-2] in ",."):
                phoneme = Phoneme("d")
            elif text[index-1].upper() in "MNÑL":
                phoneme = Phoneme("d")
            elif text[index-1]==" "and text[index-2].upper() in "MNÑL":
                phoneme = Phoneme("d")
            else: phoneme = Phoneme("ð̞")
        if char == 'G':
            if index == 0 or (index>1 and text[index-2] in ",. "):
                phoneme = Phoneme("g")
            elif text[index-1].upper() in "MNÑ":
                phoneme = Phoneme("g")
            elif text[index-1]==" "and text[index-2].upper() in "MNÑ":
                phoneme = Phoneme("g")
            else: phoneme = Phoneme("ɣ")
        #c y ch
        if char == "C":
            if text[index+1].upper() in "EI":
                phoneme = Phoneme("s")
            elif text[index+1].upper() == "H":
                phoneme = Phoneme("tʃ")
            else:
                phoneme = Phoneme("k")

        if char == "F":
            phoneme = Phoneme("f")
        if char == "J":
            phoneme = Phoneme("x")
        if char == "L":
            if text[index+1].upper() == "L":

                phoneme = Phoneme("ʎ")
            elif text[index-1].upper() == "L":
                pass
            else:
                phoneme = Phoneme("l")
        if char == "M":
            phoneme = Phoneme("m")

        if char == "Ñ":
            phoneme = Phoneme("ɲ")

        if char == "N":
            if text[index+1].upper() == "F":
                phoneme = Phoneme("ɱ")
            if text[index+1].upper() in "TD":
                phoneme = Phoneme("n̪")
            if text[index+1].upper() in "GJK":
                phoneme = Phoneme("ŋ")
            if text[index+1].upper() in "BV":
                phoneme = Phoneme("m")
            phoneme = Phoneme("n")

        if char == "Q":
            phoneme = Phoneme("k")
        
        if char == "R":
            if text[index-1].upper() in " R":
                phoneme = Phoneme("r")
            elif text[index+1].upper() == "R":
                phoneme = ""
            else: phoneme = Phoneme("ɾ")

        if char == "S":
            phoneme = Phoneme("s")

        if char == "W":
            phoneme = Phoneme("w")

        if char == "x":
            ipa_string.append(Phoneme("k"))
            phoneme = Phoneme("s")

        if char == "Y":
            if text[index+1] != ' ':
                phoneme = Phoneme("ʝ")
            else:
                phoneme = Phoneme("i")


        if char == "Z":
            phoneme = "s"



        #process spaces and punctuation




        if phoneme: ipa_string.append(phoneme)
        #if phoneme: print(phoneme.char)
        index+=1

    return ipa_string

def print_ipa_from_phonemes(phoneme_list):
    for char in phoneme_list:
        print(char.char, end="")
    print()


text = input("¿De cual texto quieres la transcripsión? : ")
print("La transcripsión de IPA:")
print_ipa_from_phonemes(text_to_ipa(text))
    
