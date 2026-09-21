---
name: desktop-app
description: "Desktop application standard — turn an existing React web application into a Windows, macOS and Linux desktop app with an Electron or a Wails v2 (Go) native core, without creating a second project and without losing the website. Covers the additive folder layout, the single desktop bridge, the script names, per-OS build targets, versioning, publishing installers to S3-compatible object storage (Linode and any other), and the auto-update feed. Use for ANY desktop app work — converting a web app, adding an OS target to one that already ships, wiring auto-update or the release upload, and auditing an existing desktop app against the standard. Pairs with /cloudhouse:frontend. Invoked as /cloudhouse:desktop-app."
---

# Desktop App Skill — convert, ship and audit to one fixed standard

You are working under a fixed house standard. **Part B of this file is the standard.**
It is not advice and not a starting point: it is the specification. Do not substitute your own
conventions, do not "improve" the layout, and do not follow a tool's scaffolder where it
contradicts Part B.

The standard covers two native cores — **Electron** and **Wails v2** — and the same product built
on either must end up with the same folders, the same file names, the same scripts, the same
release pipeline and the same update behaviour. Only the native folder's contents change.

One thing matters more than everything else in this file, so it is stated before the standard:

> **The desktop app is added to the web app you already have. It does not replace it.**
> There is no second project, no second folder, no fork. The web application keeps building and
> keeps deploying exactly as it did the day before the conversion.

Read Part B in full before writing or changing a single file.

---

## 0. First — identify what already exists

Before asking the user anything:

1. **Read the manifest** (`package.json`). Note the framework, the bundler, the current `scripts`,
   and whether `main`, `build`, `electron` or `electron-builder` already appear.
2. **Detect the native core**, if there is one:
   - `electron/` + a `"main"` field + `electron-builder` → **Electron**
   - `wails.json` + `go.mod` → **Wails v2**
   - neither → the app is web-only and this is a conversion (Mode A)
3. **Detect which OS targets already ship.** Read the builder config's `win` / `mac` / `linux`
   blocks and look at what is actually in the output folder. A project with only an `.exe` built is
   the common "I already did Windows, now I need Mac" case — that is Mode B, not a fresh conversion,
   and the folder structure is already settled.
4. **Check the frontend structure**, against `/cloudhouse:frontend §3`. The desktop layer sits on
   top of the web app, so if the web app is not on the standard, the desktop layer inherits the
   mess. If `src/` does not follow `/cloudhouse:frontend §3`, say so in one line and run that
   skill's audit flow — findings table, three buckets, four-option menu — before scaffolding
   anything. Only continue once the user has chosen what to do about it.

State what you found in one line — the stack, the OS targets already built, and whether the
frontend is on the standard — and then continue.

---

## 1. Pick the mode

Read what the user typed after `/desktop-app` and choose one:

| The user asks for | Mode |
|---|---|
| "make this web app a desktop app", "build an exe", "add Electron / Wails" | **A — Convert** |
| "add Mac / Linux", "wire auto-update", "change the release bucket", "cut a release" | **B — Extend** |
| "update / check / review this desktop app" | **C — Audit** |
| anything else touching the desktop layer (a bug fix, a tweak) | **D — Edit** |

If it is genuinely unclear, ask once, then proceed.

---

## 2. Then establish the stack — Electron or Wails v2

This applies in **every** mode, not only a conversion. Never write a line of native code before it
is settled.

Detect first (§0.2). If detection is unambiguous, say which stack the project is on in one line and
move on — do not ask a question the repository already answers.

If the project has no native layer yet, or detection is ambiguous, **ask, and offer exactly two
options**. Nothing else is on the menu for now:

- **Electron** — the normal business application. The native side is a Node main process. Fastest
  to get running, the widest ecosystem, the largest binary. Its weakness is that the application
  ships as readable JavaScript, and anyone can extract it from the installer in seconds.
- **Wails v2** — for an application that must not be reverse-engineered, edited or resold. The
  valuable logic compiles into a Go core as machine code: licence and seat checks, pricing, tax and
  stock rules, an encrypted local database, hardware access. Roughly 15 MB, starts in under a
  second. Move to v3 when it reaches a stable release, not before.

If the user has not said and the product is security-sensitive — licensing, seat metering, offline
money, prices the client must not be able to edit — recommend **Wails v2** and say why in one line.
Be honest about the limit while you do: no desktop software is reverse-proof, and the reason the
approach works is that the server stays the final authority, so a cracked client still cannot forge
valid data.

If a project already on one stack is asked to move to the other, say in one line that this is a
rewrite of the native layer rather than a setting, and confirm before starting.

### The stack never changes the structure

