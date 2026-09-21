---
name: frontend
description: "Frontend structure standard for any framework — React, Next.js, Vue, Nuxt, Svelte, Angular. Module-wise folder layout, file and folder naming, in-file ordering, the HTTP client with one base URL and a development/production switch, per-entity service files that own every endpoint path, state and store conventions, and the page and component anatomy. Use for ANY frontend work — creating a new frontend, adding a module/page/component, writing or editing services, stores, routes or types, and for auditing an existing frontend against the standard. Pairs with /cloudhouse:backend and /cloudhouse:role-permission. Invoked as /cloudhouse:frontend."
---

# Frontend Skill — build and audit to one fixed standard

You are working under a fixed house standard. **Part B of this file is the standard.**
It is not advice and not a starting point: it is the specification. Do not substitute your own
conventions, do not "improve" the layout, and do not follow the framework scaffolder's
conventions where they contradict Part B.

The standard is deliberately framework-independent. The same product built in React, Next.js,
Vue or Angular must end up with the same module folders, the same file names, the same order
inside each file, one base URL in one place, and one service per entity that owns every URL for
it. Only the syntax changes.

Read Part B in full before writing or changing a single file.

---

## 0. First — identify the framework

Before writing anything:

1. Read the manifest (`package.json`) and identify the framework, the bundler, the router and
   the state container.
2. Look for a **router-owned folder** — `app/`, `pages/`, `routes/`, `src/app/`. Its presence
   changes §3.4 and nothing else.
3. If the project is new and the user has not said which framework, **ask once**, then proceed.

From that point every example, file name, extension and command you produce is in **that
framework's idiom only**. Never show the user code from a framework the project does not use,
and never carry another framework's naming into it.

**The examples in this document are pseudocode on purpose.** They fix the shape, the order and
the sequence — not the syntax. Translate them. The parts that are **not** pseudocode — the
folder trees in §3, the URL shapes, and the `.env` keys — are literal.

This skill is the frontend half of the house standard. The backend half is
**`/cloudhouse:backend`** (any language) or **`/cloudhouse:go-backend`** (Go + Echo);
authorization — permission stores, route guards, nav filtering — is
**`/cloudhouse:role-permission`**. Where those overlap this document, they win on their own
subject and this file points at them rather than repeating them.

---

## 1. Pick the mode

Read what the user typed after `/frontend` and choose one:

| The user asks for | Mode |
|---|---|
| a new frontend, a new module, a new page/component, a new service | **A — Build** |
| "update / check / review / restructure the current frontend" | **B — Audit** |
| anything else touching frontend code (a bug fix, a tweak) | **C — Edit** |

If it is genuinely unclear, ask once, then proceed.

---

## 2. Mode A — Build

1. Confirm the framework (§0) and say which layout you picked (§2 of Part B) in one line.
2. Create the files in this order, one module at a time:
   **module folder → types → service → store → components → page → route registration**.
   The order matters: the service defines the shape the store consumes, the store defines what
   the components read, and the page is a shell over the components.
3. Every file follows its skeleton in §5. Every call to the API goes through a service (§7).
   The base URL is touched in exactly one file (§6).
4. Run the self-check in section 5 below before reporting done.

## 3. Mode B — Audit an existing frontend

Do **not** change anything until the user approves.

1. List the tree and read enough of it to judge — at minimum the HTTP client, two services (or
   two store slices if there is no service layer), the router, one full page, one component,
   the store entry, and every env-related file.
2. Run these sweeps, which are what actually catch the damage:

   **(a) Host strings.** Search the whole repo for `http://` and `https://`. Every hit outside
   the HTTP client file is a finding. A second hardcoded host in a store slice or a raw fetch
   call means the app talks to two backends and nobody knows.

   **(b) Env vars referenced vs declared.** Collect every environment variable the code reads.
   Every one must exist in the committed example file. A variable that is read but never
   declared is `undefined` at runtime — it does not fail, it silently produces
   `undefined/uploads/photo.jpg` in an image tag or passes `undefined` as an encryption key.

   **(c) Duplicated endpoint paths.** Collect every URL path literal. Any path appearing in more
   than one file is a finding — it is the thing a per-entity service exists to prevent.

   **(d) Filename vs export.** Every file's name must equal the name it exports.

   **(e) Dead and foreign files.** Anything named `*1`, `*New`, `*-backup`, `*-old`,
   `*(previousprojectfile)*`, plus archives, editor workspace files and build artifacts inside
   the source tree.

3. Compare against Part B and produce this table, most severe first:

   | # | File | Rule broken (§) | What is wrong | Fix |
   |---|---|---|---|---|

   Check at least: layout and module ownership (§2, §3), file naming (§4), in-file ordering
   (§5), the HTTP client and the dev/prod switch (§6), services and path ownership (§7), env
   and secrets (§8), stores (§9), page anatomy (§10), components (§11), types (§12), routing
   and guards (§13).

4. Group the findings into: **(a) mechanical** — naming, import order, formatting, dead files;
   **(b) structural** — moving files into modules, extracting a service, splitting a page;
   **(c) behavioural** — hardcoded hosts, undefined env vars, a production build pointing at
   the dev API, unmemoized work in render, a page calling the client directly.

5. Then ask the user, with the counts filled in:

   > Found N violations: X mechanical, Y structural, Z behavioural.
   > 1. Fix everything (structural moves included)
   > 2. Fix mechanical + behavioural only, leave the folder structure as it is
   > 3. Fix a specific list I give you
   > 4. Leave it as is — report only
   >
   > Which one?

6. Apply only what was chosen. Structural moves go **one module at a time** — page, components,
   service and types together — and the project must still build and typecheck after each
   module. Never move ten modules and then try to fix the imports.

