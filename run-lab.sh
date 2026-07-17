#!/usr/bin/env bash
# run-lab.sh — one-click launcher for the Reachy Mini mini-lab.
#
# For non-technical attendees: no need to know terminals, venvs, or IDEs. Just
# start this (double-click "Reachy Mini Lab" on the desktop, or run ./run-lab.sh)
# and pick a number. It takes care of the venv, the robot daemon, and Ollama.
#
# The classic terminal/IDE flow (lab/LAB.md) still works as a fallback for staff.

set -uo pipefail

# --- locate ourselves so double-click / any CWD works ----------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- pretty output ---------------------------------------------------------
BOLD="$(tput bold 2>/dev/null || true)"
DIM="$(tput dim 2>/dev/null || true)"
RED="$(tput setaf 1 2>/dev/null || true)"
GRN="$(tput setaf 2 2>/dev/null || true)"
YLW="$(tput setaf 3 2>/dev/null || true)"
CYN="$(tput setaf 6 2>/dev/null || true)"
RST="$(tput sgr0 2>/dev/null || true)"

say()  { printf "%s\n" "$*"; }
info() { printf "%s%s%s\n" "$CYN" "$*" "$RST"; }
ok()   { printf "%s✅ %s%s\n" "$GRN" "$*" "$RST"; }
warn() { printf "%s⚠️  %s%s\n" "$YLW" "$*" "$RST"; }
err()  { printf "%s❌ %s%s\n" "$RED" "$*" "$RST"; }

pause() {
    printf "\n%sPress Enter to return to the menu…%s" "$DIM" "$RST"
    read -r _ || true
}

