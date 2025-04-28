
ipaIndex = {"00":"a",
            "01":"e",
            "02":"i",
            "03":"o",
            "04":"u",
            "05":"b",
            "06":"d",
            "07":"ɡ",
            "08":"p",
            "09":"t",
            "10":"k",
            "11":"s",
            "12":"tʃ", 
            "13":"x",
            "14":"m",
            "15":"n",
            "16":"ɲ",
            "17":"l",
            "18":"ʝ",
            "19":"ɾ",
            "20":"f",
            "21":"r",
            "22":"j",
            "23":"w",
            "24":"pl",
            "25":"pɾ",
            "26":"bl",
            "27":"bɾ",
            "28":"tɾ",
            "29":"dɾ",
            "30":"kl",
            "31":"kɾ",
            "32":"gl",
            "33":"ɡɾ",
            "34":"fl",
            "35":"fɾ",
            "__":"__"
            }

def ipaToIndex(ipa:str):
    keys = [key for key, val in ipaIndex.items() if val == ipa]
    if keys:
        return keys[0]
    return

def indexToIpa(index:str):
    return ipaIndex[index]
