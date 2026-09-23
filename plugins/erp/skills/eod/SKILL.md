---
name: eod
description: Post a work update, status and progress to the Cloudhouse ERP, picking the project, then the task, then the subtask. Signs in on first use, drafts the update from what was really done that day across every Claude Code session of that day, computes progress from the subtask description, and posts only what the user approved or edited. Use when the user says "/erp:eod", "post my daily update", "end of day update", "update ERP", "log today's work", "daily work update", or asks to change a subtask's status or progress in the ERP.
---

# End-of-day ERP update

Drill down — **project → task → subtask** — then draft, review, post. Every ERP call goes
through `scripts/erp.py`; every command prints one JSON object with `"ok": true|false`, so parse
it rather than guessing.

Run commands as `py "<skill dir>/scripts/erp.py" <subcommand>` (`python` if `py` is missing).

**Header rule:** every question you ask and every list you show starts with the signed-in
account, so the user always knows which login is about to write:

```
Signed in: akhil@cloudstick.io · Backend Developer · api.cloudhousetechnologies.com
```

## 1. Session check — before anything else

```
py scripts/erp.py whoami
```

**Already signed in** (`ok: true`) → print the header line above and go to step 2. Do not ask
for credentials, do not ask for a URL.

**Not signed in** (`ok: false`), or `token_fresh: false` with `can_auto_refresh: false`:

1. Ask the user for their **email** in chat (that is not a secret).
2. Open a login window so the password is typed into a real console, never into this chat:

   ```
   cmd //c start "ERP login" cmd //k py "<skill dir>/scripts/erp.py" login --email <email>
   ```

   The window shows the ERP URL (built in — the user never types it) and asks for the password
   with hidden input.
3. Tell the user: "Enter your password in the login window, then say ready."
4. When they say so, run `whoami` again and print the header line.

Never ask for, echo, or pass a password in chat or on a command line. If the user insists on
typing it here, still route it through the window — explain that a password in chat stays in the
transcript.

**Switching account:** `login --update` (it prints who is currently signed in first).
**Signing out:** `/erp:logout`, or `erp.py logout` — clears this machine's stored credentials so
the next `/erp:eod` asks for login again.

## 2. Pick the project

```
py scripts/erp.py tasks
```

**Do not use `AskUserQuestion` for this** — it shows at most 4 options, and the user has more
projects than that, so choices would silently disappear. Print **every** project as a numbered
list in your message and ask the user to reply with a number:

```
Signed in: akhil@cloudstick.io

Which project? (reply with the number)

   1. CloudHouse ERP                      2 tasks,  2 subtasks   (this repo)
   2. Thalirtea                           4 tasks, 12 subtasks
   3. Shopping App                        3 tasks, 10 subtasks
   4. Melusive — Multi-Portal Ecommerce   3 tasks,  6 subtasks
   5. ITS INFRA INDIA                     4 tasks,  6 subtasks
   6. GST - Training System               1 task,   1 subtask
   7. KSITL                               1 task,   1 subtask
   8. Freight Forwarding ERP              1 task,   0 subtasks
```

The same rule applies to the task and subtask lists in steps 3 and 4: **always print the whole
list**, never a truncated one. Only fall back to `AskUserQuestion` when there are genuinely 4 or
fewer choices, or for yes/no style confirmations.

List every project the `tasks` call returned, in the order it returned them, including any with
0 subtasks (say `no subtasks assigned`). If the count you print does not match
`len(data)`, you have dropped something — print them all.

If the current repo clearly matches one project, put it first and mark it `(this repo)` — but
still let the user choose. Never pick for them.

## 3. Pick the task

Print **every** task under the chosen project as a numbered list and ask for a number. Always
offer `0` as back.

```
Signed in: akhil@cloudstick.io · Melusive — Multi-Portal Ecommerce

Which task? (number, or 0 to pick a different project)

   1. 140  Implement New Client Requested Features    3 subtasks
   2. 118  New Update by Client                       2 subtasks
   3.  78  Client design mockups                      1 subtask
```

## 4. Pick the subtask

Print **every** subtask under the chosen task, numbered. The user may reply with several numbers
when the day's work spans more than one. `0` goes back to the task list.

```
Signed in: akhil@cloudstick.io · Melusive → Implement New Client Requested Features

Which subtask? (one or more numbers, or 0 to pick a different task)

   1. 674  Create Product Detail Page
   2. 675  Update Shop & All Category Redirection
   3. 676  Add Offline Orders Section
```

Back must work at any point before posting — the user can change project or task, and the
selection below it resets.

## 5. Fetch the detail

For each chosen subtask:

```
py scripts/erp.py subtask --subtask 674 --task 140
py scripts/erp.py updates --subtask 674 --limit 3
```

`subtask` gives the `name`, the `description` (HTML from the ERP editor, already converted to
plain text) and the **current** `status` and `progress`. `updates` shows what was already
reported, so the new update covers only what moved since.

## 6. Read what was really done

```
py scripts/today.py                          # today, this repo only
py scripts/today.py --date 2026-09-21        # a specific day
py scripts/today.py --scope "C:\path\to\repo"  # if the repo does not match the project
```

**Do not use git commits as the source of truth** — work is often committed a week later. The
collector reads **every** Claude Code session of that day (not just this chat), filtered per
entry timestamp into one local-day window, plus files changed on disk and any commits.

