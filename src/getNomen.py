
import array
import string
import codecs
from pathlib import Path


def getPath(name):
    return (str(Path(__file__).resolve().parent.joinpath(name)))

text_file = codecs.open(getPath("nomen.txt"), 'r', 'utf-8')
lines = text_file.readlines()
text_file.close()
lines[:] = [x.upper().rstrip("\n\r") for x in lines if len(x.strip())==5]
print ("Loaded "+str(len(lines)) + " Words.")

print (lines)
goalWord=lines[randrange(len(lines))]