7. Re-run the self-check and report what is now compliant and what the user chose to leave.

## 4. Mode C — Edit

Small change, same rules. Before editing a file, check whether it already follows Part B. If it
does not, fix the part you are touching to be compliant, mention the rest in one line, and do
not silently spread the old pattern.

In particular: if you need an endpoint and the module has no service, **write the service** —
do not add one more inline URL to a store slice because that is what the file next to it does.

---

## 5. Self-check — run before saying you are done

- [ ] Every file sits in its module: `modules/<feature>/{pages,components,services,types}` (§2, §3)
- [ ] One naming convention across the whole repo; filename equals the exported name (§4)
- [ ] Imports use the path alias, grouped in blocks (§5.1)
- [ ] Module-level order: constants → types → helpers → sub-components → main component (§5.2)
- [ ] Nothing that should be module-level is declared inside the component body (§5.3)
- [ ] **The base URL appears in exactly one file** — no host string anywhere else (§6)
- [ ] **The dev/prod flag reads `false`** if this build is going to production (§6.1)
- [ ] The HTTP client sets a timeout, attaches the token, and handles 401 (§6.3, §6.4)
- [ ] Every endpoint path lives in exactly one service file (§7)
- [ ] No page, component or store calls the HTTP client directly (§7.1)
- [ ] Every env variable the code reads exists in the committed example file (§8)
- [ ] The real env file is git-ignored and **not committed** (§8)
- [ ] Stores use the typed hooks, one slice per entity, slices call services (§9)
- [ ] The page is a shell; the data work is in a component or a fetcher hook (§10)
- [ ] Props typed above the component; one component per file (§11)
- [ ] Types colocated with the module; no backend entity redeclared inline in a page (§12)
- [ ] Guarded routes agree with the navigation entries (§13, `/cloudhouse:role-permission`)
- [ ] No dead files, no archives, no editor workspace files in the source tree (§4.3)
- [ ] No comment longer than one line, and none that restates the code (§5.5)
- [ ] The project typechecks and builds clean

---

## 6. Non-negotiables

1. **One base URL, one file.** No host string anywhere else in the repo.
2. **A page never calls the HTTP client.** It calls a service.
3. **A URL path lives in exactly one service file.**
4. **One module owns its pages, components, services and types.**
5. **The filename equals the exported name.**
6. **Imports use the path alias**, never a chain of `../../..`.
7. **Module-level order: constants → types → helpers → component.** Nothing declared mid-body
   that belongs at module level.
8. **No secrets in the repo.** The example env file is committed; the real one is not.
9. **No dead files.** No `Page1`, `-backup`, `-old`, `(previousprojectfile)`, no archives, no
   editor workspace files in the source tree.
10. **The dev/prod flag is `false` on any production build.**

If the user explicitly asks for something that breaks a rule, say which rule in one sentence,
then do what they asked.

## 7. Staying on the standard for the whole session

This standard applies to every later message in the conversation, not only the one that invoked
`/frontend`. Before each new file you write or edit, re-check section 5. If the conversation has
been long, re-read the relevant section of Part B rather than working from memory.

---
---

# PART B — THE STANDARD

Everything below this line is the specification. Follow it exactly.

# Frontend Structure & Coding Standard (any framework)

This document defines how a frontend is organised and written — the folder layout, the file
names, the order of things inside each file, how the app reaches the API, and the anatomy of a
page and a component.

It is the single source of truth. When something is not covered here, copy the closest pattern
in this document rather than inventing a new one, and then add the new pattern here.

Read §2–§5 before your first file; §6 and §7 are the two you will come back to.

### How to read the examples

```
COMPONENT Name(props):        a UI component
SERVICE name:                 a module's API service
STORE name:                   a store slice
FUNC name(args) -> type:      a plain function
STATE x = initial             component-local state
DERIVED x = ...               a computed value
ON MOUNT: ...                 a mount-time side effect
ON CHANGE(a, b): ...          a side effect keyed on dependencies
RENDER: ...                   the markup the component produces
```

Folder trees, URL shapes and `.env` keys are **literal**. Everything else is a shape to
translate into the project's framework.

---

## 1. Stack baseline

The framework, the router and the state container are the team's choice, **declared once at the
top of the repo README** and then not mixed. What is fixed:

- **TypeScript, with strict type checking on.** Not "on eventually" — on. A codebase with
  `strict: false` silently accumulates thousands of implicit-any values that no later change can
  economically undo.
- **The build typechecks.** The build script runs the type checker before the bundler, so a type
  error fails the build rather than shipping.
- **A path alias to the source root**, configured in *both* the bundler config and the
  TypeScript config, and kept identical between them.
- **One package manager, one lockfile.** Two lockfiles in a repo means two different dependency
  trees depending on who last installed.
- **One UI primitive library.** Its components live in the shared primitives folder and stay
  generic (§2.4).
- **Do not add a library** for something the framework or an existing dependency already does.

Whatever the framework's generator produces (`create-next-app`, `ng generate`, a component CLI),
the output is **rearranged to match §3 and §5** before it is committed. The generator is a
typing shortcut, not the layout authority.

---

## 2. The module layout

This mirrors the backend standard deliberately. A backend module owns its controllers, models
and routers; a frontend module owns its pages, components, services and types. The same feature
has the same name on both sides, so a developer moving between them navigates by the same map.

### 2.1 What a module owns

```
modules/
	<feature>/
		pages/          the screens
		components/     the parts those screens are built from
		services/       every API call for this feature
		types/          the shapes this feature uses
		store/          optional — this feature's state slice
		hooks/          optional — this feature's own hooks
```

A module is a product area, not a screen: `invoices`, `purchase-orders`, `employees`,
`projects`. If it has one page and three components, it is still a module.

