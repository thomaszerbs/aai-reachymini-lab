#!/usr/bin/env bash
# start-lab.sh — open the lab launcher (run-lab.sh) inside a terminal window.
#
# This exists so the desktop icon (reachy-mini-lab.desktop) works no matter which
# terminal emulator the booth machine has. If you already have a terminal open,
# you can just run ./run-lab.sh directly instead.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$SCRIPT_DIR/run-lab.sh"

# Already inside a terminal? Just run it here.
if [[ -t 1 ]]; then
    exec "$LAUNCHER"
fi

# Otherwise find a terminal emulator and open the launcher in it.
run_in() {
    command -v "$1" >/dev/null 2>&1
}

if run_in gnome-terminal; then
    exec gnome-terminal --title="Reachy Mini Lab" -- bash -lc "\"$LAUNCHER\"; exec bash"
elif run_in konsole; then
    exec konsole --title "Reachy Mini Lab" -e bash -lc "\"$LAUNCHER\"; exec bash"
elif run_in xfce4-terminal; then
    exec xfce4-terminal --title="Reachy Mini Lab" -e "bash -lc \"'$LAUNCHER'; exec bash\""
elif run_in tilix; then
    exec tilix -t "Reachy Mini Lab" -e bash -lc "\"$LAUNCHER\"; exec bash"
elif run_in x-terminal-emulator; then
    exec x-terminal-emulator -e bash -lc "\"$LAUNCHER\"; exec bash"
elif run_in xterm; then
    exec xterm -T "Reachy Mini Lab" -e bash -lc "\"$LAUNCHER\"; exec bash"
else
    # Last resort: no known terminal. Tell the user via a GUI dialog if we can.
    msg="No terminal emulator found. Open a terminal and run: $LAUNCHER"
    if run_in zenity; then
        zenity --error --text="$msg"
    elif run_in notify-send; then
        notify-send "Reachy Mini Lab" "$msg"
    fi
    exit 1
fi
