# Cloudhouse Claude Code Skills

Our engineering standards, packaged as Claude Code skills. Install once, then pull updates
whenever we push a new version.

Everything ships as a single plugin named `cloudhouse`, distributed through a plugin
marketplace named `cloudhouse-skills`. This repository **is** the marketplace.

## Available skills

| Skill | What it does |
|---|---|
| `/cloudhouse:go-backend` | **Go + Echo** backend standard — folder layout, file naming, in-file ordering, handler structure, response envelope, migrations, config. Builds new backends, audits existing ones, and keeps edits compliant. |
| `/cloudhouse:backend` | **Every other language** — the same standard for NestJS, Express, Laravel, Django, FastAPI, Spring, Rails. Identical folders, file naming, handler sequence, URLs, response envelope and SQL migrations; only the syntax changes. Contains no Go code. |
| `/cloudhouse:frontend` | **Frontend structure, any framework** — React, Next.js, Vue, Nuxt, Svelte, Angular. Module-wise layout (`modules/<feature>/{pages,components,services,types}`), file naming, in-file ordering, the HTTP client with **one base URL and a dev/prod switch**, and a per-entity service that owns every endpoint path. |
| `/cloudhouse:role-permission` | **Roles & permissions, backend and frontend in one contract.** Permission tables and seeding, grant defaults, token claims, permission middleware and error shapes, the permissions API — then the frontend store, `can()` helper, route guard, gate component and sidebar filtering, so a page the user can't open is **hidden**, not shown empty. Language and framework neutral. |
| `/cloudhouse:desktop-app` | **Ship the web app as a desktop app** — Windows, macOS and Linux, on an **Electron** or a **Wails v2 (Go)** core. Converts the frontend you already have *in place*: nothing in `src/` moves, `npm run dev` and the web deploy keep working, and the native layer is added beside them. Covers the single desktop bridge, per-OS build targets, versioning, publishing installers to S3-compatible storage (Linode or any other), and auto-update. |
| `/cloudhouse:mobile-app` | **Turn a mobile-layout design into a real app** — iOS and Android, on **Expo + React Native**. Works from a single `index.html` prototype or a React page laid out at phone width: strips the simulated phone frame, ports the CSS `:root` tokens 1:1 into a theme file, maps every screen to a route, and rebuilds the UI with the same module structure as a Cloudhouse frontend. Asks once whether the app runs on demo data or the real API. |

### Which one do I use?

Use `go-backend` if the project is Go. Use `backend` for anything else. They are the same
standard, so a NestJS backend and a Go backend built from these skills end up with the same
folder tree, the same routes, the same database tables and the same JSON on the wire — the
frontend cannot tell them apart.

Use `frontend` for the client side, whatever the framework. It mirrors the backend module
layout on purpose: the same feature has the same name and the same shape on both sides, so
moving between them means navigating by the same map.

Don't run two structure skills on one project. If you're unsure, just describe the project and
Claude picks the right one from the manifest it finds.

`role-permission` is different — it **stacks on top** of the structure skills and covers both
halves at once. Reach for it any time you add a permission, gate an endpoint or a page, build
the role-permission admin screen, or want an existing setup audited. It has to work on both
sides because a permission enforced on only one is the bug that produces a visible menu item
leading to an empty list.

`desktop-app` also stacks: it assumes the frontend is already on the `frontend` standard and adds
the native layer on top, rather than restructuring anything. It asks two things up front — Electron
or Wails v2, and which operating systems — and then finishes the job without stopping to ask again.
Pick Wails v2 when the application must not be reverse-engineered or resold, because its licence,
pricing and stock rules compile into a Go core instead of shipping as readable JavaScript.

`mobile-app` is the same idea for phones, but it is a rebuild rather than a wrapper: a design laid
out at phone width is read for its screens, tokens and data shapes, and the app is built natively
from them. The design stays where it is and is never edited to match the app — it is the reference
you diff each screen against. Reach for it whenever a UI exists as a mobile-shaped web page and
needs to become something installable.

Every skill works the same way: it picks a mode from what you say. **Build** (or **Convert**, on the
two app skills), **Audit** — which reports first and changes nothing until you approve — and
**Edit** for a small change. So `/cloudhouse:frontend review this app` behaves like
`/cloudhouse:go-backend review this backend`, and `/cloudhouse:mobile-app review this app` behaves
like both.

More coming. When they land you just run the update commands below — nothing to re-install.

## Install (once per machine)

**Do not `git clone` this repo.** Claude Code clones and updates it for you — that is what
makes `/plugin update` work later.