The folder layout (§2 of Part B), the file names and the script names (§4) are **identical** under
Electron and under Wails v2. Only the native folder differs — `electron/` holding Node, or `core/`
holding Go.

Do not accept a scaffolder's own layout where it contradicts Part B. `wails init` is the specific
trap: it generates its own project shape, with Go files at the repository root and the web
application demoted to a `frontend/` subfolder inside it. That is exactly the separate-project
outcome this standard exists to prevent. Generate into the existing project and keep Part B's
layout, the same way `/cloudhouse:frontend §0` refuses a framework generator's conventions.

The same rule applies inside `src/`: it stays a `/cloudhouse:frontend §3` tree under either stack,
and the bridge file (§3) is the only thing either stack is allowed to add to it.

---

## 3. Mode A — Convert an existing web app

Say in one line, before anything else, what the conversion will and will not do: **nothing in
`src/` moves, `npm run dev` and the web build keep working exactly as they do today, and the
desktop layer is added beside them.** The user needs to hear this, because the thing they are
worried about is losing the website.

Then ask the rest of the interview — once, in this order, and having already settled the stack (§2):

1. **Which OS targets?** Windows, macOS, Linux — any one, any combination, or all three.
   Build **only** what was chosen. Never all three by default: two of them will be untested, and an
   untested installer on the download page is worse than no installer.
2. **Where do releases publish?** The S3-compatible endpoint, region, bucket and folder (§8 of
   Part B). Offer Linode — `https://<region>.linodeobjects.com` — as the default, and say plainly
   that any S3-compatible storage works and that switching later is a change to the env file, not
   to the code.

**Once those are answered, stop asking and finish the job.** Do not return with another question
between every file. Scaffold the native layer, wire the bridge, add the scripts, configure the
chosen targets, write the release scripts and the updater, add the CI workflow, then run the
self-check (§7) and report.

Create things in this order — it matters, because each step is what the next one consumes:

**bridge → native entry → window + preload/bindings → scripts → build targets → release scripts →
updater → CI.**

---

## 4. Mode B — Extend an app that already ships

The structure is settled and the app is in the field. Change only what was asked for, and protect
the clients who already have it installed.

- **Adding an OS target.** Add only that target's block to the builder config, add its
  `build:<os>` script if it is missing, add its runner to the CI matrix, and check the platform
  pitfalls in §10 and §9 before declaring it done. Do not quietly enable the third platform
  because the config makes it easy.
- **Wiring or changing the updater.** The feed lives beside the installers in the same bucket
  folder (§8). Check the publish URL against the bucket and folder in the env file **by hand**
  before shipping — nothing enforces that they agree (§8), and if they disagree the installed
  clients either update from the wrong place or never see the update at all.
- **Changing the release bucket.** Change the env keys and the publish URL together, in one
  commit. Then re-upload the current release to the new bucket before pointing anything at it, or
  every installed client's next check fails against an empty folder.
- **Cutting a release.** Version, tag, build, upload, verify (§7 and §8 of Part B). Verify is not
  optional — a feed naming a file that is not in the bucket breaks updates for every installed
  client and reports nothing.

---

## 5. Mode C — Audit an existing desktop app

Do **not** change anything until the user approves.

### 5.1 The sweeps

Run all of them. Each one names the failure it catches — report the finding in those terms, not as
a style preference.

**(a) Native code in the renderer.** Search `src/` for `window.electron`, `ipcRenderer`, `require(`,
`window.go.`, `wailsjs` and `runtime.`. Every hit outside the single bridge file is a finding. This
is the sweep that matters most: each one of those hits is a line that throws in a browser, and the
website is the thing the conversion promised not to break.

**(b) The web app still works.** `dev` and `build` still mean what they meant before the
conversion. The web build still writes to its own folder. `base` and the router were not switched
globally to suit `file://` loading — if they were, the deployed website is serving broken asset
paths right now.

**(c) Script names.** The added names (§4 of Part B) are present and do what they claim. A
`build:mac` that quietly builds all three is a finding.

**(d) Build-target drift.** The targets configured versus the targets the product actually ships.
Both directions are findings: a target built and never tested, and a target promised on the
download page but not in the config.

**(e) Publish coupling.** The `publish` URL in the builder config versus `S3_BUCKET` and
`S3_FOLDER` in the environment. Nothing enforces that these agree. This is the single most fragile
point in the whole pipeline and it fails silently, in the field, weeks later.

**(f) Version comparison.** A check written as `currentVersion !== remoteVersion` rather than a
real semver-greater comparison. String inequality means a *downgrade* sitting in the bucket reads
as "update available", and every client will happily install it.

