#!/usr/bin/env python3
"""Collect what was actually worked on for one calendar day.

Commits are unreliable (work is often committed days later) and a single chat is only
part of the day, so the evidence comes from three timestamped sources, all filtered to
the same local-day window:

  1. every Claude Code session transcript (~/.claude/projects/*/*.jsonl) - all chats,
     all repos - using per-entry timestamps
  2. files on disk whose modification time falls inside the day
  3. git commits authored inside the day (a bonus, never the only source)

    py today.py [--date YYYY-MM-DD] [--repo PATH ...] [--day-start 05:00] [--full]

Prints one JSON object. Nothing outside the requested day is ever included.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, time as dtime, timedelta

PROJECTS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "projects")

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", ".next", ".nuxt", "vendor",
    "__pycache__", ".venv", "venv", "target", ".idea", ".vscode", "coverage",
    ".turbo", ".cache", "tmp", "Pods", ".expo", "bin", "obj",
}
SKIP_SUFFIXES = (
    ".log", ".lock", ".map", ".pyc", ".class", ".exe", ".dll", ".zip", ".png",
    ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".mp4", ".woff", ".woff2", ".ttf",
)

# Bash commands worth reporting - the rest is noise (ls, cat, cd, grep ...).
INTERESTING_CMD = re.compile(
    r"\b(git commit|git push|git merge|git tag|npm run build|npm run deploy|yarn build|"
    r"pnpm build|docker build|docker compose|docker-compose|go build|go test|pytest|"
    r"npm test|npx expo|eas build|vercel|rsync|scp|migrate|alembic|prisma)\b",
    re.I,
)

NOISE_BLOCK = re.compile(
    r"<(system-reminder|ide_selection|ide_opened_file|command-name|command-message|"
    r"command-args|local-command-stdout|local-command-stderr|local-command-caveat)>.*?</\1>"
    r"|<(system-reminder|ide_selection|ide_opened_file)>.*",
    re.S,
)

# prompts the harness generated, not the user: slash commands, caveats, resume preambles
SLASH_ONLY = re.compile(r"^/?[\w:-]+$")
HARNESS_PROMPT = re.compile(
    r"^(Caveat: The messages below|This session is being continued|"
    r"Your response above was cut off|\[Request interrupted)",
    re.I,
)


# --------------------------------------------------------------------------- helpers


def parse_ts(value):
    """Parse an ISO timestamp from a transcript entry into an aware datetime."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def day_window(date_str, day_start):
    """Local-time window for the requested day, returned as aware datetimes."""
    day = datetime.strptime(date_str, "%Y-%m-%d").date()
    hour, _, minute = day_start.partition(":")
    start_time = dtime(int(hour), int(minute or 0))
    local_tz = datetime.now().astimezone().tzinfo
    start = datetime.combine(day, start_time, tzinfo=local_tz)
    return start, start + timedelta(days=1)