Inside Claude Code, run these **one at a time**. Run the first command, wait for
`✓ Successfully added marketplace: cloudhouse-skills`, then run the second:

```
/plugin marketplace add https://github.com/akhil-cloudstick/claude-skills.git
```

```
/plugin install cloudhouse@cloudhouse-skills
```

> **Do not paste both lines together.** `/plugin marketplace add` opens a prompt asking for the
> marketplace source. If both lines go in at once, the second command is swallowed into that
> prompt and you get `is not a valid GitHub owner/repo shorthand`. Run them separately.

The repo is public, so no GitHub login or SSH key is needed.

The install opens a details view where you pick a scope — choose **user** so the skills are
available in every project, not just the current one.

If the install summary says `Run /reload-plugins to activate.`, run:

```
/reload-plugins
```

Verify it worked:

```
/plugin
```

`cloudhouse` should be listed as installed and enabled. Typing `/cloudhouse:` should now
offer `backend`, `desktop-app`, `frontend`, `go-backend`, `mobile-app` and `role-permission`.

> The marketplace also carries a second, optional plugin called `erp`, unrelated to the
> standards. You do not need it and it is not installed unless you ask for it.

## Use

```
/cloudhouse:go-backend       # Go + Echo projects
/cloudhouse:backend          # NestJS, Express, Laravel, Django, FastAPI, Spring, Rails, …
/cloudhouse:frontend         # React, Next.js, Vue, Nuxt, Svelte, Angular, …
/cloudhouse:role-permission  # roles & permissions — backend + frontend together
/cloudhouse:desktop-app      # ship the web app as a Windows/macOS/Linux desktop app
/cloudhouse:mobile-app       # convert a mobile-layout design into an Expo iOS + Android app
```

Say what you want after the command and the skill picks its mode:

| You say | Mode |
|---|---|
| "new backend", "add a module", "add an endpoint", "new migration" | Build |
| "review / check / restructure this backend" | Audit — reports first, changes nothing until you approve |
| "make this a desktop app", "convert this design to a mobile app" | Convert |
| "add Mac / iOS", "add a screen", "wire auto-update" | Extend |
| a bug fix or a small tweak | Edit |

The standard applies for the rest of the session, not just the message that invoked it.

## Get updates

When we announce a new version:

```
/plugin marketplace update
/plugin update cloudhouse
```

The first command refreshes the catalog from GitHub; the second pulls the new plugin
version. Restart Claude Code, or run `/reload-plugins`, if prompted.

## Optional: skip the install step for the whole team

Instead of every person running `/plugin marketplace add`, the marketplace can be
registered centrally in a shared `settings.json` (user, project, or managed scope):

```json
{
  "extraKnownMarketplaces": {
    "cloudhouse-skills": {
      "source": {
        "source": "github",
        "repo": "akhil-cloudstick/claude-skills"
      }
    }
  },
  "enabledPlugins": {
    "cloudhouse@cloudhouse-skills": true
  }
}
```

With this in place the marketplace is known and the plugin is enabled automatically.

## Contributing a change

1. Edit the skill under `plugins/cloudhouse/skills/<skill-name>/SKILL.md`.
2. Bump `version` in `plugins/cloudhouse/.claude-plugin/plugin.json`. **This is required** —
   `/plugin update` is a no-op for everyone else if the version string is unchanged.
3. Validate before pushing:
   ```bash
   claude plugin validate ./plugins/cloudhouse --strict
   ```
4. Commit and push to `main`.

### Adding a whole new skill

Create `plugins/cloudhouse/skills/<new-skill>/SKILL.md` with YAML frontmatter:

```markdown
---
name: react-frontend
description: "What it covers, and when Claude should reach for it. Invoked as /cloudhouse:react-frontend."
---
```

> **Always wrap `description` in double quotes.** YAML cannot parse a colon-followed-by-space
> inside an unquoted value, so a description like `Use for ANY work: creating a page` breaks
> the whole frontmatter. It fails **silently** — the skill still loads, but with no name and no
> description, so Claude will never pick it up on its own. This has already caught us once.
> `claude plugin validate --strict` detects it; run it before every push.

Then bump the version and push. `marketplace.json` does **not** need to change — skills are
auto-discovered from the `skills/` directory.

## Repository layout

```
.claude-plugin/marketplace.json          the catalog (this repo is the marketplace)
plugins/cloudhouse/
  .claude-plugin/plugin.json             plugin manifest + version
  skills/
    backend/SKILL.md                     one directory per skill
    desktop-app/SKILL.md
    frontend/SKILL.md
    go-backend/SKILL.md
    mobile-app/SKILL.md
    role-permission/SKILL.md
```