| field | how to read it |
|---|---|
| `sessions[].prompts` | what was asked for — the day's intent |
| `files_edited_by_claude[]` | what actually landed — the strongest evidence |
| `repos[].files_modified_today` | work done outside Claude (IDE edits) |
| `repos[].git.commits_today` | often empty; a bonus signal, never the only one |
| `repos[].git.uncommitted` | what is still in flight |

A prompt with no matching file change is **pending**, not done. `commands` is where a build or
demo URL comes from. The day window runs 05:00 → 05:00 (`--day-start`), so past-midnight work
counts as the previous working day. Never mix two days into one update.

If the collector returns nothing, say so and ask what was done. Do not invent work.

## 7. Draft

**Title** — `Work Update`, or `Work Completed` when the subtask is being closed.

**Description** — short bullet points in plain English, matching the user's own past updates:

> Variant stock fixes — bag/wishlist/PDP no longer falsely show "out of stock"; quantities capped with live stock warning; out-of-stock items stay in cart disabled instead of being deleted.
> Variant display — exact combo (e.g. Colour: Silver, Material: Gold) now shown across cart, orders, invoices & returns.
> Admin wizard — new product wizard no longer gets stuck; stock totals save correctly.

> Navigation & Flash Sale Demo Created the new Flash Sale demo page and updated the navigation bar by centering the menu links and adding automatic bold highlighting that changes as you scroll.
>
> Offer Spinner
> spinner created and return fixed for gift items

> Completed all four user portals: Stock Manager, Admin, Super Admin, and Salesman, including both frontend and backend functionality.
> Deployed the application using Docker on the server (65.20.89.79) for testing purposes.
>
> New build URL: http://sheeltron.65.20.89.79.nip.io

Rules: 2–6 lines, one line per thing done, each a short sentence or an `Area — what changed`
pair. Plain English, user-visible change, never file paths, function names or commit hashes. A
small heading line only when the work splits into separate areas. Any demo or build URL on its
own line at the end. No "Done / Pending / Next" template, no "worked on" filler.

**Progress** — from the **description**, never guessed:

1. **Has a description** — split it into the deliverables it names, mark which are finished from
   the day's evidence and earlier updates, use that fraction, and show the split:
   ```
   Progress  0% → 65%   (new page ✓, View More redirect ✓, keep filters — partial → 2.5 of 3)
   ```
2. **No description** — fall back to the subtask name, current progress and today's work. Be
   conservative and say plainly that it is an estimate.

Ignore the backend/frontend/testing/review workflow split — one person does all of it here, so
it says nothing about progress (the `subtask` command does not even return it).

Guards: never decrease stored progress unless work was reverted; keep the number inside the band
for the status (`Todo` 0, `In Progress` 1–75, `Testing` 60–90, `Review` 80–95, `Completed` 100);
`100` only with `Completed`; hours are never progress.

**Status** — exactly one of `Todo`, `In Progress`, `Backend`, `Front-end`, `Testing`, `Review`,
`Completed`. Never empty — the API accepts an empty string and blanks the field.

## 8. Show it, and post what the user approved

```
Signed in: akhil@cloudstick.io
Melusive — Multi-Portal Ecommerce → Implement New Client Requested Features

Subtask 674 — Create Product Detail Page

  1. Update    Work Update
               Product detail page built with gallery and variant selection.
               View More now redirects to it, keeping the active filters.
  2. Status    Todo → In Progress
  3. Progress  0% → 65%   (new page ✓, redirect ✓, filters partial → 2.5 of 3)

Approve all · edit 1 / 2 / 3 · skip 1 / 2 / 3 · skip this subtask · back
```

- **The user's edit is what gets posted.** If they rewrite the text, change the status or set a
  different percentage, send *their* version verbatim — never the drafted one, and never a merge
  of the two. Re-show the block after an edit and ask again.
- Nothing is sent until an explicit yes.

Then fire the calls **separately, one at a time**, printing each result before the next:

```
py scripts/erp.py update   --subtask 674 --title "Work Update" --description-file <tmp file>
py scripts/erp.py status   --subtask 674 --task 140 --status "In Progress"
py scripts/erp.py progress --subtask 674 --task 140 --progress 65
```

Write the description to a temp file and pass `--description-file` — multi-line text does not
survive Windows quoting. Attach files with a repeatable `--file <path>`. Skip any call whose
value is unchanged or was skipped. On `ok: false`, report the exact error and URL, stop that
subtask, and continue with the next one. Never retry a 4xx.

## 9. Summary

One short table: subtask, what was posted, what was skipped, what failed. Then offer another
subtask, task or project — the user often has more than one to log.

## Commands

| command | purpose |
|---|---|
| `whoami` | who is signed in on this machine, and whether the token is fresh |
| `login` / `login --update` | sign in, or switch account (email + password only; URL is built in) |
| `logout` | clear this machine's stored credentials |
| `tasks` | assigned projects → tasks → subtasks |
| `subtask --subtask <id> --task <id>` | description, current status and progress |
| `updates --subtask <id> --limit <n>` | updates already posted |
| `update` / `status` / `progress` | the only three that write |

## Rules

- Never post without an explicit yes, and post the user's edit rather than the draft.
- Never send an empty status.
- Never ask for or echo a password in chat; use the login window.
- Never propose progress without reading the subtask first.
- One day, one update. One project per run — ask again rather than mixing projects.
- Show the signed-in email on every prompt.
- Do not invent work the collector output does not support.
