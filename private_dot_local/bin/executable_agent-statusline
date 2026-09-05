#!/usr/bin/env bash
# Agent statusLine (Claude Code & Antigravity). Design system:
#   - identity segments (host, path, branch, model) are neutral greys, with the
#     path brightest since it is the most-scanned
#   - the three usage numbers (context, 5h session, weekly) all read as
#     PERCENT USED, so a bigger number always means less headroom, and they
#     share one colour ramp: grey -> amber -> red
#   - colour is reserved for state, never decoration, so a red segment always
#     means "this is the constraint you are about to hit"
# Rate limit segments require a Pro/Max subscription; they are absent for API keys.

input=$(cat)

# Single jq pass instead of one fork per field -- the statusline re-renders on every turn
mapfile -t fields < <(jq -r '
  .workspace.current_dir // .cwd // "",
  .model.display_name // .model.name // .model // "",
  .session_name // .agent.name // "",
  .context_window.used_percentage // .context.used_percentage // .context_window_used_percentage // "",
  .rate_limits.five_hour.used_percentage // "",
  .rate_limits.five_hour.resets_at // "",
  .rate_limits.seven_day.used_percentage // "",
  .rate_limits.seven_day.resets_at // ""
' <<<"$input")
cwd="${fields[0]}"
model="${fields[1]}"
session_name="${fields[2]}"
ctx_pct="${fields[3]}"
five_hour_pct="${fields[4]}"
five_hour_resets="${fields[5]}"
week_pct="${fields[6]}"
week_resets="${fields[7]}"
for v in ctx_pct five_hour_pct week_pct; do
  [[ -n "${!v}" ]] && printf -v "$v" '%.0f' "${!v}"
done

host=$(hostname -s)
home_dir="$HOME"
cwd_display="${cwd/#$home_dir/\~}"

# Git branch (skip optional locks for speed)
branch=""
if git -C "$cwd" --no-optional-locks rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null \
           || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
fi

# Session window is capped at 5h, so a plain H:MM countdown never needs a day component
countdown_hm() {
  local secs=$(( $1 - $(date +%s) ))
  (( secs < 0 )) && secs=0
  printf '%d:%02d' $(( secs / 3600 )) $(( (secs % 3600) / 60 ))
}

# Wall-clock reset time, e.g. "5:47pm", or "Thu 5:47pm" when it is not today
reset_clock() {
  if [[ "$(date -d "@$1" +%Y%m%d)" == "$(date +%Y%m%d)" ]]; then
    date -d "@$1" +'%-I:%M%P'
  else
    date -d "@$1" +'%a %-I:%M%P'
  fi
}

BRANCH_ICON=$''     # nf-pl-branch
HOURGLASS_ICON=$''  # nf-fa-hourglass_half
CLOCK_ICON=$''      # nf-fa-clock_o
SESSION_ICON=$'✻'

WEEK_SHOW_THRESHOLD=70  # weekly window stays hidden until it is plausibly the constraint
USAGE_WARN=60           # shared by all three usage numbers
USAGE_HOT=85

# Light/dark adaptation.
BG_CACHE_TTL=10  # theme flips are rare; this keeps probe off the hot path

bg_mode() {
  if [[ -n "${CLAUDE_STATUSLINE_BG:-}" ]]; then
    printf '%s' "$CLAUDE_STATUSLINE_BG"
    return
  fi

  local cache="${XDG_CACHE_HOME:-$HOME/.cache}/claude-statusline-bg"
  local mode="" mtime now
  now=$(date +%s)
  if [[ -r "$cache" ]]; then
    mtime=$(stat -c %Y "$cache" 2>/dev/null || echo 0)
    if (( now - mtime < BG_CACHE_TTL )); then
      read -r mode < "$cache"
      if [[ -n "$mode" ]]; then
        printf '%s' "$mode"
        return
      fi
    fi
  fi

  mode=dark
  if command -v reg.exe &>/dev/null; then
    # AppsUseLightTheme: 0x1 light, 0x0 dark. reg.exe emits CRLF, hence tr.
    local val
    val=$(reg.exe query 'HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize' \
            /v AppsUseLightTheme 2>/dev/null \
          | tr -d '\r' | awk '/AppsUseLightTheme/ {print $NF}')
    [[ "$val" == "0x1" ]] && mode=light
  elif command -v gsettings &>/dev/null; then
    local scheme
    scheme=$(gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null)
    [[ "$scheme" == *default* ]] && mode=light
  fi

  mkdir -p "${cache%/*}" 2>/dev/null
  printf '%s\n' "$mode" >"$cache" 2>/dev/null
  printf '%s' "$mode"
}

# 256-colour escapes rather than the 30-37/90-97 ANSI codes: those render at
# whatever darkness each terminal's palette assigns.
if [[ "$(bg_mode)" == light ]]; then
  NEUTRAL='\033[38;5;239m'
  NEUTRAL_DIM='\033[38;5;245m'
  NEUTRAL_BRIGHT='\033[38;5;233m'
  ACCENT='\033[38;5;25m'
  WARN='\033[38;5;130m'
  HOT='\033[38;5;124m'
else
  NEUTRAL='\033[38;5;245m'
  NEUTRAL_DIM='\033[38;5;242m'
  NEUTRAL_BRIGHT='\033[38;5;252m'
  ACCENT='\033[38;5;110m'
  WARN='\033[38;5;214m'
  HOT='\033[38;5;196m'
fi
RESET='\033[0m'

# One ramp for every usage number, so the same colour means the same pressure
usage_color() {
  if (( $1 >= USAGE_HOT )); then printf '%s' "$HOT"
  elif (( $1 >= USAGE_WARN )); then printf '%s' "$WARN"
  else printf '%s' "$NEUTRAL"; fi
}

# Fixed-width-ish segments first, variable-length session title last
parts=()
parts+=("${NEUTRAL_DIM}${host}${RESET}")
parts+=("${NEUTRAL_BRIGHT}${cwd_display}${RESET}")

if [[ -n "$branch" ]]; then
  parts+=("${NEUTRAL}${BRANCH_ICON} ${branch}${RESET}")
fi

if [[ -n "$model" ]]; then
  parts+=("${NEUTRAL}${model}${RESET}")
fi

if [[ -n "$ctx_pct" ]]; then
  parts+=("$(usage_color "$ctx_pct")ctx ${ctx_pct}%${RESET}")
fi

if [[ -n "$five_hour_pct" && -n "$five_hour_resets" ]]; then
  parts+=("$(usage_color "$five_hour_pct")${HOURGLASS_ICON} ${five_hour_pct}% $(countdown_hm "$five_hour_resets")${RESET}")
fi

if [[ -n "$week_pct" && -n "$week_resets" ]] && (( week_pct >= WEEK_SHOW_THRESHOLD )); then
  parts+=("$(usage_color "$week_pct")${CLOCK_ICON} ${week_pct}% $(reset_clock "$week_resets")${RESET}")
fi

if [[ -n "$session_name" ]]; then
  parts+=("${ACCENT}${SESSION_ICON} ${session_name}${RESET}")
fi

# Dim separator so it recedes behind the content it divides
sep="${NEUTRAL_DIM} · ${RESET}"
out=""
for part in "${parts[@]}"; do
  if [[ -z "$out" ]]; then
    out="$part"
  else
    out="${out}${sep}${part}"
  fi
done

printf "%b\n" "$out"
