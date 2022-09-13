# holocure save transfer

import sys
from argparse import ArgumentParser
from base64 import b64decode, b64encode
from pathlib import Path

if __name__ == "__main__":
    argParser = ArgumentParser("Holocure Save transfer")
    argParser.add_argument("-o", "--oldSave", type=Path, required=True)
    argParser.add_argument("-n", "--newSave", type=Path, required=True)

    p = argParser.parse_args()

    oldSaveLoc : Path = p.oldSave
    newSaveLoc : Path = p.newSave

    if not oldSaveLoc.exists() and not newSaveLoc.exists():
        print("Couldn't find save files specified")
        sys.exit(1)

    with open(oldSaveLoc, 'rb') as ofp:
        oldSaveEncoded = ofp.readline()
    
    with open(newSaveLoc, 'rb') as nfp:
        newSaveEncoded = nfp.readline()

    newSaveDecoded = b64decode(newSaveEncoded)
    oldSaveDecoded = b64decode(oldSaveEncoded)


    oldSavelio7b = len(oldSaveDecoded) - oldSaveDecoded[::-1].find(0x7b) - 1
    newSavelio7b = len(newSaveDecoded) - newSaveDecoded[::-1].find(0x7b) - 1

    combined = newSaveDecoded[0:newSavelio7b] + oldSaveDecoded[oldSavelio7b:]

    with open("convertedsav.dat", "wb") as cfp:
        cfp.write(b64encode(combined))