### 2.2 Shared code

```
common/
	components/     used by two or more modules
	services/       the HTTP client, and services shared across modules
	hooks/          used by two or more modules
	types/          shapes two or more modules use
	utils/          pure helpers
	layout/         shells, sidebars, headers
```

**Anything used by two or more modules moves to `common/`, never duplicated.** A module never
imports from another module's folder — if it needs something from there, that something belongs
in `common/`.

### 2.3 The graduation rule

A feature starts as a single page in the flat layout (§3.1). The moment it grows past **~3
pages**, or gains its own set of components and a service, it moves into `modules/<feature>/`
with the folders above. **Move the page, its components, its service and its types together**,
in one commit.

### 2.4 The shared primitives folder

`common/components/ui/` holds design-system primitives — button, input, dialog, table, select.

**Nothing domain-specific ever goes in there.** A component that knows what a purchase order is,
or reads a project's budget, is a module component, not a primitive. Once domain components leak
into the primitives folder, nobody can tell what is safe to change, and you end up with two
files differing only in naming style because the second author could not find the first.

A primitive:

- takes only presentational props;
- imports nothing from `modules/`;
- would make sense in a different product.

### 2.5 Rules for both layouts

- `common/`, the router registration and the app entry point are **always at the root**, never
  duplicated inside a module.
- A module may nest a sub-module when one area is genuinely its own sub-product; the sub-module
  carries the same folders.
- The framework's own conventional folders (`app/`, `routes/`, `views/`, `containers/`) do not
  replace these. Where the framework owns a routing folder, see §3.4.

---

## 3. Folder structure reference

`.<ext>` is the project's source extension. Every file keeps the base name shown.

### 3.1 Flat layout — small, single-area app

Use when the product is one area with a handful of screens.

```
<project>/
├── .env                          # never committed
├── .env.example                  # same keys, empty values, committed
├── <dependency manifest>
├── <bundler config>              # path alias lives here
├── <typescript config>           # and here, identically
│
└── src/
	├── main.<ext>                # entry point — mounts the app, nothing else
	├── App.<ext>                 # providers + router registration
	│
	├── common/
	│   ├── components/
	│   │   ├── ui/               # design-system primitives only
	│   │   └── layout/           # shell, sidebar, header
	│   ├── services/
	│   │   └── httpClient.<ext>  # THE ONLY FILE WITH A BASE URL (§6)
	│   ├── hooks/
	│   ├── types/
	│   └── utils/
	│
	├── pages/                    # one folder per screen area
	│   ├── dashboard/DashboardPage.<ext>
	│   ├── invoices/InvoicesPage.<ext>
	│   └── settings/SettingsPage.<ext>
	│
	├── services/                 # one file per entity (§7)
	│   ├── invoiceService.<ext>
	│   └── employeeService.<ext>
	│
	├── store/
	│   ├── store.<ext>           # the store instance
	│   ├── hooks.<ext>           # typed store hooks
	│   └── slices/
	│       ├── invoiceSlice.<ext>
	│       └── employeeSlice.<ext>
	│
	└── types/
		└── invoice-types.<ext>
```

### 3.2 Modular layout — the default for a real product

```
src/
├── main.<ext>
├── App.<ext>
│
├── common/
│   ├── components/
│   │   ├── ui/
│   │   └── layout/
│   ├── services/
│   │   └── httpClient.<ext>          # THE ONLY FILE WITH A BASE URL
│   ├── hooks/
│   ├── types/
│   └── utils/
│
├── modules/
│   ├── invoices/
│   │   ├── pages/
│   │   │   ├── InvoicesPage.<ext>
│   │   │   ├── InvoiceCreatePage.<ext>
│   │   │   └── InvoiceDetailPage.<ext>
│   │   ├── components/
│   │   │   ├── InvoiceTable.<ext>
│   │   │   ├── InvoiceForm.<ext>
│   │   │   └── InvoiceStatusBadge.<ext>
│   │   ├── services/
│   │   │   └── invoiceService.<ext>  # every invoice URL, and only here
│   │   ├── store/
│   │   │   └── invoiceSlice.<ext>
│   │   └── types/
│   │       └── invoice-types.<ext>
│   │
│   ├── purchase-orders/
│   │   ├── pages/  components/  services/  store/  types/
│   │
│   └── employees/
│       ├── pages/  components/  services/  store/  types/
│
├── store/
│   ├── store.<ext>                   # combines every module's slice
│   └── hooks.<ext>
│
└── routes/
	└── routes.<ext>                  # registers every module's routes
```

### 3.3 Rules

- **Zero loose files** in `modules/`, `pages/` or `components/`. Everything is in a folder that
  says what it belongs to.
- No file appears in two folders. If two modules need it, it goes to `common/`.
- Folder names are lowercase and hyphenated: `purchase-orders`, `currency-settings`.
- The same feature name is used on the backend and the frontend.

### 3.4 Frameworks that own the routing folder

Next.js, Nuxt, SvelteKit and Angular derive routes from a folder they control. **That folder
holds shells, not pages.** The real page stays in `modules/<feature>/pages/`, so the feature tree
is identical in every framework and only the shell differs.

| Framework | Router file | What it contains |
|---|---|---|
| Next.js (app router) | `app/invoices/page.<ext>` | re-export of `modules/invoices/pages/InvoicesPage` |
| Next.js (pages router) | `pages/invoices/index.<ext>` | re-export of the same |
| Nuxt | `pages/invoices/index.<ext>` | a shell rendering the module page |
| SvelteKit | `routes/invoices/+page.<ext>` | a shell rendering the module page |
| Angular | the module's route table | the component path points into `modules/` |
| Plain React / Vue router | `routes/routes.<ext>` | a route entry pointing into `modules/` |

