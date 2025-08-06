#!/usr/bin/env python3
import os
import re
from collections import defaultdict

def get_character_game(folder_name):
    # Remove skin if present
    base_name = folder_name.split('$')[0]
    match = re.match(r'([^\.]+)\.([^\.]+)', base_name)
    if match:
        return match.group(1), match.group(2)
    return base_name, ''

def scan_hurt(base_path):
    hurt_path = os.path.join(base_path, 'hurt')
    if not os.path.isdir(hurt_path):
        return []
    return [d for d in os.listdir(hurt_path) if os.path.isdir(os.path.join(hurt_path, d))]

def scan_voice(base_path):
    voice_path = os.path.join(base_path, 'voice')
    if not os.path.isdir(voice_path):
        return []
    return [d for d in os.listdir(voice_path) if os.path.isdir(os.path.join(voice_path, d))]

def scan_pld(base_path, game_folder):
    result = []
    for pld in ['pld0', 'pld1']:
        pld_path = os.path.join(base_path, game_folder, pld)
        if os.path.isdir(pld_path):
            result.extend([d for d in os.listdir(pld_path) if os.path.isdir(os.path.join(pld_path, d))])
    return result

def scan_all_characters(base_path):
    char_games = defaultdict(set)  # character.game$skin -> set of games present
    char_voice_count = defaultdict(int)  # character.game -> voice count (shared across skins)
    char_hurt_count = defaultdict(int)  # character.game -> hurt file count (shared across skins)
    char_game_folder = {}  # character.game$skin -> game
    all_folders = set()
    # Hurt
    for folder in scan_hurt(base_path):
        base_folder = folder.split('$')[0]
        char, game = get_character_game(base_folder)
        all_folders.add(folder)
        char_game_folder[folder] = game
        hurt_path = os.path.join(base_path, 'hurt', folder)
        char_hurt_count[base_folder] += len([f for f in os.listdir(hurt_path) if os.path.isfile(os.path.join(hurt_path, f))])
    # Voice
    for folder in scan_voice(base_path):
        base_folder = folder.split('$')[0]
        char, game = get_character_game(base_folder)
        voice_path = os.path.join(base_path, 'voice', folder)
        char_voice_count[base_folder] += len([f for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))])
        all_folders.add(folder)
        char_game_folder[folder] = game
    # re1, re2, re3, recv
    for game_folder in ['re1', 're2', 're3', 'recv']:
        for folder in scan_pld(base_path, game_folder):
            all_folders.add(folder)
            char, game = get_character_game(folder)
            char_game_folder[folder] = game
    # Now, for each character.game$skin, find which games (re1, re2, re3, recv) it exists in
    for folder in all_folders:
        for game_folder in ['re1', 're2', 're3', 'recv']:
            pld_folders = scan_pld(base_path, game_folder)
            if folder in pld_folders:
                char_games[folder].add(game_folder)
    return char_games, char_voice_count, char_hurt_count, char_game_folder, all_folders

def main():
    base_path = 'data'
    char_games, char_voice_count, char_hurt_count, char_game_folder, all_folders = scan_all_characters(base_path)
    # Prepare rows
    rows_in_games = []
    rows_not_in_games = []
    for folder in all_folders:
        char, game = get_character_game(folder)
        games_present = char_games.get(folder, set())
        base_folder = folder.split('$')[0]
        voice_count = char_voice_count.get(base_folder, 0)
        base_folder = folder.split('$')[0]
        hurt_count = char_hurt_count.get(base_folder, 0)
        row = (char, game, folder, voice_count, hurt_count, games_present)
        if any(g in games_present for g in ['re1','re2','re3','recv']):
            rows_in_games.append(row)
        else:
            rows_not_in_games.append(row)
    def sort_key(row):
        char, game, _, _, _, _ = row
        return (char if game else 'zzzzzz', game)
    rows_in_games.sort(key=sort_key)
    rows_not_in_games.sort(key=sort_key)
    # Build markdown
    with open('STATS.md', 'w', encoding='utf-8') as f:
        f.write('# Playable Characters\n')
        f.write('| Character Name | Game | Skin | Voice File Count | Hurt File Count | re1 | re2 | re3 | recv |\n')
        f.write('|---|---|---|---|---|---|---|---|---|\n')
        for char, game, folder, voice_count, hurt_count, games_present in rows_in_games:
            skin = ''
            if '$' in folder:
                skin = folder.split('$',1)[1]
            def tick(g): return '✅' if g in games_present else ''
            f.write(f'| {char} | {game} | {skin} | {voice_count} | {hurt_count} | {tick("re1")} | {tick("re2")} | {tick("re3")} | {tick("recv")} |\n')
        f.write('\n# Voice only\n')
        f.write('| Character Name | Game | Skin | Voice File Count | Hurt File Count | re1 | re2 | re3 | recv |\n')
        f.write('|---|---|---|---|---|---|---|---|---|\n')
        for char, game, folder, voice_count, hurt_count, games_present in rows_not_in_games:
            skin = ''
            if '$' in folder:
                skin = folder.split('$',1)[1]
            def tick(g): return '✅' if g in games_present else ''
            f.write(f'| {char} | {game} | {skin} | {voice_count} | {hurt_count} | {tick("re1")} | {tick("re2")} | {tick("re3")} | {tick("recv")} |\n')

if __name__ == '__main__':
    main()