def clean_prompt(text):
    text = NOISE_BLOCK.sub("", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    if SLASH_ONLY.match(text) or HARNESS_PROMPT.match(text):
        return ""
    return text


def rel(path, root):
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


# --------------------------------------------------------------------------- sessions


def read_session(path, start, end, full):
    """Return the part of one transcript that falls inside the window."""
    out = {
        "session_id": os.path.splitext(os.path.basename(path))[0],
        "cwd": None,
        "titles": [],
        "first_activity": None,
        "last_activity": None,
        "prompts": [],
        "files_changed": {},
        "commands": [],
    }

    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            has_stamp = '"timestamp"' in line
            if not has_stamp and '"aiTitle"' not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue

            # chat titles carry no timestamp; keep them, they describe the session
            if entry.get("type") == "ai-title":
                title = entry.get("aiTitle")
                if title and title not in out["titles"]:
                    out["titles"].append(title)
                continue

            stamp = parse_ts(entry.get("timestamp"))
            if not stamp or not (start <= stamp < end):
                continue

            if entry.get("cwd") and not out["cwd"]:
                out["cwd"] = entry["cwd"]
            iso = stamp.isoformat(timespec="minutes")
            if not out["first_activity"]:
                out["first_activity"] = iso
            out["last_activity"] = iso

            kind = entry.get("type")

            if kind == "user":
                content = entry.get("message", {}).get("content")
                if isinstance(content, str):
                    parts = [content]
                elif isinstance(content, list):
                    parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                else:
                    parts = []
                for part in parts:
                    text = clean_prompt(part)
                    if len(text) > 2:
                        text = text if full else text[:400]
                        if text not in out["prompts"]:  # resumed turns repeat the prompt
                            out["prompts"].append(text)

            elif kind == "assistant":
                content = entry.get("message", {}).get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if block.get("type") != "tool_use":
                        continue
                    name = block.get("name")
                    args = block.get("input") or {}
                    if name in EDIT_TOOLS and args.get("file_path"):
                        key = args["file_path"]
                        out["files_changed"][key] = out["files_changed"].get(key, 0) + 1
                    elif name == "Bash":
                        command = (args.get("command") or "").strip()
                        if INTERESTING_CMD.search(command):
                            command = re.sub(r"\s+", " ", command)
                            out["commands"].append(command if full else command[:300])

    return out


def collect_sessions(start, end, full):
    sessions = []
    if not os.path.isdir(PROJECTS_DIR):
        return sessions
    cutoff = start.timestamp()
    for folder in sorted(os.listdir(PROJECTS_DIR)):
        folder_path = os.path.join(PROJECTS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for name in sorted(os.listdir(folder_path)):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(folder_path, name)
            try:
                # a transcript untouched since before the window holds nothing for it
                if os.path.getmtime(path) < cutoff:
                    continue
            except OSError:
                continue
            session = read_session(path, start, end, full)
            if session["first_activity"]:
                session["project_folder"] = folder
                sessions.append(session)
    return sessions


# --------------------------------------------------------------------------- disk + git


def scan_files(repo, start, end, limit=400):
    """Files under repo whose mtime falls inside the window."""
    found = []
    lo, hi = start.timestamp(), end.timestamp()
    for root, dirs, names in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in names:
            if name.endswith(SKIP_SUFFIXES):
                continue
            path = os.path.join(root, name)
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            if lo <= mtime < hi:
                found.append(
                    {
                        "path": rel(path, repo),
                        "modified": datetime.fromtimestamp(mtime).isoformat(timespec="minutes"),
                    }
                )
                if len(found) >= limit:
                    return sorted(found, key=lambda f: f["modified"])
    return sorted(found, key=lambda f: f["modified"])


import tempfile

CLAUDE_HOME = os.path.normcase(os.path.join(os.path.expanduser("~"), ".claude"))
TEMP_HOME = os.path.normcase(tempfile.gettempdir())


def repo_root(file_path):
    """Nearest ancestor directory holding a .git folder, else the containing directory."""
    path = os.path.dirname(os.path.normpath(file_path))
    lowered = os.path.normcase(path)
    if lowered.startswith(CLAUDE_HOME) or lowered.startswith(TEMP_HOME):
        return None  # plans, transcripts and scratch files are not project work
    walker = path
    while walker and os.path.basename(walker):
        if os.path.isdir(os.path.join(walker, ".git")):
            return walker
        parent = os.path.dirname(walker)
        if parent == walker:
            break
        walker = parent
    return path if os.path.isdir(path) else None


def under(path, root):
    """True when path is root itself or sits inside it."""
    path = os.path.normcase(os.path.normpath(path))
    root = os.path.normcase(os.path.normpath(root))
    return path == root or path.startswith(root + os.sep)


def scope_sessions(sessions, scope):
    """Keep only the work that belongs to one repo, dropping everything else."""
    kept = []
    for session in sessions:
        files = {p: n for p, n in session["files_changed"].items() if under(p, scope)}
        in_scope = bool(files) or (session["cwd"] and under(session["cwd"], scope))
        if not in_scope:
            continue
        session = dict(session, files_changed=files)
        if not (files or session["prompts"] or session["commands"]):
            continue  # a chat that only opened in this repo is not work
        kept.append(session)
    return kept


def dedupe_repos(repos):
    """Drop any repo that sits inside another one already in the set."""
    ordered = sorted(repos, key=len)
    kept = []
    for repo in ordered:
        lowered = os.path.normcase(repo)
        if any(os.path.normcase(k) == lowered for k in kept):
            continue
        if any(lowered.startswith(os.path.normcase(k) + os.sep) for k in kept):
            continue
        kept.append(repo)
    return sorted(kept)


def git(repo, *args):
    try:
        result = subprocess.run(
            ["git", "-C", repo] + list(args),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def git_activity(repo, start, end):
    if not os.path.isdir(os.path.join(repo, ".git")):
        return None
    since = start.isoformat()
    until = end.isoformat()
    commits = git(
        repo, "log", "--all", "--since", since, "--until", until,
        "--pretty=%h|%an|%ad|%s", "--date=format:%H:%M",
    )
    return {
        "branch": git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "commits_today": [
            dict(zip(("hash", "author", "time", "subject"), line.split("|", 3)))
            for line in commits.splitlines()
            if line
        ],
        "uncommitted": git(repo, "status", "--short").splitlines()[:60],
    }


# --------------------------------------------------------------------------- main


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(description="Collect one day of real work")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument(
        "--day-start",
        default="05:00",
        help="local time the work day starts; late-night work before it counts as the previous day",
    )
    parser.add_argument("--repo", action="append", help="extra repo to scan (repeatable)")
    parser.add_argument(
        "--scope",
        default=None,
        help="repo to limit the day to; defaults to the current repo. Ignored with --all",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="every repo worked in that day instead of just this one",
    )
    parser.add_argument("--full", action="store_true", help="do not truncate prompts or commands")
    args = parser.parse_args()

    try:
        start, end = day_window(args.date, args.day_start)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": "Bad --date or --day-start: %s" % exc}))
        sys.exit(1)

    # One project, one update: by default only the repo this was run in is reported.
    scope = None
    if not args.all:
        scope = repo_root(os.path.join(args.scope or os.getcwd(), "_"))
        if not scope:
            scope = os.path.normpath(os.path.abspath(args.scope or os.getcwd()))

    sessions = collect_sessions(start, end, args.full)
    if scope:
        sessions = scope_sessions(sessions, scope)

    repos = set()
    for session in sessions:
        if session["cwd"]:
            repos.add(os.path.normpath(session["cwd"]))
        # work often lands outside the session's cwd - follow the edited files home
        for path in session["files_changed"]:
            root = repo_root(path)
            if root:
                repos.add(root)
    for extra in args.repo or []:
        repos.add(os.path.normpath(os.path.abspath(extra)))
    if scope:
        repos = {r for r in repos if under(r, scope)} | {scope}
    repos = dedupe_repos(repos)

    repo_reports = []
    for repo in sorted(repos):
        if not os.path.isdir(repo):
            continue
        repo_reports.append(
            {
                "repo": repo,
                "git": git_activity(repo, start, end),
                "files_modified_today": scan_files(repo, start, end),
            }
        )

    edited = {}
    for session in sessions:
        for path, count in session["files_changed"].items():
            edited[path] = edited.get(path, 0) + count

    print(
        json.dumps(
            {
                "ok": True,
                "date": args.date,
                "scope": scope or "ALL REPOS",
                "window": {"from": start.isoformat(), "to": end.isoformat()},
                "session_count": len(sessions),
                "sessions": sessions,
                "files_edited_by_claude": [
                    {"path": p, "edits": n}
                    for p, n in sorted(edited.items(), key=lambda kv: -kv[1])
                ],
                "repos": repo_reports,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
