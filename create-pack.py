import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def get_character_game(folder_name):
    base_name = folder_name.split('$')[0]
    parts = base_name.split('.')
    if len(parts) == 2:
        return parts[0], parts[1]
    return base_name, ''

def collect_content(data_dir, games):
    selected = set()
    # Hurt
    hurt_path = os.path.join(data_dir, 'hurt')
    if os.path.isdir(hurt_path):
        for folder in os.listdir(hurt_path):
            char, game = get_character_game(folder)
            if game in games:
                selected.add(('hurt', folder))
    # Voice
    voice_path = os.path.join(data_dir, 'voice')
    if os.path.isdir(voice_path):
        for folder in os.listdir(voice_path):
            char, game = get_character_game(folder)
            if game in games:
                selected.add(('voice', folder))
    # BGM
    bgm_path = os.path.join(data_dir, 'bgm')
    if os.path.isdir(bgm_path):
        for folder in os.listdir(bgm_path):
            game_name = folder.split('_')[0]
            if game_name in games:
                selected.add(('bgm', folder))
    # re1, re2, re3, recv
    for game_folder in ['re1', 're2', 're3', 'recv']:
        # pld0, pld1
        for pld in ['pld0', 'pld1']:
            pld_path = os.path.join(data_dir, game_folder, pld)
            if os.path.isdir(pld_path):
                for folder in os.listdir(pld_path):
                    char, game = get_character_game(folder)
                    if game in games:
                        selected.add((os.path.join(game_folder, pld), folder))
        # emd
        emd_path = os.path.join(data_dir, game_folder, 'emd')
        if os.path.isdir(emd_path):
            for folder in os.listdir(emd_path):
                char, game = get_character_game(folder)
                if game in games:
                    selected.add((os.path.join(game_folder, 'emd'), folder))
    return selected

def collect_misc_content(data_dir):
    # Everything not in a game
    misc = set()
    # Hurt
    hurt_path = os.path.join(data_dir, 'hurt')
    if os.path.isdir(hurt_path):
        for folder in os.listdir(hurt_path):
            char, game = get_character_game(folder)
            if not game:
                misc.add(('hurt', folder))
    # Voice
    voice_path = os.path.join(data_dir, 'voice')
    if os.path.isdir(voice_path):
        for folder in os.listdir(voice_path):
            char, game = get_character_game(folder)
            if not game:
                misc.add(('voice', folder))
    # emd (top-level only, not in game folders)
    emd_path = os.path.join(data_dir, 'emd')
    if os.path.isdir(emd_path):
        for folder in os.listdir(emd_path):
            char, game = get_character_game(folder)
            if not game:
                misc.add(('emd', folder))
    # title folder (all contents)
    title_path = os.path.join(data_dir, 'title')
    if os.path.isdir(title_path):
        misc.add(('title', ''))  # '' means copy whole folder
    return misc

def copy_selected(data_dir, pack_dir, selected):
    for subdir, folder in selected:
        if subdir == 'title' and folder == '':
            src = os.path.join(data_dir, 'title')
            dst = os.path.join(pack_dir, 'data', 'title')
            if os.path.isdir(src):
                shutil.copytree(src, dst)
        else:
            src = os.path.join(data_dir, subdir, folder)
            dst = os.path.join(pack_dir, 'data', subdir, folder)
            if os.path.isdir(src):
                shutil.copytree(src, dst)

def zip_pack(pack_dir, pack_name):
    zip_path = os.path.abspath(os.path.join('datapacks', f'{pack_name}.zip'))
    # Zip all files/folders found in pack_dir
    files_to_zip = [f for f in os.listdir(pack_dir)]
    if sys.platform == 'win32':
        seven_zip = shutil.which('7z') or 'C:\Program Files\7-Zip\7z.exe'
        subprocess.run([seven_zip, 'a', zip_path] + files_to_zip, cwd=pack_dir, check=True)
    else:
        subprocess.run(['zip', '-r', zip_path] + files_to_zip, cwd=pack_dir, check=True)
    if os.path.isdir(pack_dir):
        shutil.rmtree(pack_dir)

def main():
    if len(sys.argv) < 2:
        print('Usage: create-pack.py <pack_name> [game1 game2 ...]')
        sys.exit(1)
    pack_name = sys.argv[1]
    games = sys.argv[2:]
    data_dir = 'data'
    pack_dir = os.path.join('datapacks', pack_name)
    zip_path = os.path.abspath(os.path.join('datapacks', f'{pack_name}.zip'))
    # Delete zip file and pack_dir if they already exist
    if os.path.isfile(zip_path):
        os.remove(zip_path)
    if os.path.isdir(pack_dir):
        shutil.rmtree(pack_dir)
    os.makedirs(os.path.join(pack_dir, 'data'), exist_ok=True)
    if games:
        selected = collect_content(data_dir, games)
    else:
        selected = collect_misc_content(data_dir)
    copy_selected(data_dir, pack_dir, selected)
    # Copy LICENSE and VERSION to pack_dir (top level)
    for fname in ['LICENSE', 'VERSION']:
        src = os.path.join(os.getcwd(), fname)
        dst = os.path.join(pack_dir, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    zip_pack(pack_dir, pack_name)
    print(f"Data pack {pack_name} created at {os.path.join('datapacks', pack_name + '.zip') }.")

if __name__ == '__main__':
    main()
