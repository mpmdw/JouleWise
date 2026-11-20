#!/usr/bin/env bash
# Usage: pick_filler_arg EPOCH A|B 1|2
# Picks an argument for registered filler shapes in America/Los_Angeles.

pick_filler_arg() {
    local epoch wall evening_end
    if [ "$#" -ne 3 ]; then
        printf '%s\n' 'usage: pick_filler_arg EPOCH A|B 1|2' >&2
        return 2
    fi
    epoch=${1#-}
    case "$epoch" in
        ''|*[!0-9]*)
            printf '%s\n' 'EPOCH must be integer seconds' >&2
            return 2
            ;;
    esac
    case "$2:$3" in
        A:1) evening_end=234810 ;;
        A:2) evening_end=230310 ;;
        B:1) printf '%s\n' NO-WINDOW; return ;;
        B:2) printf '%s\n' NONE; return ;; # the registered B filler queues are one-leg
        *)
            printf '%s\n' 'expected pin A or B and roster size 1 or 2' >&2
            return 2
            ;;
    esac

    # BSD date on the Air, GNU date on Linux. Prefix to avoid octal parsing.
    wall=$(LC_ALL=C TZ=America/Los_Angeles date -r "$1" +%H%M%S 2>/dev/null) ||
        wall=$(LC_ALL=C TZ=America/Los_Angeles date -d "@$1" +%H%M%S) || return 2
    wall=$((1$wall - 1000000))
    if [ "$wall" -gt 105000 ] && [ "$wall" -lt 131500 ]; then
        printf '%s\n' NONE
    elif [ "$wall" -lt 23500 ] || [ "$wall" -gt "$evening_end" ]; then
        printf '%s\n' 13:14-13:15
    else
        printf '%s\n' 02:00-02:35
    fi
}

case ${ZSH_EVAL_CONTEXT-} in
    *:file) ;; # zsh source
    *)
        if [ -n "${ZSH_VERSION-}" ] || [ "${BASH_SOURCE[0]}" = "$0" ]; then
            pick_filler_arg "$@"
        fi
        ;;
esac