**(g) Undeclared dependencies.** Anything imported but missing from `package.json`. It works on the
developer's machine because some other package happens to pull it in, and it breaks the first time
the dependency tree shifts or CI installs clean.

**(h) Signing.** Missing code-signing configuration, and whether the certificate has actually been
started (§10). Unsigned means Windows warns every user on every install, and it means macOS
auto-update does not work at all.

**(i) Secrets.** Any credential committed to the repository. A committed example env file, with the
same keys and empty values. An access key in the repo is rotated, not deleted — deleting it from
the working tree leaves it in the history.

**(j) Comments.** Blocks of generated explanation left in `electron/`, `core/`, `scripts/` or the
CI workflow (§12 of Part B).

### 5.2 Report and ask

1. Write the findings in one table, most severe first:

   | # | File | Rule broken (§) | What is wrong | Fix |
   |---|---|---|---|---|

2. Group them into: **(a) mechanical** — script names, artifact naming, config tidiness, comments;
   **(b) structural** — splitting the build outputs, extracting a bridge, moving native code out of
   the renderer; **(c) behavioural** — a broken website, a broken updater, the wrong OS targets, a
   release pointing at the wrong bucket, a credential in the repo.

3. Then ask the user, with the counts filled in:

   > Found N violations: X mechanical, Y structural, Z behavioural.
   > 1. Fix everything (structural moves included)
   > 2. Fix behavioural + mechanical only, leave the build layout as it is
   > 3. Fix a specific list I give you
   > 4. Leave it as is — report only
   >
   > Which one?

4. Apply only what was chosen. Do the behavioural fixes first — they are the ones costing something
   today. After each one, confirm the web app still builds and the desktop app still starts. Never
   change the build outputs, the bridge and the updater in one pass and then try to work out which
   of the three broke the app.

5. Re-run the self-check (§7) and report what is now compliant and what the user chose to leave.

---

## 6. Mode D — Edit

Small change, same rules. Before editing a file, check whether it already follows Part B. If it
does not, fix the part you are touching to be compliant, mention the rest in one line, and do not
silently spread the old pattern.

In particular: if a component needs something native and the bridge has no method for it, **add the
method to the bridge** — do not reach for `window.electron` in the component because the file next
to it already does. That one shortcut is what turns the website into a blank screen.

---

## 7. Self-check — run before saying you are done

- [ ] `npm run dev` still starts the web app in a browser, unchanged (§3)
- [ ] `npm run build` still produces the web deploy artifact, in its own folder (§2, §3)
- [ ] Nothing under `src/` was moved or renamed; exactly one file was added to it (§3)
- [ ] **No renderer file touches the native runtime except the bridge** (§3)
- [ ] The app renders in a browser with desktop-only controls hidden, not throwing (§3)
- [ ] `npm run start` opens the app in a desktop window (§4)
- [ ] Only the OS targets the user chose are configured and built (§2 of Part A, §11)
- [ ] The renderer build, the web build and the installers land in three different folders (§2)
- [ ] The artifact name contains no spaces (§7)
- [ ] The version exists in exactly one place (§7)
- [ ] **The publish URL and the bucket + folder env values agree** — checked by hand (§8)
- [ ] The update check uses a semver-greater comparison, never `!==` (§9)
- [ ] The updater's six events are all relayed, and all unsubscribed (§5, §9)
- [ ] `contextIsolation` on and `nodeIntegration` off, or the Wails equivalent (§5)
- [ ] Every env key the code reads is in the committed example file, with an empty value (§8)
- [ ] No credentials committed; the real env file is git-ignored (§8)
- [ ] No comment longer than one line, and none that restates the code (§12)
- [ ] The project typechecks, the web build is clean, and the desktop build produces an installer

---

## 8. Non-negotiables

1. **The web app keeps working.** `dev`, `build` and the deploy are the same after the conversion
   as before it.
2. **One folder.** No second project, no `frontend/` subfolder, no fork of the source.
3. **Nothing in `src/` moves.** The conversion adds one file to it and changes nothing else.
4. **One bridge.** Exactly one file in the renderer touches the native runtime; everything else
   asks it.
5. **The bridge degrades in a browser.** A missing native runtime hides a control; it never throws.
6. **The stack does not dictate the structure.** A scaffolder's layout loses to Part B.
7. **Build only the OS targets that were asked for.**
8. **One version, in one place**, and the artifact, the feed and the tag all derive from it.
9. **Never hand-edit an update feed.** It is generated, checksums and all.
10. **No secrets in the repo.** The example env file is committed; the real one is not.

If the user explicitly asks for something that breaks a rule, say which rule in one sentence, then
do what they asked.

## 9. Staying on the standard for the whole session

