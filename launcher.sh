#!/bin/sh
APP_DIR="$(dirname "$0")"
cd "$APP_DIR"
OPK_NAME="Mapp-0-lo"
LOG_DIR="/home/retrofw/rspdw_lab/black_box"
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi
LOG_FILE="${LOG_DIR}/${OPK_NAME}.log"
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0
export SDL_NOMOUSE=1
python2 main.py > "$LOG_FILE" 2>&1
