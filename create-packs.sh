#!/bin/bash
rm -rf datapacks
python create-pack.py base
python create-pack.py classic re1 re1.5 re2 re3 recv
python create-pack.py modern re4 re5 re6
python create-pack.py reboot re7 re8
python create-pack.py remakes re0 re1r re2r re3r re4r
python create-pack.py spinoffs rerev1 rerev2 resurv reuc redc reout
python create-pack.py silenthill sh1
python create-pack.py dinocrisis dc1
