# Cloudhouse Claude Code Skills

Our engineering standards, packaged as Claude Code skills. Install once, then pull updates
whenever we push a new version.

Everything ships as a single plugin named `cloudhouse`, distributed through a plugin
marketplace named `cloudhouse-skills`. This repository **is** the marketplace.

## Available skills

| Skill | What it does |
|---|---|
| `/cloudhouse:go-backend` | Go + Echo backend standard — folder layout, file naming, in-file ordering, handler structure, response envelope, migrations, config. Builds new backends, audits existing ones, and keeps edits compliant. |

More coming: React frontend, role & permission, and others. When they land you just run the
update commands below — nothing to re-install.

## Install (once per machine)

**Do not `git clone` this repo.** Claude Code clones and updates it for you — that is what
makes `/plugin update` work later. Just run the two commands below, inside Claude Code:

```
/plugin marketplace add akhil-cloudstick/claude-skills
/plugin install cloudhouse@cloudhouse-skills
```

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
offer `go-backend`.

## Use

```
/cloudhouse:go-backend
```

Say what you want after the command and the skill picks its mode:

| You say | Mode |
|---|---|
| "new backend", "add a module", "add an endpoint", "new migration" | Build |
| "review / check / restructure this backend" | Audit — reports first, changes nothing until you approve |
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
    go-backend/SKILL.md                  one directory per skill
```
