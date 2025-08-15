#!/usr/bin/env python3

import subprocess
import os
import sys
import random
import glob

def get_available_wallpapers():
    """Get list of configured wallpapers"""
    configs_dir = os.path.expanduser("~/Scripts/wallpaper_configs")
    if not os.path.exists(configs_dir):
        return []
    
    configs = glob.glob(os.path.join(configs_dir, "*.plist"))
    return [os.path.splitext(os.path.basename(config))[0] for config in configs]

def add_wallpaper_config(name):
    """Add a new wallpaper configuration"""
    configs_dir = os.path.expanduser("~/Scripts/wallpaper_configs")
    os.makedirs(configs_dir, exist_ok=True)
    
    try:
        index_path = find_wallpaper_store()
    except FileNotFoundError as e:
        print(f"error: {e}")
        return False
    
    print(f"setting up wallpaper config: {name}")
    print(f"1. manually switch to your desired wallpaper in system preferences")
    input("press enter when done...")
    
    config_path = os.path.join(configs_dir, f"{name}.plist")
    subprocess.run(['cp', index_path, config_path], check=True)
    print(f"saved {name} config to {config_path}")
    return True

def setup_wallpaper_configs():
    """Interactive setup for multiple wallpapers"""
    print("wallpaper setup - add as many as you want")
    print("ctrl+c to finish\n")
    
    try:
        while True:
            name = input("wallpaper name (or ctrl+c to finish): ").strip()
            if not name:
                continue
            if not add_wallpaper_config(name):
                break
            print()
    except KeyboardInterrupt:
        print("\nsetup complete!")

def find_wallpaper_store():
    """Find the wallpaper store, even if apple moves it"""
    possible_paths = [
        "~/Library/Application Support/com.apple.wallpaper/Store/Index.plist",
        "~/Library/Wallpaper/Store/Index.plist",
        "~/Library/Preferences/com.apple.wallpaper/Index.plist"
    ]
    
    for path in possible_paths:
        full_path = os.path.expanduser(path)
        if os.path.exists(full_path):
            return full_path
    
    # last resort: search for it
    search_patterns = [
        "~/Library/**/wallpaper/**/Index.plist",
        "~/Library/**/Index.plist"
    ]
    
    for pattern in search_patterns:
        matches = glob.glob(os.path.expanduser(pattern), recursive=True)
        for match in matches:
            try:
                with open(match, 'rb') as f:
                    if b'wallpaper.choice' in f.read():
                        return match
            except:
                continue
    
    raise FileNotFoundError("couldn't find wallpaper store - apple may have changed the location")

def switch_wallpaper(wallpaper_name):
    """Switch wallpaper by copying the appropriate config"""
    configs_dir = os.path.expanduser("~/Scripts/wallpaper_configs")
    config_file = os.path.join(configs_dir, f"{wallpaper_name}.plist")
    
    try:
        index_path = find_wallpaper_store()
    except FileNotFoundError as e:
        print(f"error: {e}")
        return False
    
    if not os.path.exists(config_file):
        print(f"config not found: {wallpaper_name}")
        available = get_available_wallpapers()
        if available:
            print(f"available: {', '.join(available)}")
        else:
            print("no wallpaper configs found - run with --setup")
        return False
    
    try:
        # backup current config
        backup_path = f"{index_path}.backup"
        subprocess.run(['cp', index_path, backup_path], check=True)
        
        # copy the config
        subprocess.run(['cp', config_file, index_path], check=True)
        
        # restart wallpaper agent
        restart_wallpaper_agent()
        
        print(f"wallpaper changed to: {wallpaper_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"failed to change wallpaper: {e}")
        return False
    except Exception as e:
        print(f"error: {e}")
        return False

def restart_wallpaper_agent():
    """Try multiple methods to restart the wallpaper agent"""
    user_id = os.getuid()
    
    methods = [
        ['launchctl', 'kickstart', '-k', f'gui/{user_id}/com.apple.wallpaper.agent'],
        ['launchctl', 'kill', 'SIGTERM', f'gui/{user_id}/com.apple.wallpaper.agent'],
        ['killall', 'WallpaperAgent']
    ]
    
    for method in methods:
        try:
            subprocess.run(method, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            continue
    
    print("warning: couldn't restart wallpaper agent, changes might not take effect immediately")
    return False

def show_usage():
    """Show usage information"""
    available = get_available_wallpapers()
    
    print("usage:")
    print("  wallpaper.py [wallpaper_name]  # switch to wallpaper (random if no name)")
    print("  wallpaper.py --setup           # add wallpaper configurations")
    print("  wallpaper.py --add <name>      # add single wallpaper config")
    print("  wallpaper.py --list            # show available wallpapers")
    print("  wallpaper.py --help            # show this help")
    
    if available:
        print(f"\navailable wallpapers: {', '.join(available)}")
    else:
        print("\nno wallpaper configs found - run --setup first")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--setup":
            setup_wallpaper_configs()
        elif arg == "--add" and len(sys.argv) > 2:
            add_wallpaper_config(sys.argv[2])
        elif arg == "--list":
            available = get_available_wallpapers()
            if available:
                print('\n'.join(available))
            else:
                print("no wallpaper configs found - run --setup first")
        elif arg in ["--help", "-h"]:
            show_usage()
        else:
            # try to switch to this wallpaper
            switch_wallpaper(sys.argv[1])
    else:
        # random choice
        available = get_available_wallpapers()
        if available:
            wallpaper = random.choice(available)
            switch_wallpaper(wallpaper)
        else:
            print("no wallpaper configs found - run --setup first")
            show_usage()
