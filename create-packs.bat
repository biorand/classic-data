@echo off
rd /s/q datapacks
python create-pack.py base
python create-pack.py classic re1 re1.5 re2 re3 recv cv
python create-pack.py modern re4 re5 re6
python create-pack.py reboot re7 re8
python create-pack.py remakes re0 re1r re2r re3r re4r
python create-pack.py spinoffs rev1 rev2 resurv survivor reuc redc outbreak
python create-pack.py silenthill sh sh1
python create-pack.py dinocrisis dc
