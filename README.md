# wallpaper switcher for macos

fast (apple) wallpaper switching without fighting apple's apis.

## what this solves

changing wallpapers on macos programmatically is painful. chosing any image to be the wallpaper is easy, but being able to trigger apple made wallpapers such as macintosh or sonoma is a lot more complicated. this script sidesteps all complexity by copying working system config files.

## how it works

1. you set wallpapers manually in system preferences 
2. script saves those configs as `.plist` files
3. switching just copies the right config file over the active one
4. wallpaper agent gets restarted to apply changes

works because we're using the exact same config format macos uses internally.

## installation

```bash
# download the script
curl -o wallpaper.py https://github.com/sushismitcher/Command-based-default-wallpaper-switcher-macOS/blob/main/wallpaper.py
chmod +x wallpaper.py

# move to somewhere in your PATH (optional)
mv wallpaper.py /usr/local/bin/wallpaper
```

## setup

```bash
# add wallpaper configurations
./wallpaper.py --setup

# or add them one by one
./wallpaper.py --add forest
./wallpaper.py --add space
./wallpaper.py --add minimal
```

for each wallpaper:
1. script pauses and tells you to change wallpaper in system preferences
2. you go change it manually 
3. press enter when done
4. script saves that config

## usage

```bash
# switch to specific wallpaper
./wallpaper.py forest

# random wallpaper
./wallpaper.py

# list available wallpapers  
./wallpaper.py --list

# show help
./wallpaper.py --help
```

## why this works better

- **reliable**: uses macos's own config format
- **fast**: no gui automation or broken apis
- **future-proof**: works even when apple moves files around
- **simple**: 150 lines of python vs fighting with objc apis

## requirements

- macos (tested on sequoia)
- python 3.6+
- admin access (for launchctl commands)

## notes

script automatically finds wallpaper configs even if apple moves them. stores your configs in `~/Scripts/wallpaper_configs/`.

if wallpaper doesn't change immediately, the agent restart failed. just switch wallpapers manually once and it'll work.

## automation examples

```bash
# random wallpaper every hour
echo "0 * * * * /usr/local/bin/wallpaper" | crontab

# specific wallpaper at sunset (requires macos shortcuts integration)
# or use with hammerspoon, alfred, etc.
```