```
# app/invoices/page.<ext> — the entire file
export { default } from "@/modules/invoices/pages/InvoicesPage"
```

Rules:

- **A router-folder file is one to three lines.** No data fetching, no markup, no state. The
  moment logic appears there, the module has been bypassed.
- Framework-specific concerns that genuinely belong to the route — metadata, loaders,
  server-side data functions — may live in the router file, and nothing else may.
- The router folder mirrors the URL, not the module tree. `modules/purchase-orders/` can serve
  `app/purchase-orders/` and `app/vendors/[id]/orders/` at once.

---

## 4. File naming

### 4.1 The table

| Item | Rule | Example |
|---|---|---|
| Module folder | lowercase, hyphenated, plural where natural | `invoices/`, `purchase-orders/` |
| Page | `<Feature>Page`, PascalCase | `InvoicesPage`, `InvoiceCreatePage`, `InvoiceDetailPage` |
| Component | PascalCase, named for what it is | `InvoiceTable`, `InvoiceStatusBadge` |
| UI primitive | the primitive library's own convention, kept as shipped | `button`, `dropdown-menu` |
| Hook | `use-<thing>` | `use-debounce`, `use-permission` |
| Service | `<entity>Service`, singular entity | `invoiceService`, `employeeService` |
| Store slice | `<entity>Slice` | `invoiceSlice`, `employeeSlice` |
| Types | `<entity>-types` | `invoice-types`, `purchase-order-types` |
| HTTP client | `httpClient` | one file, in `common/services/` |

**Pick one case convention for each kind and hold it across the whole repo.** Components in one
folder split between PascalCase and hyphenated names is a violation even though both files work.

### 4.2 The filename equals the exported name

A file called `InvoicesPage` exports something called `InvoicesPage`. Not `InvoiceDashboard`,
not `InvoiceList`, not `Invoices`.

This sounds pedantic until you search the codebase for a component you saw on screen and cannot
find the file, or you open a file expecting one thing and find another. It also makes every
import statement predictable from the path alone.

One component per file. A file that exports two components has one too many.

### 4.3 What never appears in the source tree

- Versioned duplicates: `EmployeesPage1`, `DashboardPageNew`, `ProjectDetailsPageNewdesign`
- Backups: `*-backup`, `*-old`, `*(previousprojectfile)*`, `*.orig`
- Archives: `.zip`, `.tar`, `.rar`
- Editor and tooling files: workspace files, timestamped bundler configs
- Fixtures and seed scripts mixed in with real pages

Git holds the history. A file kept "just in case" is a file the next reader has to evaluate,
and eventually one of them edits the wrong copy.

---

## 5. In-file ordering

### 5.1 Imports

Blocks separated by exactly one blank line, in this order:

```
1. framework and router
2. third-party libraries
3. UI primitives            @/common/components/ui/...
4. shared components        @/common/components/...
5. module components        @/modules/<feature>/components/...
6. store                    hooks first, then slices
7. hooks and utils          @/common/hooks, @/common/utils
8. type-only imports
9. colocated siblings       ./invoice-types
```

- **Always the path alias.** The only acceptable relative import is a sibling in the same folder
  (`./invoice-types`). A `../../../common/utils` means the file is in the wrong place, or the
  alias is not configured.
- Do not mix: a file importing one thing by alias and the next by relative path is a finding.
- Where the toolchain sorts imports automatically, accept its output and configure it once to
  match this order — but never hand-write a fourth scheme.

### 5.2 Module level

After the imports, in this order:

```
1. constants           SCREAMING_SNAKE for values, frozen where the language allows
2. types / interfaces  props types and local shapes
3. pure helpers        small functions with no state
4. sub-components      tiny presentational pieces used only by this file
5. the main component
6. the export
```

For files past roughly 150 lines, mark the sections with a **one-line** banner comment each:

```
# --- Constants ---
# --- Types ---
# --- Helpers ---
# --- Main component ---
```

One line only. No drawn separators, no paragraph explaining what constants are.

### 5.3 Inside the component

```
1. route/navigation values       params, query, navigate
2. store dispatch
3. store selectors
4. local state
5. refs
6. derived values and memos
7. effects
8. handlers                      handleXxx
9. early returns                 loading, empty, denied
10. the markup
```

**Nothing that could be module-level is declared in here.** A constant map, a column definition,
a status lookup — if it does not depend on props or state, it goes above the component (§5.2).
Declared inside, it is rebuilt on every single render, and a fresh object identity on every
render defeats memoisation in everything downstream that receives it.

This is a real pattern in the reference code: a currency-to-country map and a sort of the
company list, both declared between two effects in the middle of a component body. Neither
depends on anything the component holds.

### 5.4 Naming inside a file

| Kind | Convention | Example |
|---|---|---|
| Event handler | `handle<Thing><Event>` | `handleSubmit`, `handleStatusChange`, `handleDelete` |
| Prop callback | `on<Thing>` | `onSave`, `onOpenChange`, `onRowClick` |
| Data loader | `fetch<Thing>` | `fetchInvoices`, `fetchInvoiceById` |
| Boolean | `is` / `has` / `can` prefix | `isLoading`, `hasChanges`, `canEdit` |
| Constant | `SCREAMING_SNAKE` | `PAGE_LIMIT`, `STATUS_OPTIONS` |

Never `xxxHandler`. Never a bare lowercase loader like `getbyid`.

### 5.5 Formatting

- **Tabs**, per the house standard — set once in the editor config and the formatter, matching.
- One blank line between functions and between blocks; **never two in a row**; never a blank
  line right after an opening brace.
- **Comments: 0–1 lines, and mostly none.** The default is to write no comment. Write one only
  where the reason is genuinely not visible in the code — a business rule, a workaround, a unit, a
  warning. **One line is the hard maximum.** Never two, never a paragraph, never a block above a
  function. If a comment needs more than one line, the code needs a better name instead.