# --- environment -----------------------------------------------------------
activate_venv() {
    if [[ -f "venv/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source venv/bin/activate
    else
        err "Python environment (venv/) not found. A staff member needs to run ./setup.sh first."
        exit 1
    fi
}

ensure_ollama() {
    # The local LLM/VLM server. Tasks 2 & 3 need it; Task 1 doesn't.
    if curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
        return 0
    fi
    if command -v ollama >/dev/null 2>&1; then
        info "Starting the local AI server (Ollama)…"
        nohup ollama serve >/tmp/reachy-lab-ollama.log 2>&1 &
        for _ in $(seq 1 20); do
            sleep 0.5
            curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && { ok "Local AI server ready."; return 0; }
        done
        warn "Local AI server didn't come up in time (see /tmp/reachy-lab-ollama.log). Tasks 2 & 3 may not respond."
    else
        warn "Ollama not installed — Tasks 2 & 3 need it. Flag a staff member."
    fi
}

daemon_running() {
    pgrep -f "reachy-mini-daemon" >/dev/null 2>&1
}

ensure_daemon() {
    # The robot daemon drives the motors. We start it with --no-media so the
    # camera stays free for the vision task (Task 3).
    if daemon_running; then
        return 0
    fi
    info "Waking up the robot (starting the daemon)…"
    nohup reachy-mini-daemon --no-media >/tmp/reachy-lab-daemon.log 2>&1 &
    for _ in $(seq 1 20); do
        sleep 0.5
        daemon_running && { ok "Robot is awake."; sleep 1.0; return 0; }
    done
    warn "The robot daemon didn't start (see /tmp/reachy-lab-daemon.log)."
    warn "The robot may not move. Flag a staff member if so."
}

# --- "make it yours" prompts ----------------------------------------------
# Ask the attendee for a free-form line, with a clear default on Enter. We pass
# the answer to the scripts via env vars (LAB_ROBOT_PERSONA / LAB_VISION_PROMPT)
# so nothing on disk changes and every run starts clean.
ask_persona() {
    printf "\n%s✋ Make it yours — give Reachy a personality.%s\n" "$BOLD" "$RST"
    printf "%s   Examples: talk like an excited puppy · be a grumpy pirate · sound like a wise robot%s\n" "$DIM" "$RST"
    printf "   Type a personality, or just press Enter to keep the default:\n   %s> %s" "$CYN" "$RST"
    read -r reply || reply=""
    if [[ -n "${reply// }" ]]; then
        export LAB_ROBOT_PERSONA="You are a desktop robot. $reply"
        ok "Got it — Reachy will: $reply"
    else
        unset LAB_ROBOT_PERSONA
        info "Keeping Reachy's default personality."
    fi
}

ask_vision_prompt() {
    printf "\n%s✋ Make it yours — tell Reachy how to describe what it sees.%s\n" "$BOLD" "$RST"
    printf "%s   Examples: describe it like a pirate · guess my mood · name every object you see%s\n" "$DIM" "$RST"
    printf "   Type an instruction, or just press Enter to keep the default:\n   %s> %s" "$CYN" "$RST"
    read -r reply || reply=""
    if [[ -n "${reply// }" ]]; then
        export LAB_VISION_PROMPT="$reply"
        ok "Got it — Reachy will: $reply"
    else
        unset LAB_VISION_PROMPT
        info "Keeping Reachy's default way of describing things."
    fi
}

# --- tasks -----------------------------------------------------------------
# Each task runs in the foreground; Ctrl+C returns to the menu (we trap SIGINT
# only around the task so the menu itself stays responsive).
run_task() {
    local title="$1"; shift
    printf "\n%s%s%s\n" "$BOLD" "$title" "$RST"
    info "Starting… (press Ctrl+C to stop and come back to the menu)"
    say ""
    # Run in a subshell with its own SIGINT handling so Ctrl+C stops only the task.
    ( trap - INT; "$@" )
    say ""
    ok "Done."
}

task_voice() {
    run_task "🗣️  Task 1 — Reachy talks (cloud voice)" \
        python lab/emo_v1.py --chat
}

task_local() {
    ensure_ollama
    ask_persona
    run_task "💻 Task 2 — Reachy talks, 100% offline on AMD" \
        python lab/emo_v2.py --chat
}

task_local_voice() {
    ensure_ollama
    ask_persona
    run_task "🎙️  Task 2 (talk to it) — speak instead of typing" \
        python lab/emo_v2.py --asr
}

task_vision() {
    ensure_ollama
    ask_vision_prompt
    printf "\n%s👀 Task 3 — Reachy sees and describes the world%s\n" "$BOLD" "$RST"
    info "A browser window will open at http://localhost:8080 with a live camera"
    info "feed and a big \"Look & Describe\" button. Hold up an object and click it!"
    info "(Press Ctrl+C here to stop and come back to the menu.)"
    say ""
    # Open the browser shortly after the server starts.
    ( sleep 3; xdg-open "http://localhost:8080" >/dev/null 2>&1 || true ) &
    ( trap - INT; python lab/emo_v3.py --preview-web )
    say ""
    ok "Done."
}

# --- menu ------------------------------------------------------------------
menu() {
    while true; do
        clear
        cat <<EOF
${BOLD}${CYN}╔══════════════════════════════════════════════════════════╗
║              🤖  Reachy Mini — Interactive Lab           ║
╚══════════════════════════════════════════════════════════╝${RST}

  Pick what you'd like Reachy to do (type a number, then Enter):

    ${BOLD}1${RST}  🗣️   Give Reachy a voice        ${DIM}(cloud voice, type to chat)${RST}
    ${BOLD}2${RST}  💻  Run it 100% offline on AMD ${DIM}(local AI, type to chat)${RST}
    ${BOLD}3${RST}  🎙️   Talk to Reachy            ${DIM}(offline, speak instead of typing)${RST}
    ${BOLD}4${RST}  👀  Give Reachy eyes           ${DIM}(sees & describes, in the browser)${RST}

    ${BOLD}m${RST}  🎤  Choose / test the microphone
    ${BOLD}q${RST}  👋  Quit

EOF
        printf "  Your choice: "
        read -r choice || { echo; break; }
        case "${choice,,}" in
            1) ensure_daemon; task_voice; pause ;;
            2) ensure_daemon; task_local; pause ;;
            3) ensure_daemon; task_local_voice; pause ;;
            4) ensure_daemon; task_vision; pause ;;
            m) python lab/emo_v2.py --list-mics; pause ;;
            q|quit|exit) break ;;
            "") : ;;  # empty: just redraw
            *) warn "Didn't catch that — please type 1, 2, 3, 4, m, or q."; sleep 1.2 ;;
        esac
    done
    say ""
    ok "Thanks for playing with Reachy Mini! 👋"
}

main() {
    activate_venv
    menu
}

main "$@"
