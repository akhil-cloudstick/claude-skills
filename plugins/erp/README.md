# erp

Post your daily work update to the Cloudhouse ERP without writing it yourself.

Optional and self-contained: installing this does not install the `cloudhouse` standards plugin,
and installing that one does not install this.

| | |
|---|---|
| `/erp:eod` | draft and post a work update, status and progress for a subtask |
| `/erp:logout` | sign out on this machine |

## Why

Every day, every subtask you touched needs an update in the ERP — what was done, plus a status
and a progress bump. It gets skipped when work is busy, and reconstructing a week later is
guesswork.

The work itself is already recorded: in your Claude Code sessions, in the files you changed, and
sometimes in commits. This reads that, drafts the update in your own style, works out the
progress from the subtask's own description, and posts only what you approved.

## Install

```
/plugin marketplace add akhil-cloudstick/claude-skills
/plugin install erp@cloudhouse-skills
```

Already added the marketplace? The second line is enough. Repeat on each machine you work
from — office, client RDP, laptop. Nothing is shared between them.

## First run

```
/erp:eod
```

Not signed in yet? It asks for your email, then opens a small login window where you type your
password — hidden, and never in the chat transcript. The ERP URL is built in
(`https://api.cloudhousetechnologies.com`), so you never type it.

The session is stored in `~/.cloudhouse-eod.json` **on that machine only**, never in this repo.
It lasts 72 hours and renews itself silently.

## What happens

1. **Signed in as** — every prompt carries the account, so you always know which login will write.
2. **Pick the project** — a selectable list of everything assigned to you; more than four, and a
   `More` option pages through the rest. Nothing is hidden.
3. **Pick the task**, then **the subtask** — same list style, multi-select on subtasks, with
   back options at each level. You can also type a subtask id or part of its name to jump
   straight there.
4. **It reads the day** — every Claude Code session of that day, not just the current chat, plus
   files changed on disk and any commits. Scoped to the repo you ran it in, so one project's
   work never leaks into another's update.
5. **It drafts** — short bullet points in plain English, and a proposed status and progress.
6. **You review** — approve, edit any of the three, or skip. **Your edit is what gets posted**,
   word for word.
7. **It posts** — update, then status, then progress, one request at a time, reporting each.
   Unchanged values send nothing.

## How progress is worked out

From the subtask's **description**, not guessed. It reads the subtask first, so the "from"
number is the real stored one:

```
Progress  0% → 65%   (new page ✓, View More redirect ✓, keep filters — partial → 2.5 of 3)
```

No description? It falls back to the subtask name, the current progress and what you did that
day, and says plainly that it is estimating.

It never lowers stored progress unless you say work was reverted, never proposes a number that
contradicts the status, and never treats logged hours as progress.

## Day and project boundaries

- **One day, one update.** The day runs 05:00 → 05:00, so work past midnight counts as the
  previous working day. Missed yesterday? Ask for that date — it is posted as its own update,
  never merged into today's.
- **One project per run.** The repo you are in decides the project. For another project, run it
  in that project's repo.

## Switching account / signing out

```
/erp:logout                   sign out on this machine
erp.py login --update         sign in as someone else
```

Credentials live per machine and are never committed. Signing out deletes the stored email,
password and token locally; nothing on the ERP server changes.

## Files

```
skills/eod/SKILL.md            the workflow
skills/eod/scripts/erp.py      ERP client — login, tasks, subtask, updates, update/status/progress
skills/eod/scripts/today.py    collects one day of real work from sessions, disk and git
commands/logout.md             /erp:logout
```

Both scripts are Python 3 standard library only — nothing to install. They can be run directly
if you want to check something by hand:

```
py skills/eod/scripts/erp.py whoami
py skills/eod/scripts/erp.py tasks
py skills/eod/scripts/today.py --date 2026-09-21
```

Only `update`, `status` and `progress` write anything; everything else is read-only.