- Comments that restate the code add nothing — delete them. A generated scaffold arrives full of
  them; strip them rather than inheriting them.
- The banner comments in §5.2 (`// --- Constants ---`, `// --- Types ---`) are not affected by this
  rule. They are structural markers, not explanation, and they are one line by construction.
- **Cross-reference the backend where a value must stay in sync**: a status list that mirrors a
  server-side list gets a one-line comment naming the file it mirrors. This is the single most
  useful comment habit in the reference code and it is required here.
- No commented-out code. No emoji-decorated notes left over from a generator. No stray logging
  in committed code.

---

## 6. The HTTP client

**One file. One base URL. Everything that talks to the API goes through it.**

`common/services/httpClient.<ext>`. This is the only file in the entire repository that contains
a hostname.

### 6.1 The environment switch — the top of the file

```
# ===== ENVIRONMENT =====
# Flip this before building. false = production.
isDevelopment = false

# development API
DEV_URL  = "https://dev-api.example.com/api/v1"
# production API
PROD_URL = "https://api.example.com/api/v1"

apiUrl = isDevelopment ? DEV_URL : PROD_URL
```

Rules, and they are strict because this is a hand-operated switch:

- **The flag is the first statement in the file.** Not below the imports of a hundred-line
  header, not halfway down. First, so nobody can miss it in a diff.
- **The two URLs are adjacent, each with a comment naming its environment.** Never separated by
  other code, never only one of them commented.
- **Every URL carries the same suffix.** If production ends in `/api/v1`, development ends in
  `/api/v1`. A mismatched pair is the classic failure here — the development branch of a second
  base URL kept a path segment the production branch did not, and every development image URL
  was wrong for months without anyone noticing, because nobody builds in development mode.
- **`isDevelopment = false` before any production build.** This is on the self-check and the
  audit sweep. It is the one line in the codebase that, set wrong, points the whole app at the
  wrong backend while every test passes.
- If the app needs a second host (an asset bucket, a third-party API), it gets its **own**
  clearly-named pair of constants **in this same file** — never a hostname in a store slice, a
  component or a raw fetch call.

### 6.2 The base path belongs in the base URL

The shared prefix — `/api/v1` — is part of the base URL, not part of every call.

This is the single most repeated substring in a frontend that gets it wrong: the same eleven
characters typed at several hundred call sites, and a version bump becomes a repository-wide
find-and-replace. In the base URL it is one edit.

Consequently, **service paths start after the prefix**: `/users/12/invoice`, not
`/api/v1/users/12/invoice`. The backend standard describes its routes as
`/api/v1/users/:user_id/<entity>` — that is the same URL, split differently between the client's
base and the service's path.

### 6.3 The client instance

```
client = createHttpClient({
	baseURL: apiUrl,
	timeout: 30000,          # required — see below
})
```

**Set a timeout.** Without one, a backend that accepts the connection and never answers leaves
the request pending forever: the spinner never stops, the user has no error to act on, and no
retry is possible. Every frontend that omits this eventually gets a support ticket describing
"the page just hangs".

### 6.4 The request interceptor

```
client.onRequest(config => {
	token = storage.get("token")
	IF token:
		config.headers.set("Authorization", "Bearer " + token)
	IF config.body IS FormData:
		config.headers.delete("Content-Type")       # the client must set the multipart boundary
	ELSE IF NOT config.headers.has("Content-Type"):
		config.headers.set("Content-Type", "application/json; charset=UTF-8")
	RETURN config
})
```

Two details that are easy to get wrong:

- **Delete `Content-Type` for multipart bodies.** The HTTP library computes a boundary token and
  must set the header itself; a hand-set `multipart/form-data` without the boundary produces a
  body the server cannot parse.
- **Only set the default when the caller has not.** Overwriting unconditionally silently
  discards a per-call override, which then looks like a server bug.

### 6.5 The response interceptor

```
client.onResponse(
	response => response,
	error => {
		status = error.response?.status
		message = error.response?.data?.message        # optional-chain EVERY level
		IF status == 401 OR message == "token expired":
			storage.clear()
			redirectTo("/login")
		IF status == 403:
			surfaceDenial(error)                        # see /cloudhouse:role-permission §13
		IF error.isNetworkError:
			RETURN reject({ isNetworkError: true, message: error.message })
		RETURN reject(error)
	}
)
```

- **Optional-chain every level.** Reading `error.response?.data.message` optional-chains
  `response` and then hard-dots `data` — so any error whose body is absent (a gateway error page,
  an empty 502) throws a second error *inside the interceptor*, replacing a useful failure with
  a meaningless one.
- **Actually act on 401.** Clear the session and send the user to login. Logging it to the
  console means the user sits looking at a page whose every request is failing.
- **Tag network failures** so callers can say "cannot reach the server" rather than showing a
  validation-style error.
- When rejecting with a new object, copy the fields you need explicitly — spreading an error
  object drops its message and stack, because those are not enumerable properties.

### 6.6 The wrappers

The rest of the app never touches the client instance. It uses these five:

```
api = {
	getEvents(url, config?)           -> client.get(url, config)
	postEvents(url, data, config?)    -> client.post(url, data, config)
	patchEvent(url, data, config?)    -> client.patch(url, data, config)
	putEvent(url, data, config?)      -> client.put(url, data, config)
	deleteEvents(url, config?)        -> client.delete(url, config)
}
```

- **These names are fixed.** They are already what the existing products use; renaming them
  would touch every call site in every repository for no behavioural gain.
- **Every method takes an optional config**, including `getEvents` and `deleteEvents` — a
  missing config parameter is the reason call sites reach past the wrapper to the raw client.
