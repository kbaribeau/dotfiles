#!/bin/bash
# Bash 3.2 compatible. Never source configuration or evaluate manifest data.
# Handle statuses explicitly (including the three destination states below).
export LC_ALL=C

usage() { printf 'Usage: %s [--dry-run] [--home /absolute/home]\n' "${0##*/}"; }
fail() { printf 'error: %s\n' "$1" >&2; exit "${2:-1}"; }

# Resolve final and parent symlinks without GNU readlink -f. A bound also
# rejects cycles; legitimate chains longer than 64 final links are unsupported.
resolve() {
    local path=$1 parent leaf target hops=0
    while :; do
        parent=${path%/*}
        parent=$(cd -P -- "${parent:-/}" 2>/dev/null && pwd -P) || return 1
        leaf=${path##*/}
        path=$parent/$leaf
        if [ ! -L "$path" ]; then
            [ -e "$path" ] || return 1
            if [ -d "$path" ]; then
                (cd -P -- "$path" 2>/dev/null && pwd -P)
            else
                printf '%s\n' "$path"
            fi
            return $?
        fi
        hops=$((hops + 1))
        [ "$hops" -le 64 ] || return 1
        target=$(readlink "$path") || return 1
        case "$target" in
            /*) path=$target ;;
            *) path=$parent/$target ;;
        esac
    done
}

script=${BASH_SOURCE[0]}
case "$script" in
    /*) ;;
    */*) script=$PWD/$script ;;
    *) # `bash install.sh` opens a cwd-relative filename, even without '.' in PATH.
       if [ ! -e "$script" ] && [ ! -L "$script" ]; then
           script=$(command -v -- "$script") || fail 'cannot locate installer'
       fi
       case "$script" in /*) ;; *) script=$PWD/$script ;; esac ;;
esac
script=$(resolve "$script") || fail 'cannot resolve installer (missing path or symlink loop)'
repo=${script%/*}

home=${HOME:-}
dry_run=0
home_seen=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --dry-run) [ "$dry_run" -eq 0 ] || fail 'duplicate --dry-run' 2; dry_run=1; shift ;;
        --home)
            [ "$#" -ge 2 ] && [ "$home_seen" -eq 0 ] || fail 'expected one --home value' 2
            home=$2; home_seen=1; shift 2 ;;
        --help|-h) [ "$#" -eq 1 ] || fail 'help takes no additional arguments' 2; usage; exit 0 ;;
        *) usage >&2; fail 'unknown argument' 2 ;;
    esac
done

# Require normalized relative names; spaces are data, not separators.
relative_path() {
    case "$1" in
        ''|/*|*/|*//*|.|..|./*|../*|*/./*|*/../*|*/.|*/..|*[[:cntrl:]]*) return 1 ;;
    esac
}
case "$home" in /*) ;; *) fail 'home must be an absolute path' 2 ;; esac
home=${home%/}
relative_path "${home#/}" || fail 'home must be a normalized, non-root absolute path' 2
command -v perl >/dev/null 2>&1 || fail 'Perl is required for exact no-clobber symlink creation'

manifest=$repo/install/links.tsv
[ -f "$manifest" ] && [ -r "$manifest" ] || fail 'cannot read install/links.tsv'
# Bash read silently drops NULs. Reject control bytes before parsing, not after.
perl -e 'open my $f, "<", $ARGV[0] or exit 1;
    while (<$f>) { exit 2 if /[\x00-\x08\x0b-\x1f\x7f]/ }' "$manifest"
manifest_status=$?
[ "$manifest_status" -ne 2 ] || fail 'manifest contains unsupported control bytes' 2
[ "$manifest_status" -eq 0 ] || fail 'cannot validate manifest'
sources=() destinations=() names=()
status=0
problem() {
    printf 'error: %s\n' "$1" >&2
    [ "$status" -ge "$2" ] || status=$2
}
overlap() { case "$1/" in "$2/"*) return 0 ;; esac; case "$2/" in "$1/"*) return 0 ;; esac; return 1; }
line_number=0
tab=$'\t'
while IFS= read -r line || [ -n "$line" ]; do
    line_number=$((line_number + 1))
    case "$line" in ''|'#'*) continue ;; esac
    case "$line" in
        *"$tab"*) source=${line%%"$tab"*}; destination=${line#*"$tab"} ;;
        *) problem "manifest line $line_number: expected two tab-separated fields" 2; continue ;;
    esac
    if ! relative_path "$source" || ! relative_path "$destination"; then
        problem "manifest line $line_number: invalid path or extra field" 2
        continue
    fi
    # Conservative case-folding also prevents collisions on default macOS volumes.
    folded=$(printf '%s' "$destination" | tr '[:upper:]' '[:lower:]')
    for previous in "${names[@]}"; do
        if overlap "$folded" "$previous"; then
            problem "manifest line $line_number: duplicate or overlapping destination" 2
        fi
    done
    names[${#names[@]}]=$folded
    sources[${#sources[@]}]=$repo/$source
    destinations[${#destinations[@]}]=$home/$destination
done < "$manifest"
[ "${#sources[@]}" -gt 0 ] || problem 'manifest has no mappings' 2

# Reject symlinks at EVERY destination ancestor, including the selected home.
# Do not canonicalize them away: that could authorize writes outside the home.
parents_safe() {
    local path=${1%/*} part current='' rest nearest=/
    rest=${path#/}
    while [ -n "$rest" ]; do
        part=${rest%%/*}; current=$current/$part
        if [ -L "$current" ]; then return 1; fi
        if [ -e "$current" ]; then
            [ -d "$current" ] && [ -x "$current" ] || return 1
            nearest=$current
        else
            [ -w "$nearest" ] || return 1
        fi
        case "$rest" in */*) rest=${rest#*/} ;; *) rest='' ;; esac
    done
    if [ ! -e "$1" ] && [ ! -L "$1" ]; then [ -w "$nearest" ] || return 1; fi
    return 0
}
source_ready() {
    [ -r "$1" ] || return 1
    if [ -d "$1" ]; then [ -x "$1" ]; else [ -f "$1" ]; fi
}
# Keep link text and inode verbatim, including equivalent relative/chained links.
link_state() {
    local actual expected
    if [ -L "$2" ]; then
        actual=$(resolve "$2") && expected=$(resolve "$1") && [ "$actual" = "$expected" ] && return 0
        return 1
    fi
    [ ! -e "$2" ] && return 3
    return 1
}