This standard applies to every later message in the conversation, not only the one that invoked
`/desktop-app`. Before each new file you write or edit, re-check section 7. If the conversation has
been long, re-read the relevant section of Part B rather than working from memory.

---
---

# PART B — THE STANDARD

Everything below this line is the specification. Follow it exactly.

# Desktop Application Structure & Release Standard (Electron or Wails v2)

This document defines how a Cloudhouse web application becomes a desktop application — what is
added to the project, what is never touched, how the renderer reaches the native layer, how the
application is built per operating system, how installers are published, and how an installed
client updates itself.

It is the single source of truth. When something is not covered here, copy the closest pattern in
this document rather than inventing a new one, and then add the new pattern here.

Read §2, §3 and §4 before your first file. §8 and §9 are the two you will come back to.

### How to read the examples

```
SCRIPT name:                  a package manifest script
BRIDGE method(args):          a method the renderer calls on the native layer
NATIVE handler(name):         a handler on the native side
EVENT name                    an event the native layer pushes to the renderer
FUNC name(args) -> type:      a plain function
CONFIG key = value            a build or tool configuration value
ON START: ...                 something that happens at application launch
```

Folder trees, script names, env keys and file names are **literal**. Everything else is a shape to
translate into the project's stack.

---

## 1. Stack baseline

The renderer is an ordinary Cloudhouse frontend and follows `/cloudhouse:frontend` in full — that
skill wins on everything inside `src/`, and this document does not restate it. What this document
adds is fixed:

- **One of two native cores**: Electron with `electron-builder` and `electron-updater`, or
  Wails v2 with Go. Declared once, at the top of the repo README, and then not mixed.
- **The renderer is the same code in both cases.** Nothing in `src/` knows which core it is
  running under, except the bridge (§3).
- **TypeScript stays strict**, and the desktop build typechecks before it bundles. A build that
  ships a type error to a client's machine cannot be hot-fixed the way a website can — they have to
  download a new installer.
- **One package manager, one lockfile.** CI installs clean, and two lockfiles mean CI and the
  developer are building different applications.
- **Do not add a native library** for something the core already does. Electron has dialogs, a
  window state, a tray, a shell opener and a power monitor; Wails has the equivalents.

Whatever a scaffolder produces — `wails init`, an Electron template, a CI generator — the output is
**rearranged to match §2 and stripped of its comments (§12)** before it is committed.

---

## 2. Folder structure — what the conversion adds

The web application already exists. Everything marked **NEW** is added by the conversion;
everything else is what you already have, untouched.

```
<project>/                             the folder that already exists — not moved, not renamed
├── .env                               existing; the S3_* keys are appended
├── .env.example                       NEW if absent — the same keys, empty values, committed
├── package.json                       existing; scripts, "main" and the build block are added
├── vite.config.<ext>                  existing; the desktop-only settings go in a mode (§3)
├── global.d.ts                        NEW — the renderer ↔ native contract
│
├── src/                               UNTOUCHED — a /cloudhouse:frontend §3 tree
│   └── common/
│       └── services/
│           └── desktopBridge.<ext>    NEW — THE ONLY FILE THAT TOUCHES THE NATIVE RUNTIME
│
├── electron/                          NEW — Electron only. Plain ESM, never bundled.
│   ├── app.js                         entry point; single-instance lock, lifecycle
│   ├── mainWindow.js                  the window, and the window IPC
│   ├── preload.js                     contextBridge, with explicit channel allowlists
│   ├── update.js                      the updater
│   ├── state.js                       lifecycle flags shared across the main process
│   └── constants.js
│
├── core/                              NEW — Wails v2 only. The compiled Go core.
│   ├── main.go                        entry point; window options, bindings registration
│   ├── app.go                         the bound struct — every method the renderer can call
│   ├── licence/                       licence and seat logic (§6)
│   ├── storage/                       the encrypted local database (§6)
│   └── update/                        the updater (§9)
│
├── build/                             NEW — icons, entitlements, signing assets
├── scripts/                           NEW — upload, verify and tag
│   ├── upload.js
│   ├── download.js
│   └── tag.cjs
├── .github/workflows/release.yml      NEW — the per-OS build matrix
│
├── dist/                              existing — the WEB build output, still the web artifact
├── dist-desktop/                      NEW — the desktop renderer build
└── release/                           NEW — installers and the update feed
```

### 2.1 Three output folders, not one

This is the rule people break first, and it is why it is stated before anything else.

- `dist/` is the **website's** build output. It is what the web deploy uploads. The desktop build
  must never write here, or a desktop build immediately before a deploy ships a `file://`-relative,
  hash-routed bundle to the public website.