- **`data` is typed** as an object, form data, or an array — never an untyped catch-all.
- Export the client instance too, but only so a service can be built on it. Nothing outside
  `services/` imports it.

---

## 7. Services — one file per entity, and it owns the URLs

### 7.1 The rule

**Every URL for an entity lives in that entity's service file, and nowhere else.** Pages,
components and store slices call the service. They never build a path, and never call `api`.

Without this, a path spreads. In the reference code the same employee endpoint is written out in
six unrelated files, and one permissions endpoint is spelled four different ways in two files.
When the backend renames a route, finding every copy is archaeology — and the one you miss fails
only on the screen nobody opened during testing.

With it, a backend route change is a one-file edit.

### 7.2 The shape

```
# modules/invoices/services/invoiceService

# Every invoice URL in the application is on this line and the ones below it.
FUNC base(userId) -> string:
	RETURN "/users/" + userId + "/invoice"

SERVICE invoiceService:

	FUNC create(userId, payload) -> Invoice:
		response = api.postEvents(base(userId), payload)
		RETURN response.data

	FUNC list(userId, params) -> InvoiceListResponse:
		response = api.getEvents(base(userId) + toQueryString(params))
		RETURN response.data

	FUNC getById(userId, invoiceId) -> Invoice:
		response = api.getEvents(base(userId) + "/" + invoiceId)
		RETURN response.data

	FUNC update(userId, invoiceId, payload) -> Invoice:
		response = api.patchEvent(base(userId) + "/" + invoiceId + "/update", payload)
		RETURN response.data

	FUNC updateStatus(userId, invoiceId, status) -> Invoice:
		response = api.patchEvent(base(userId) + "/" + invoiceId + "/status", { status })
		RETURN response.data

	FUNC remove(userId, invoiceId) -> void:
		api.deleteEvents(base(userId) + "/" + invoiceId + "/delete")
```

### 7.3 Rules

- **Function order matches the backend handler order**: `create` → `list` → `getById` →
  `update` → `updateStatus` → `remove`, then extras. The two standards line up, so a developer
  reading the controller can predict the service and the reverse.
- **One path builder at the top.** Every function composes from it; none writes the entity
  segment twice.
- **Services return the payload, not the transport response.** Callers should never unwrap
  `.data.data`. Where the backend uses the house envelope, the service unwraps it — see
  `/cloudhouse:backend` §7 for the envelope shape.
- **Services do not touch the store, show toasts, or navigate.** They fetch and return. A
  service that dispatches is no longer reusable from anywhere else.
- **Query strings are built by a shared helper**, not concatenated by hand at each call — hand
  concatenation is where unencoded values and stray `&` characters come from.
- File uploads: build the form body in the service, so the multipart detail stays out of the
  component.

### 7.4 Before and after

```
# Wrong — the same path in six files. Rename the route on the backend and
# you are searching the repository, hoping you found all of them.
# store/slices/employeeSlice:   api.getEvents(`/api/v1/users/${userId}/employee`)
# pages/ProfilePage:            api.getEvents(`/api/v1/users/${userId}/employee`)
# components/POApprovalSettings:api.getEvents(`/api/v1/users/${userId}/employee`)
# store/slices/authSlice:       api.getEvents(`/api/v1/users/${userId}/employee`)
```

```
# Right — one file knows the path; everything else knows the function.
# modules/employees/services/employeeService
FUNC base(userId): RETURN "/users/" + userId + "/employee"

# everywhere else:
employees = employeeService.list(userId, { page, limit })
```

---

## 8. Environment and secrets

### 8.1 The two files

| File | Committed? | Contents |
|---|---|---|
| `.env` | **No** — git-ignored | the real values for this machine |
| `.env.example` | **Yes** | every key the app reads, with empty values |

**The example file is not optional.** It is the only record of what the application needs. A
project without one has no way for a new developer, or a deployment, to know which variables
exist — which is exactly how an app ends up reading a variable that was never set anywhere.

### 8.2 An unset variable does not fail loudly

This is the trap. A missing environment variable is not an error — it is the value `undefined`,
and it flows onward:

- into a string template, producing the literal text `undefined/uploads/photo.jpg` as an image
  source, so every avatar in the product is a broken image;
- into a cryptographic call as the key, which either throws deep inside a library with an
  unrelated message or, worse, does not;
- into a request header, sending the string `undefined` to the server.

So: **every variable the code reads is declared in the example file**, and every variable is
**declared in the environment type definition file** so the type checker knows about it and a
typo in the name is caught at build time rather than at runtime.

### 8.3 What belongs in env, and what does not

| Value | Where |
|---|---|
| API base URL | **Not env.** The client file's dev/prod constants (§6.1) |
| Third-party publishable keys | env |
| Feature flags for a deployment | env |
| Anything secret | **Neither** — a frontend bundle is public (§8.4) |

### 8.4 A frontend has no secrets

Everything the bundle contains is readable by anyone who loads the page. A private key, an API
secret or a database credential placed in a frontend environment variable is published the
moment you deploy — the variable prefix that exposes it to the bundle is doing exactly what it
says.

Only publishable, client-safe values go in a frontend env file. Anything else belongs on the
backend, behind an endpoint.

### 8.5 Check whether the real file is already committed

Adding `.env` to the ignore file does **not** untrack a file that was committed before the rule
existed — it stays in the repository and in its history, and both reference products are in
exactly that state. Check, and if it is tracked, untrack it, rotate anything it exposed, and add
the example file in its place.

---

## 9. State and stores

- **One store**, created in one file, combining every module's slice.
- **Typed store hooks in one file**, and everything uses them — never the untyped originals. A
  codebase that mixes both loses type safety in exactly the places nobody checks.