canonical_sources=()
actions=()
for source in "${sources[@]}"; do
    canonical=$(resolve "$source") || canonical=$source
    canonical_sources[${#canonical_sources[@]}]=$canonical
done
for ((i=0; i<${#sources[@]}; i++)); do
    source=${sources[i]}; destination=${destinations[i]}
    source_ready "$source" || problem "source unavailable: ${source#"$repo/"}" 1
    parents_safe "$destination" || problem "unsafe ancestor: ${destination#"$home/"}" 1
    link_state "$source" "$destination"; state=$?
    [ "$state" -ne 1 ] || problem "destination conflict: ${destination#"$home/"}" 1
    if [ "$state" -eq 0 ]; then actions[i]=keep; else actions[i]=create; fi
    # Check both lexical and physical source locations, where resolvable.
    for other in "${sources[@]}" "${canonical_sources[@]}"; do
        if overlap "$destination" "$other"; then
            problem "source/destination overlap: ${destination#"$home/"}" 2
            break
        fi
    done
done
[ "$status" -eq 0 ] || exit "$status"

if [ "$dry_run" -eq 1 ]; then
    for ((i=0; i<${#sources[@]}; i++)); do
        printf '%s: %s\n' "${actions[i]}" "${destinations[i]#"$home/"}"
    done
    printf 'Dry run: no writes.\n'
    exit 0
fi

created=0
parents_created=0
kept=0
runtime_failure() {
    printf 'error: %s; partial progress: %s links and %s parents created, %s links kept; no rollback performed\n' \
        "$1" "$created" "$parents_created" "$kept" >&2
    exit 1
}
make_parents() {
    local path=${1%/*} part current='' rest
    rest=${path#/}
    while [ -n "$rest" ]; do
        part=${rest%%/*}; current=$current/$part
        [ ! -L "$current" ] || return 1
        if [ ! -e "$current" ]; then
            mkdir -- "$current" || return 1
            parents_created=$((parents_created + 1))
        fi
        [ ! -L "$current" ] && [ -d "$current" ] && [ -x "$current" ] || return 1
        case "$rest" in */*) rest=${rest#*/} ;; *) rest='' ;; esac
    done
}
for ((i=0; i<${#sources[@]}; i++)); do
    source=${sources[i]}; destination=${destinations[i]}
    if ! source_ready "$source" || ! parents_safe "$destination"; then
        runtime_failure 'source or ancestor changed'
    fi
    link_state "$source" "$destination"; state=$?
    case "$state" in
        0) kept=$((kept + 1)); continue ;;
        1) runtime_failure "destination changed: ${destination#"$home/"}" ;;
    esac
    make_parents "$destination" || runtime_failure 'cannot create safe parents'
    if ! source_ready "$source" || ! parents_safe "$destination"; then
        runtime_failure 'source or ancestor changed'
    fi
    link_state "$source" "$destination"; state=$?
    case "$state" in
        0) kept=$((kept + 1)); continue ;;
        1) runtime_failure "destination changed: ${destination#"$home/"}" ;;
    esac
    # ln can nest inside a directory appearing after the check. symlink(2)
    # instead fails at the exact destination for ANY existing entry, atomically.
    perl -e 'symlink($ARGV[0], $ARGV[1]) or exit 1' -- "$source" "$destination" ||
        runtime_failure "cannot create link: ${destination#"$home/"}"
    created=$((created + 1))
done
printf 'Done: %s links created, %s links kept, %s parents created.\n' "$created" "$kept" "$parents_created"