- `dist-desktop/` is the **renderer build the installer packages**. It is built with different
  settings (§3) and it is never deployed anywhere.
- `release/` is the **installers and the update feed**. The uploader reads this folder (§8).

The reference implementation used one folder for the renderer bundle and the installers, which
forced the uploader to guess what to upload by file extension. Three folders, and the uploader
uploads everything in `release/`.

### 2.2 Rules

- **Zero native code outside the native folder.** `electron/` or `core/` holds all of it.
- **`electron/` is never bundled.** It ships as source, listed in the builder's `files` array, and
  it is plain ESM. Do not add a second bundler for the main process.
- **`core/` is Go and is compiled.** Nothing in it is readable in the shipped binary — that is the
  entire reason for choosing the stack (§6).
- **Folder names are exactly as above.** Not `main/`, not `desktop/`, not `src-electron/`.
- The native layer never imports from `src/`, and `src/` never imports from the native layer.
  The bridge and `global.d.ts` are the whole contract between them.

---

## 3. The conversion is additive

The web application and the desktop application are the same source, built twice, with different
settings. Everything in this section exists to keep that true.

### 3.1 What may not change

- **`npm run dev` is not modified.** Whatever it did before the conversion, it does after: the dev
  server, in a browser, the same application.
- **`npm run build` is not modified.** Same command, same output folder, same deploy.
- **Nothing in `src/` moves or is renamed.** The conversion adds exactly one file inside it.
- If the user asks for a change to either script, say in one line that this breaks the web deploy
  and confirm before doing it.

### 3.2 The two settings the web build cannot inherit

Two things the desktop build needs are actively wrong for a website. Neither is applied by editing
the shared configuration — both are applied **only to the desktop build**, through a build mode:

| Setting | Desktop needs | Website needs | Why |
|---|---|---|---|
| Asset base path | `'./'` — relative | the deploy path | A packaged app loads from `file://`, where an absolute `/assets/...` path resolves to the filesystem root and every asset 404s. A website served from a subpath breaks under `'./'`. |
| Router | hash | whatever it uses today | `file://` has no server to resolve a deep path, so a history router shows a blank screen on any route but the first. |

```
CONFIG base = isDesktopBuild ? './' : <the existing value>
CONFIG outDir = isDesktopBuild ? 'dist-desktop' : 'dist'
```

The router is chosen the same way, read from the bridge (§3.3) rather than from a build flag, so
that the same bundle behaves correctly whether it is opened in a window or served on the web.

### 3.3 The bridge — one file, and only one

Every call into the native layer goes through `src/common/services/desktopBridge`. This is the same
rule as the one base URL in `/cloudhouse:frontend §6`, for the same reason: one file knows, and
everything else asks it.

The bridge does three things:

1. **Detects the runtime.** Is there an Electron preload? A Wails runtime? Neither?
2. **Exposes one interface**, identical under both stacks, so no caller ever branches on which core
   is running.
3. **Degrades when there is no runtime**, so the same code runs in a browser.

```
SERVICE desktopBridge:

	DERIVED isDesktop = the native runtime is present
	DERIVED platform  = "win" | "mac" | "linux" | "web"

	FUNC printReceipt(bill) -> result:
		IF NOT isDesktop: RETURN { ok: false, reason: "not available in the browser" }
		RETURN NATIVE print(bill)

	FUNC checkForUpdate() -> updateInfo | null:
		IF NOT isDesktop: RETURN null
		RETURN NATIVE checkUpdate()

	FUNC onUpdateEvent(name, handler) -> unsubscribe:
		IF NOT isDesktop: RETURN a no-op unsubscribe
		RETURN NATIVE subscribe(name, handler)
```

Rules:

- **A missing runtime returns a value. It never throws.** A component that calls `printReceipt` in
  a browser gets `{ ok: false }` and shows a message. It does not crash the page.
- **Every subscribe returns its own unsubscribe.** The caller unsubscribes on unmount, including
  the no-op one, so that the cleanup path is the same in both environments.
- **Desktop-only UI is hidden, not disabled.** Window controls, the update button and the printer
  settings do not render at all when `isDesktop` is false. A disabled button in a browser is a
  question the user cannot answer.
- **No component, page, store or service imports the native runtime directly.** Not
  `window.electron`, not `window.go`, not the generated Wails bindings. Those imports are what the
  audit sweeps for first (§5.1 of Part A), because each one is a line that throws on the website.

---

## 4. The scripts

Existing and untouched:

| Script | What it does |
|---|---|
| `dev` | the web app, in a browser — exactly as before the conversion |
| `build` | the web deploy artifact, into `dist/` — exactly as before |

Added:

| Script | What it does |
|---|---|
| `start` | the desktop app in development — dev server plus the native shell |
| `build:desktop` | the renderer, desktop settings, into `dist-desktop/` |
| `build:win` | `build:desktop` then package for Windows, into `release/` |
| `build:mac` | the same, for macOS |
| `build:linux` | the same, for Linux |
| `build:all` | all three — **only** when all three were asked for |
| `release` | build the chosen targets, then `upload` |
| `upload` | push `release/` to the bucket (§8) |
| `download` | pull the feed back and verify every file it names (§8) |
| `tag` | create and push the version tag, which triggers CI (§7, §11) |

These names are fixed, and they are the same under Electron and under Wails, so the command never
depends on which core the product uses. If one of them already exists in the project and means
something else, say so in one line and choose an adjacent name rather than overwriting it.

`start` runs the dev server and the native shell together and waits for the server before opening
the window. A window that opens first shows a blank frame and, in the packaged-app case, caches the
failure.

---

## 5. The renderer ↔ native contract

### 5.1 Electron

```
CONFIG contextIsolation = true
CONFIG nodeIntegration  = false
CONFIG sandbox          = false   only if a preload dependency genuinely requires it
```

These are not negotiable. `nodeIntegration: true` gives any script that reaches the renderer — an
injected one, a compromised dependency — the full filesystem and process API of the machine.

The preload exposes a **named allowlist**, never a generic pass-through:

```
CONST allowedSend    = ["window-minimize", "window-close", …]
CONST allowedReceive = ["update-available", "update-download-progress", …]

BRIDGE send(channel, payload):
	IF channel NOT IN allowedSend: RETURN
	forward to the main process

BRIDGE on(channel, handler) -> unsubscribe:
	IF channel NOT IN allowedReceive: RETURN a no-op unsubscribe
	subscribe, and RETURN a function that removes this exact listener
```

Exposing `ipcRenderer.send` directly, or an allowlist built from a wildcard, defeats
`contextIsolation` entirely — the boundary is only worth what the allowlist is.

`on()` returns its own unsubscribe closure. A component that subscribes on mount and cannot remove
exactly its own listener leaks one per mount, and after a few navigations every update event fires
its handler a dozen times.

### 5.2 Wails v2

Methods are bound on the app struct in `core/app.go`; Wails generates the TypeScript. The generated
bindings are imported **only** by the bridge file — never by a component, which is the same rule as
Electron's, for the same reason.

Events use the Wails runtime and are wrapped so that subscribing returns an unsubscribe, matching
§5.1 exactly. The bridge's interface is identical under both stacks; that is the whole point.

### 5.3 The types

`global.d.ts` holds the shape of whatever the native layer exposes to the renderer. It is the only
place that shape is written down, and the bridge is typed against it. A bridge typed as `any` is a
bridge that compiles after the native side changed and fails at runtime on a client's machine.

---

## 6. What belongs in the compiled core — Wails v2

If the product is on Wails, it is on Wails for a reason, and putting the valuable logic in the
renderer wastes the entire decision. JavaScript ships as readable text and can be extracted from
any installer in seconds; compiled Go cannot.

In the Go core:

- **Licence and seat logic.** Key validation, expiry, how many sessions are allowed.
- **Pricing, tax and stock rules.** Anything a client could profit from editing.
- **The local database, encrypted.** A client must not be able to open the local file and rewrite
  their own stock, prices or history.
- **Hardware access.** Printers, cash drawers, card terminals, serial ports.
- **The signed key material.** Server-signed, so that editing a seat count or an expiry date breaks
  the signature.

In the renderer: screens, input, layout, and calls to the bridge. No rule worth stealing.

Two closing rules:

- **The server is the final authority.** Prices, stock and reports are validated server-side, so
  that even a fully cracked client cannot forge valid data. Every layer above this one raises the
  cost of cracking; this is the layer that makes cracking pointless.
- **Say the honest thing.** No desktop software is 100% reverse-proof. The goal is to make it more
  expensive to crack than to buy. Do not tell the user the binary is safe.

---

## 7. Versioning

**The version lives in exactly one place: `package.json`.** Three things derive from it, and none
of them is ever typed by hand:

1. the installer's filename,
2. the update feed,
3. the git tag that triggers CI (`scripts/tag.cjs` reads the manifest and pushes `v<version>`).

A version typed into a second place is a version that will disagree with the first one, and the
symptom is an update that installs and then offers itself again forever.

**The artifact name contains no spaces.** Configure it explicitly:

```
CONFIG artifactName = "<product>-<version>-<os>.<ext>"
```

The default naming produces files like `CloudHouse Agent Setup 0.2.0.exe`. That name goes into a
URL and into the update feed, where the spaces have to survive two layers of encoding and
frequently do not.