- **One slice per entity**, named `<entity>Slice`, living in the module it belongs to.
- **Slices call services, never the HTTP client.** A slice that builds a URL has taken the
  service's job.
- **Loading and error state live in the slice**, not duplicated into component-local state. Two
  sources of truth for "is this loading" always drift.
- Keep server data and UI state separate. A slice holds what came back from the API; a dialog's
  open/closed state is component-local and does not belong in the store.
- Do not put a value in the store because it might be needed later. Local until shared.

```
STORE invoiceSlice:
	STATE: { items: [], current: null, pagination: {}, loading: false, error: null }

	ACTION fetchInvoices(userId, params):
		loading = true, error = null
		TRY:
			result = invoiceService.list(userId, params)     # the service, not api
			items = result.data
			pagination = { page: result.page, totalPages: result.total_pages }
		CATCH err:
			error = messageFrom(err)
		FINALLY:
			loading = false
```

---

## 10. Page anatomy

**A page is a shell.** Layout, heading, page-level actions, and the feature component that does
the work.

```
COMPONENT InvoicesPage():
	navigate = ROUTER.navigate
	RENDER:
		Layout:
			PageHeader(title: "Invoices", actions: [ CreateInvoiceButton ])
			InvoiceList()                 # everything real happens in here
```

The list, its filters, its pagination and its data fetching belong in `InvoiceList`, a module
component. This is what keeps pages readable and components reusable — and it is the difference
in the reference code between a 58-line page that delegates and a 3,000-line page that does not.

**A page past a few hundred lines has a component waiting to be extracted from it.**

### 10.1 Fetching

Fetch in the component that owns the data, driven by the values it depends on:

```
COMPONENT InvoiceList():
	{ items, loading, error, pagination } = STORE.select(invoice)
	STATE search = ""
	STATE page = 1
	DERIVED debouncedSearch = debounce(search, 400)
	ON CHANGE(debouncedSearch, page):
		STORE.dispatch(fetchInvoices(userId, { search: debouncedSearch, page, limit: PAGE_LIMIT }))
	IF loading:  RENDER Skeleton()
	IF error:    RENDER ErrorState(error, onRetry)
	IF isEmpty(items): RENDER EmptyState()
	RENDER: InvoiceTable(items), Pagination(pagination)
```

Rules:

- **One effect per concern**, with an accurate dependency list. Two effects that both fetch on
  mount produce two identical requests — a real pattern in the reference code.
- **Debounce with the shared hook**, from `common/hooks/`. Do not re-implement a timer in each
  page; there are three different hand-rolled versions across the reference products.
- **Always render the three non-happy states**: loading, error with a retry, and empty. An
  empty table with no message is indistinguishable from a broken one.
- Where a page needs several related values, extract a `use<Feature>Data` hook returning
  `{ data, loading, error, refetch }` rather than growing the component.

---

## 11. Components

```
# modules/invoices/components/InvoiceTable

# --- Types ---
INTERFACE InvoiceTableProps:
	invoices    Invoice[]
	loading     bool
	onRowClick  (id: string) -> void
	onDelete?   (id: string) -> void

# --- Main component ---
COMPONENT InvoiceTable({ invoices, loading, onRowClick, onDelete }: InvoiceTableProps):
	...
```

- **Props typed in a named type above the component**, destructured in the signature. Not inline
  in the parameter list — an inline shape cannot be reused, cannot be documented, and grows
  until the signature is unreadable.
- **One component per file**, named the same as the file.
- **Presentational components take data and callbacks**; they do not read the store. A component
  that selects from the store can only ever be used in one place.
- Prop callbacks are `on<Thing>`; the handlers passed to them are `handle<Thing>`.

### 11.1 Lookup maps need a fallback

A map from a server value to a label or a style must handle a value that is not in it:

```
# --- Constants ---
# Mirrors the status list in the backend invoice controller.
STATUS_STYLES = {
	draft:    { label: "Draft",    tone: "neutral" },
	pending:  { label: "Pending",  tone: "warning" },
	approved: { label: "Approved", tone: "success" },
	rejected: { label: "Rejected", tone: "danger"  },
}

FUNC statusStyle(status) -> Style:
	RETURN STATUS_STYLES[status] ?? { label: status, tone: "neutral" }
```

Always go through the accessor. Indexing the map directly — especially with a type cast that
tells the type checker the value must be a valid key — returns nothing for any status the
backend adds later, and the component crashes on a field it thought was safe. The cast silences
the one warning that would have caught it.

### 11.2 Work that repeats every render

Table column definitions, derived lists, sorted or filtered copies — anything non-trivial built
during render is rebuilt on every render, and hands every child a new object identity. Hoist it
to module level if it is static, memoise it if it depends on props or state.

---

## 12. Types

- **Colocate**: `modules/invoices/types/invoice-types` holds the invoice shapes. The module that
  owns the entity owns its types.
- **`common/types/` only for shapes two or more modules genuinely share.**
- **Never redeclare a backend entity inline in a page.** It happens because it is quick, and then
  the same entity exists in nine slightly different versions, each missing a different field, and
  no single one of them is right.
- Import types with the type-only form so they are erased from the bundle.
- Field names match the API exactly — the backend standard serialises in `snake_case`
  (`/cloudhouse:backend` §7). Do not rename fields in the type and re-map them by hand in every
  component; if the project converts casing, it converts once, in the service layer, for
  everything.
- One entity, one type. Where a form needs a subset or a partial, derive it from the entity type
  rather than writing a second independent shape.

---

## 13. Routing and guards

- **Route declarations live in one place per module**, and the root router registers one entry
  per module — the same aggregator pattern as the backend's routers (`/cloudhouse:backend` §9.4).
  Adding a page touches one registration line.
