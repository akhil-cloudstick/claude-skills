# erp — daily ERP work updates

Optional plugin, separate from the `cloudhouse` standards plugin. Installing `cloudhouse` does
not install this, and this does not install `cloudhouse`.

One skill: **`/erp:eod`** — posts the day's work update, status and progress to the Cloudhouse
ERP for the project of the repo you run it in.

## Install

```
/plugin marketplace add akhil-cloudstick/claude-skills
/plugin install erp@cloudhouse-skills
```

Already added the marketplace for `cloudhouse`? Then only the second line is needed. Repeat it
on each machine you work from (office, client RDP, laptop) — nothing is shared between them
except the repo itself.

Non-interactive:

```
claude plugin install erp@cloudhouse-skills
```

## First run

```
py <plugin>/skills/eod/scripts/erp.py login
```

Asks only for your email and password — the ERP URL is built in
(`https://api.cloudhousetechnologies.com`; add `--dev` for `http://localhost:8085`, or
`--url <base>` for anything else). The session is stored in `~/.cloudhouse-eod.json`
**on that machine only**. Credentials are never in this repo, so each
machine and each person logs in separately. `login --update` changes account or URL.

Then, inside the repo of the project you want to report on:

```
/erp:eod
```

It reads what was really done that day in that repo — from every Claude Code session of the day,
not just the current chat — drafts a short bullet-point update per assigned subtask, proposes a
status and progress change, shows all three for you to edit, and posts each request one at a time
after you approve.

## Scope rules

- **One repo, one project.** Only the repo you run it in is reported. Other projects are posted
  by running it inside their own repo.
- **One day, one update.** The day window runs 05:00 to 05:00 by default, so past-midnight work
  counts as the previous working day.
- Missed a day: `py .../today.py --date 2026-09-21` reconstructs it; each day is posted on its own.

## Files

```
skills/eod/SKILL.md            the workflow
skills/eod/scripts/erp.py      ERP API client (login, tasks, update, status, progress)
skills/eod/scripts/today.py    collects one day of real work from sessions, disk and git
```

Both scripts are Python 3 standard library only — no installs.