---

## 8. Publishing — S3-compatible, and configurable

Installers and the feed go to an S3-compatible bucket. Linode Object Storage is the house default;
any S3-compatible storage works, and switching is a change to the env file, not to the code.

### 8.1 The keys

```
S3_ENDPOINT=
S3_REGION=
S3_BUCKET=
S3_FOLDER=
S3_ACCESS_KEY=
S3_SECRET_KEY=
```

`.env.example` is committed with these keys and empty values. It is the only record of what the
release needs. `.env` is git-ignored and holds the real values.

An access key that reached the repository is **rotated**, not deleted — removing it from the
working tree leaves it in every clone of the history.

### 8.2 `scripts/upload.js`

Path-style addressing, signature v4, `public-read` on each object. It uploads everything in
`release/` — installers and feed files — to `<S3_FOLDER>/` in the bucket. It does not filter by
extension and does not need to, because `release/` holds nothing else (§2.1).

### 8.3 `scripts/download.js` — the verify step

It pulls the feed back out of the bucket and checks that **every file the feed names actually
exists there**. Run it after every release.

This is not a nicety. A feed that names a missing file breaks updates for every installed client,
reports nothing to anyone, and is usually discovered weeks later by a client who mentions they are
still on an old version.

### 8.4 The coupling nothing enforces

The builder's `publish` URL and `S3_BUCKET` + `S3_FOLDER` must point at the same place. **Nothing
checks this.** They are in different files, they are changed by different people, and when they
disagree the build succeeds, the upload succeeds, and the update silently never arrives.

Check them against each other by hand at every release, and change them in the same commit.

---

## 9. Auto-update

The shape is the same under both stacks, so the renderer's update UI is written once.

### 9.1 The six events

`checking` · `available` · `not-available` · `progress` · `downloaded` · `error`

All six are relayed to the renderer. A UI that only handles `available` and `downloaded` leaves the
user looking at a spinner forever whenever the check fails.

### 9.2 Electron

`electron-updater`, generic provider, pointed at the bucket folder (§8).

- `autoDownload = false`. The download is user-initiated. A background download on a shop's metered
  connection is not a decision to make on their behalf.
- The check compares versions with **semver-greater**, never `!==`. String inequality means a
  downgrade sitting in the bucket reads as an available update.
- Installing sets a **quit-for-update flag** before `quitAndInstall()`, and the window's close
  handler checks that flag and skips the "are you sure you want to exit?" confirmation. Without it
  the update stalls behind a dialog nobody is there to answer.

### 9.3 Wails v2

Wails v2 has **no built-in updater**, so the standard prescribes one:

```
ON check:
	fetch the JSON manifest from the same bucket folder
	IF semverGreater(manifest.version, currentVersion):
		EMIT available
	ELSE:
		EMIT not-available

ON download:
	download to a temporary path, EMIT progress as it goes
	verify the SHA-512 against the manifest        # a truncated download must never install
	EMIT downloaded

ON install:
	swap the binary and relaunch
```

Same six events, same semver rule, same user-initiated download.

### 9.4 The UI

One button, a state machine: `idle → checking → available → downloading → downloaded (Restart)`.

It is **hidden in a browser**, via the bridge (§3.3). It subscribes to all six events and
unsubscribes on unmount.

### 9.5 macOS

An unsigned or ad-hoc-signed macOS build **cannot auto-update** — the update mechanism rejects a
change of signing identity. Detect the platform, and degrade the control with a plain message
telling the user to download the new version. Do not leave a button that appears to work and
silently does nothing, which is what an unhandled failure looks like.

Signing macOS properly (§10) removes this limitation. Until then, say so in the UI.

---

## 10. Code signing

Two certificates, one per platform:

- **Windows** — an EV code-signing certificate. Without it, Windows SmartScreen warns every user on
  every install, and a shop owner who sees that warning phones support instead of installing.
- **macOS** — an Apple Developer ID, plus notarization. Without it the app is quarantined, and
  auto-update does not work at all (§9.5).

**The EV certificate is the longest-lead item in any desktop project.** It takes weeks of
paperwork, it has nothing to do with code, and it blocks shipping rather than building. Start it
before writing the application, not when the first release is ready.

Signing credentials are CI secrets. They are never committed and never printed in a build log.

---

## 11. CI

A tag-triggered matrix release.

- Triggered by pushing `v<version>` (§7). A manual dispatch may pick a single platform.
- **The matrix contains only the OS targets the product ships.** `windows-latest`,
  `macos-latest`, `ubuntu-latest` — the chosen ones, not all three by reflex. A runner in the
  matrix for a platform nobody tests produces an installer nobody should download.
