import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
import argparse

import re

def get_character_game(folder_name):
    """
    Extracts (base, skin, game) from folder_name.
    Format: BASE.GAME$SKIN or BASE$SKIN
    Examples:
        'ada.re2$common' -> ('ada', 'common', 're2')
        'chris.re1$battle' -> ('chris', 'battle', 're1')
        'ada.re2' -> ('ada', '', 're2')
        'npc$common' -> ('npc', 'common', '')
        'ada' -> ('ada', '', '')
    """
    if '$' in folder_name:
        base_part, skin = folder_name.split('$', 1)
        if '.' in base_part:
            base, game = base_part.split('.', 1)
        else:
            base = base_part
            game = ''
    else:
        skin = ''
        if '.' in folder_name:
            base, game = folder_name.split('.', 1)
        else:
            base = folder_name
            game = ''
    return base, skin, game


def collect_selected(data_dir, allowed_games):
    selected = set()
    # Hurt
    hurt_path = os.path.join(data_dir, 'hurt')
    if os.path.isdir(hurt_path):
        for folder in os.listdir(hurt_path):
            base, skin, game = get_character_game(folder)
            if (allowed_games and game in allowed_games) or (not allowed_games and not game):
                selected.add(('hurt', folder))
    # Voice
    voice_path = os.path.join(data_dir, 'voice')
    if os.path.isdir(voice_path):
        for folder in os.listdir(voice_path):
            base, skin, game = get_character_game(folder)
            if (allowed_games and game in allowed_games) or (not allowed_games and not game):
                selected.add(('voice', folder))
    # BGM
    bgm_path = os.path.join(data_dir, 'bgm')
    if os.path.isdir(bgm_path):
        for folder in os.listdir(bgm_path):
            game_name = folder.split('_')[0]
            if (allowed_games and game_name in allowed_games) or (not allowed_games and not game_name):
                selected.add(('bgm', folder))
    # re1, re2, re3, recv
    for game_folder in ['re1', 're2', 're3', 'recv']:
        # pld0, pld1
        for pld in ['pld0', 'pld1']:
            pld_path = os.path.join(data_dir, game_folder, pld)
            if os.path.isdir(pld_path):
                for folder in os.listdir(pld_path):
                    base, skin, game = get_character_game(folder)
                    if (allowed_games and game in allowed_games) or (not allowed_games and not game):
                        selected.add((os.path.join(game_folder, pld), folder))
        # emd
        emd_path = os.path.join(data_dir, game_folder, 'emd')
        if os.path.isdir(emd_path):
            for folder in os.listdir(emd_path):
                base, skin, game = get_character_game(folder)
                if (allowed_games and game in allowed_games) or (not allowed_games and not game):
                    selected.add((os.path.join(game_folder, 'emd'), folder))
    # base only
    if not allowed_games:
        # title folder (all contents)
        title_path = os.path.join(data_dir, 'title')
        if os.path.isdir(title_path):
            selected.add(('title', ''))  # '' means copy whole folder
        # re2/credits folder (all contents)
        credits_path = os.path.join(data_dir, 're2', 'credits')
        if os.path.isdir(credits_path):
            selected.add((os.path.join('re2', 'credits'), ''))  # '' means copy whole folder
    return selected

def copy_selected(data_dir, pack_dir, selected):
    for subdir, folder in selected:
        # Handle whole-folder copies for 'title' and 're2/credits'
        if (subdir == 'title' or subdir == os.path.join('re2', 'credits')) and folder == '':
            src = os.path.join(data_dir, subdir)
            dst = os.path.join(pack_dir, 'data', subdir)
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
        seven_zip = shutil.which('7z') or 'C:\\Program Files\\7-Zip\\7z.exe'
        subprocess.run([seven_zip, 'a', zip_path] + files_to_zip, cwd=pack_dir, check=True)
    else:
        subprocess.run(['zip', '-r', zip_path] + files_to_zip, cwd=pack_dir, check=True)
    if os.path.isdir(pack_dir):
        shutil.rmtree(pack_dir)

def main():
    parser = argparse.ArgumentParser(description='Create data packs from game assets.')
    parser.add_argument('pack_name', help='Name of the data pack')
    parser.add_argument('games', nargs='*', help='Games to include (if none, misc content only)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    pack_name = args.pack_name
    games = args.games
    dry_run = args.dry_run

    data_dir = 'data'
    pack_dir = os.path.join('datapacks', pack_name)
    zip_path = os.path.abspath(os.path.join('datapacks', f'{pack_name}.zip'))

    selected = collect_selected(data_dir, games)

    if dry_run:
        print(f"Dry run: Would create pack '{pack_name}' with games: {games or 'misc'}")
        print("Selected items:")
        for subdir, folder in sorted(selected):
            if folder == '':
                print(f"  Whole folder: {subdir}")
            else:
                print(f"  {subdir}/{folder}")
        print(f"Would copy LICENSE and VERSION to {pack_dir}")
        print(f"Would zip to {zip_path}")
        return

    # Delete zip file and pack_dir if they already exist
    if os.path.isfile(zip_path):
        os.remove(zip_path)
    if os.path.isdir(pack_dir):
        shutil.rmtree(pack_dir)
    os.makedirs(os.path.join(pack_dir, 'data'), exist_ok=True)

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