- **Lazy-load route components** so the initial bundle stays small.
- **Every route has a layout**, chosen explicitly, not assembled ad hoc inside each page.
- **Authorization is not defined here.** Route guards, the permission store, the `can()` helper
  and navigation filtering are specified in **`/cloudhouse:role-permission` §9–§13**. Use them as
  written.
- **A guarded route and its navigation entry must agree.** If a route requires a permission, the
  menu entry that points at it carries the same permission. When they disagree the user reaches a
  page from the menu and is refused by it — see `/cloudhouse:role-permission` §13.3.

---

## 14. Adding a feature — end to end

Adding **vendor contracts** to the purchase-orders area.

1. **Module folder** — `modules/vendor-contracts/` with `pages/`, `components/`, `services/`,
   `store/`, `types/`.
2. **Types** — `types/vendor-contract-types`, fields matching the API exactly.
3. **Service** — `services/vendorContractService`, one path builder plus `create`, `list`,
   `getById`, `update`, `updateStatus`, `remove`.
4. **Store** — `store/vendorContractSlice`, calling the service, holding loading and error.
   Register it in the root store.
5. **Components** — `components/VendorContractTable`, `components/VendorContractForm`.
6. **Pages** — `pages/VendorContractsPage` (shell), `pages/VendorContractCreatePage`.
7. **Route + navigation** — one entry in the module's route file, one line in the root router,
   and the nav entry with its permission metadata (`/cloudhouse:role-permission` §12). Where the
   framework owns the routing folder, add the shell (§3.4).
8. **Verify** — typecheck and build clean; the page loads; the list paginates; loading, error and
   empty states all render; and searching the repo for the contract URL returns exactly one file.

---

## 15. Anti-patterns — do not do these

| Anti-pattern | Do instead |
|---|---|
| A hostname anywhere except the HTTP client file | one base URL, one file (§6) |
| A second hardcoded host inside a store slice | the client's constants (§6.1) |
| A raw fetch call bypassing the client | go through the service, which goes through the client (§7) |
| The dev/prod URLs carrying different path suffixes | identical suffixes, adjacent, both commented (§6.1) |
| Shipping a production build with the dev flag on | the flag is on the self-check and the audit sweep (§6.1) |
| `/api/v1` repeated at every call site | fold the prefix into the base URL (§6.2) |
| No request timeout | set one, or a hung backend hangs the UI forever (§6.3) |
| Overwriting `Content-Type` unconditionally | only set it when the caller has not (§6.4) |
| Hand-setting `multipart/form-data` | delete the header and let the client set the boundary (§6.4) |
| `error.response?.data.message` | optional-chain every level, or the interceptor throws (§6.5) |
| 401 handled by logging to the console | clear the session and redirect (§6.5) |
| Spreading an error object into a new rejection | copy the fields you need; message and stack do not spread (§6.5) |
| A page or component calling `api` directly | call the service (§7.1) |
| A store slice building a URL | the service owns the path (§7.1) |
| The same endpoint path in six files | one service file owns it (§7.4) |
| A service that dispatches, toasts or navigates | it fetches and returns (§7.3) |
| Callers unwrapping `.data.data` | the service returns the payload (§7.3) |
| An env variable read but never declared anywhere | declare it in the example file and the env types (§8.2) |
| No committed example env file | commit one — it is the only record of what the app needs (§8.1) |
| The real env file committed | untrack it, rotate what it exposed (§8.5) |
| A secret in a frontend env variable | the bundle is public; put it behind a backend endpoint (§8.4) |
| The API base URL in an env variable named "DEV" pointing at production | the client's two named constants (§6.1) |
| Two store folders, or `Hooks/` beside `hooks/` | one of each, spelled one way (§3.3) |
| Domain components in the shared primitives folder | primitives stay generic (§2.4) |
| Two files differing only in naming style | one file, one convention (§4.1) |
| A local re-implementation of a shared utility | import the shared one (§2.2) |
| A component importing from another module's folder | promote it to `common/` (§2.2) |
| A router-folder file containing markup or fetching | it re-exports the module page (§3.4) |
| Filename different from the exported name | make them equal (§4.2) |
| `Page1`, `-backup`, `Newdesign`, `(previousprojectfile)` files | delete them — git has the history (§4.3) |
| Archives, workspace files or fixtures in the source tree | keep the source tree source-only (§4.3) |
| A chain of `../../..` in an import | the path alias (§5.1) |
| A constant map declared inside the component body | module level, above the component (§5.3) |
| Column definitions rebuilt on every render | hoist or memoise (§11.2) |
| An entity type redeclared inline in a page | one type, in the module that owns it (§12) |
| A status map indexed directly, with a cast to silence the checker | an accessor with a fallback (§11.1) |
| Two effects that both fetch on mount | one effect, correct dependencies (§10.1) |
| A hand-rolled debounce in each page | the shared hook (§10.1) |
| A list with no loading, error or empty state | render all three (§10.1) |
| A page of several thousand lines | extract the component (§10) |
| Untyped store hooks mixed with typed ones | typed everywhere (§9) |
| Loading state in both the slice and the component | one source of truth (§9) |
| Props typed inline in the parameter list | a named props type above the component (§11) |
| A presentational component reading the store | pass data and callbacks in (§11) |
| A guarded route whose nav entry has no permission | they must agree (§13) |
| Logging left in committed code | remove it (§5.5) |
| A comment longer than one line, or a paragraph above a function | cut it to one line, or delete it (§5.5) |
| A comment restating what the code already says | delete it — the default is no comment (§5.5) |
| A generated scaffold's comment blocks left in place | strip them, do not inherit them (§5.5) |
| Showing the user code from a framework the project does not use | detect the framework first, then stay in it (§0) |