- Install clean (`npm ci`), build the renderer, package the target, then upload.
- **The upload is gated to real release tags.** A `-test` suffixed tag builds and does not publish,
  so a release can be rehearsed end to end without touching what installed clients see.
- Platform-specific system dependencies belong in the workflow, not in a developer's head.

---

## 12. Formatting and comments

The renderer follows `/cloudhouse:frontend §5`. The native layer, the scripts and the CI workflow
follow the same rule:

- **Comments: 0–1 lines, and mostly none.** The default is to write no comment. Write one only
  where the reason is genuinely not visible in the code — a business rule, a workaround, a unit, a
  warning. **One line is the hard maximum.** Never two, never a paragraph, never a block above a
  function. If a comment needs more than one line, the code needs a better name instead.
- Comments that restate the code add nothing — delete them.
- **This is where generated scaffolding bites.** `wails init`, Electron templates, builder configs
  and CI generators all arrive full of explanatory block comments. They are stripped before the
  commit, not inherited.
- No commented-out configuration kept "in case we switch back". Git has it. A commented-out build
  target is a target the next reader has to decide about.
- No auto-generated file headers — author, date, description.

---

## 13. Converting a web app — end to end

The order to work in. Each step is what the next one consumes.

1. **Check the frontend** against `/cloudhouse:frontend §3`. Settle it before adding anything.
2. **Settle the stack** — Electron or Wails v2 (§2 of Part A).
3. **Add the bridge** — `src/common/services/desktopBridge`, browser-safe from the first line, and
   `global.d.ts` beside it (§3.3, §5.3).
4. **Add the native entry** — `electron/app.js` or `core/main.go` (§2).
5. **Add the window and the boundary** — the preload allowlist, or the bound struct (§5).
6. **Add the scripts** — `start` and `build:desktop` first; confirm both the web app and the
   desktop window run before going further (§4).
7. **Configure the chosen OS targets** — and only those (§11).
8. **Split the outputs** — `dist/`, `dist-desktop/`, `release/` (§2.1).
9. **Add the release scripts** — `upload`, `download`, `tag`, and the env keys (§7, §8).
10. **Wire the updater** — native side, then the six events, then the button (§9).
11. **Add CI** — the matrix for the chosen targets only (§11).
12. **Start the certificates** (§10). Do this on day one, not at step twelve.
13. **Verify**: the website still builds and deploys; the app still opens in a browser; the desktop
    app installs, runs and updates from the bucket.

---

## 14. Anti-patterns — do not do these

| Anti-pattern | Do instead |
|---|---|
| A second project or a `frontend/` subfolder for the desktop app | one folder, added to (§2) |
| Accepting `wails init`'s layout over this document | generate into the existing project, keep §2 (§2 of Part A) |
| Moving or renaming anything in `src/` to suit the desktop build | `src/` is untouched; add the bridge (§3.1) |
| Changing `dev` or `build` to mean the desktop build | they keep their meaning; desktop gets its own scripts (§4) |
| `window.electron` or a Wails binding imported in a component | call the bridge (§3.3) |
| The bridge throwing when there is no native runtime | return a value and degrade (§3.3) |
| A desktop-only control disabled in the browser | hide it (§3.3) |
| `base: './'` or a hash router applied to the web build too | desktop-only, via the build mode (§3.2) |
| The renderer bundle and the installers in one folder | three folders (§2.1) |
| The desktop build writing into the website's output folder | `dist-desktop/` (§2.1) |
| Spaces in the artifact name | set `artifactName` explicitly (§7) |
| The version written in a second place | one place, everything derives from it (§7) |
| `currentVersion !== remoteVersion` | a semver-greater comparison (§9.2) |
| Hand-editing the update feed | it is generated, checksums and all (§8) |
| Skipping the post-release verify | run `download` every time (§8.3) |
| The publish URL and the bucket env values changed separately | one commit, checked by hand (§8.4) |
| `nodeIntegration: true`, or a generic IPC pass-through | context isolation and a named allowlist (§5.1) |
| A subscribe with no matching unsubscribe | every subscribe returns its own (§5.1) |
| Business rules in the renderer on a Wails project | they belong in the Go core (§6) |
| Trusting the client because the core is compiled | the server is the final authority (§6) |
| Building all three OS targets when one was asked for | build what was chosen (§11) |
| A macOS update button that silently does nothing | detect it and say why (§9.5) |
| Credentials in the repository | env file, git-ignored, and rotate what leaked (§8.1) |
| Leaving a scaffolder's comment blocks in the committed code | strip them (§12) |
| Starting the code-signing certificate at release time | start it on day one (§10) |
