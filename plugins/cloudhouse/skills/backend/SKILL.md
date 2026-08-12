---
name: backend
description: "Backend structure standard for any language or framework — NestJS, Express, Laravel, Django, FastAPI, Spring, Rails. Folder layout, file naming, in-file ordering, handler body structure, response envelope, query params and form-data input, fast queries, routing grammar, SQL migrations, config layout. Use for ANY non-Go backend work — creating a new backend, adding a module/entity/endpoint, writing or editing controllers, models, routers, migrations, schedulers or config, and for auditing an existing backend against the standard. For Go + Echo backends use /cloudhouse:go-backend instead. Invoked as /cloudhouse:backend."
---

# Backend Skill — build and audit to one fixed standard, in any language

You are working under a fixed house standard. **Part B of this file is the standard.**
It is not advice and not a starting point: it is the specification. Do not substitute
your own conventions, do not "improve" the layout, and do not follow the framework's
own scaffolding conventions where they contradict Part B.

The standard is deliberately language-independent. The same product built in NestJS,
Laravel, Django or Spring must end up with the same folders, the same file names, the
same order inside each file, the same URLs, the same database tables and the same JSON
on the wire. Only the syntax changes.

Read Part B in full before writing or changing a single line of code or SQL.

---

## 0. First — identify the stack, then never mention another one

Before anything else, work out what the project is written in:

1. Look for a manifest: `package.json`, `composer.json`, `pyproject.toml` /
   `requirements.txt`, `pom.xml` / `build.gradle`, `Gemfile`, `*.csproj`.
2. Look at the existing source tree for the framework in use.
3. If the project is new and the user has not said, **ask once** which language and
   framework, then proceed.

From that point on, every example, file name, snippet, command and explanation you
produce is in **that stack's idiom only**. Do not show the user code from another
language "for comparison", and do not carry another framework's naming into the
project.

**The examples in this document are pseudocode on purpose.** They describe the shape,
the order and the sequence — not the syntax. Translate every one of them into the
project's real language before writing it to disk. Never paste a pseudocode block into
a source file.

The parts that are **not** pseudocode — the JSON response shapes (§7), the SQL in the
migrations (§10), the URL grammar (§9) and the folder trees (§3) — are literal. Those
are identical in every language and are copied exactly.

> Building a Go + Echo backend? Stop and use `/cloudhouse:go-backend` instead — it is
> the same standard with the Go implementation filled in.

---

## 1. Pick the mode

Read what the user typed after `/backend` and choose one:

| The user asks for | Mode |
|---|---|
| a new backend, a new module, a new entity/endpoint, a new migration | **A — Build** |
| "update / check / review / restructure the current backend" | **B — Audit** |
| anything else touching backend code (a bug fix, a tweak) | **C — Edit** |

If it is genuinely unclear, ask once, then proceed.

---

## 2. Mode A — Build

1. Confirm the stack (§0) and state it in one line.
2. Decide the layout using §2 of Part B (flat vs `common/` + `modules/`) and say which
   one you picked and why, in one line.
3. Create the files in this order, one entity at a time: **migration → model →
   controller → router → module aggregator → root aggregator**, then scheduler/template
   if the feature needs them (§16).
4. Every file follows its skeleton in §5. Every handler follows the input block and
   body sequence in §6. Every response uses the envelope in §7.
5. Run the self-check in section 5 below before reporting done.

## 3. Mode B — Audit an existing backend

Do **not** change anything until the user approves.

1. List the tree and read enough of it to judge — at minimum the entry point, the root
   router, one full controller, one model, one router, two migrations, and `config/`.
2. Compare against Part B and produce this table, most severe first:

   | # | File | Rule broken (§) | What is wrong | Fix |
   |---|---|---|---|---|

   Check at least: folder layout (§2, §3), file naming (§4), in-file ordering (§5),
   shared helpers in `helper.<ext>` (§5.6.1), tabs / blank lines / comments (§5.8),
   handler input block and body order (§6), status codes and no `500` (§6.7), input
   handling (§6.8), slow queries and N+1 (§6.9), response envelope (§7), model rules
   (§8), route grammar (§9), migrations and indexes (§10), config files (§11).
3. Group the findings into: **(a) mechanical** — formatting, comments, blank lines,
   naming, ordering; **(b) structural** — moving files into `modules/`, splitting a
   controller, renaming routes; **(c) behavioural** — 500s, missing pagination, N+1,
   missing indexes.
4. Then ask the user, with the counts filled in:

   > Found N violations: X mechanical, Y structural, Z behavioural.
   > 1. Fix everything (structural moves included)
   > 2. Fix mechanical + behavioural only, leave the folder structure as it is
   > 3. Fix a specific list I give you
   > 4. Leave it as is — report only
   >
   > Which one?

5. Apply only what was chosen. Structural moves go one entity at a time (controller,
   model and router together), and the project must still build after each entity.
6. Re-run the self-check and report what is now compliant and what the user chose to
   leave.

## 4. Mode C — Edit

Small change, same rules. Before editing a file, check whether the file already
follows Part B. If it does not, fix the part you are touching to be compliant, mention
the rest in one line, and do not silently spread the old pattern.

---

## 5. Self-check — run before saying you are done

Go through this list every time. If any answer is "no", fix it before reporting.

- [ ] Files are in the right folders, named after the entity, one naming convention
      across the whole repo (§3, §4)
- [ ] The triplet matches: the same entity base name in `controllers/`, `models/` and
      `routers/` (§4)
- [ ] Every file's internal order is imports → module-level vars → types → helpers →
      handlers (§5)
- [ ] Shared helpers are in the module's `helper.<ext>`, not duplicated (§5.6.1)
- [ ] Indented with **tabs**; no blank line inside any function; exactly one between
      functions; no paragraph comments; no commented-out code (§5.8)
- [ ] Every handler opens with the input block: path params → query params → vars →
      conversions/defaults — and nothing new is declared further down (§6)
- [ ] No `500` anywhere; every error is 400/401/403/404/409 with a clean sentence (§6.7)
- [ ] Filters and pagination come from query params; uploads use `data` + `files` /
      `images`; the client filename always passed through `sanitizeFileName` (§6.8, §11.2)
- [ ] Lists paginate, count and sort in SQL; no query inside a loop; no eager-loaded
      relation the list does not display (§6.9)
- [ ] Every response uses the `success` envelope; no bare arrays or raw errors (§7)
- [ ] Models are type/schema declarations only — no methods, no hooks, no queries (§8)
- [ ] Routes follow `/api/v1/users/:user_id/<entity>/:id/<action>`; paths built from a
      variable; middleware last (or absent if auth is not set up yet) (§9)
- [ ] Migration numbered `NNNN_verb_subject.sql`, has a working `Down`, indexes every
      FK / filtered / sorted column (§10)
- [ ] No hardcoded keys — everything through `.env` and `config/` (§11)
- [ ] The project's formatter and linter pass; the project builds and starts clean
- [ ] Nothing you wrote or showed contains code from a language other than this
      project's (§0)

---

## 6. Non-negotiables

These are the ones that get silently broken. Never break them, whatever the
conversation drifts into:

1. **Tabs, not spaces.** No blank lines inside a function.
2. **No `500`.** Classify the failure.
3. **The `success` envelope on every single response**, including errors and empty lists.
4. **Input block at the top of every handler.** No query param read halfway down.
5. **One entity per file**, matching base names across `controllers` / `models` / `routers`.
6. **Aggregators only aggregate.** No route declared in the root aggregator.
7. **Models hold no logic.** Routers hold no logic.
8. **SQL migrations are the schema.** Never auto-migrate, never `synchronize`, never
   `db push`. Never edit an applied file.
9. **No secrets in code.**
10. **No N+1 queries. No unpaginated lists.**

If the user explicitly asks for something that breaks a rule, say which rule in one
sentence, then do what they asked.

## 7. Staying on the standard for the whole session

This standard applies to every later message in the conversation, not only the one
that invoked `/backend`. Before each new file you write or edit, re-check section 5.
If the conversation has been long, re-read the relevant section of Part B rather than
working from memory.

---
---

# PART B — THE STANDARD

Everything below this line is the specification. Follow it exactly.

# Backend Structure & Coding Standard (any language)

This document defines **how a backend is organised and written** in our team — the
folder layout, the file names, the order of things inside each file, the shape of every
handler, and the format of every response.

It is the single source of truth. Every new file, folder, function and handler follows
the rules below. When something is not covered here, copy the closest pattern in this
document rather than inventing a new one, and then add the new pattern here.

Read §2–§5 before writing your first file; §6 and §7 are the ones you will come back to
every day; §16 is the checklist for shipping a new feature.

### Scope of this document

Folder layout, file naming, in-file ordering, function ordering, handler body
structure, response format, models, routers, migrations, config, scheduler, templates,
and the end-to-end checklist for adding a feature.

### How to read the examples

Illustrative logic is written in a neutral pseudocode. It is never valid code in any
language — translate it. The notation:

```
HANDLER Name(request):        an HTTP handler / controller action
	request.path("x")          a path parameter
	request.query("x", d)      a query parameter with default d
	request.body()             the parsed JSON body
	DECLARE a, b, c            declare every variable the handler will use
	DB.first(Model, cond)      fetch one row, or nothing
	DB.list(query)             fetch many rows
	DB.count(query)            count rows matching the same filters
	DB.transaction(tx => ...)  a database transaction
	RETURN 200 { ... }         status code + the response envelope from §7
	# comment                  a comment
```

Folder trees, URLs, SQL and JSON are **literal** — copy them as written.

---

## 1. Stack baseline

The framework and the ORM are the team's choice. What is fixed:

- **Database is PostgreSQL.** Another engine is used only when the product genuinely
  requires it, and then the SQL in §10 is adapted but the file naming and file
  structure do not change.
- **The schema lives in plain SQL migration files** (§10). The ORM's auto-migration,
  `synchronize`, `db push` or model-derived schema generation is switched **off**,
  whatever the ORM is.
- **One deployable per backend.** One dependency manifest, one entry point, one
  version of the framework.
- **The project name is short, lowercase and product-based.** Throughout this document
  it is called `myproject`.
- **Internal imports are absolute from the project root**, using the language's path
  alias or package mechanism — never long relative chains (`../../../config`). Set the
  alias up once in the project config so every file can use it.
- **Do not add a third-party library** if the job can be done with the standard library
  or a dependency the project already has.
- **Declare the stack once, at the top of the repo README** — language, framework, ORM,
  migration runner — and do not mix a second one into the same backend.

Whatever the framework's own generator produces (`nest g resource`, `php artisan
make:*`, `django-admin startapp`, `rails generate`), the output is **rearranged to
match §3 and §5** before it is committed. The generator is a typing shortcut, not the
layout authority.

---

## 2. Choosing the layout

There are exactly **two approved layouts**. Pick by the shape of the product, not by
personal preference and not by what the framework scaffolds.

### 2.1 Flat layout — single-surface project

Use when the project has **one module and one kind of user** (no separate
admin/staff/customer sides, no independent product areas).

```
controllers/   models/   routers/
```
sit directly at the project root (or the framework's source root, e.g. `src/`), next to
`config/`, `migrations/` and the entry point. Nothing is nested; every controller of
the product lives in the one `controllers/` folder, one file per entity.

### 2.2 Modular layout — multiple modules or multiple role-based surfaces

Use when **either** is true:

- the product has distinct functional modules (CRM, Projects, HR, Supports, …), **or**
- the product has different role-based surfaces (admin side, staff side, customer
  side, agent side) that need their own controllers and routes.

Then:

```
common/                 shared entities used by every module (company, employee, login, …)
  controllers/  models/  routers/
modules/
  <ModuleOrSurface>/    e.g. CRM, Projects, HumanResource, Admin, Staff, Agent
    controllers/  models/  routers/
```

Each module/surface owns the **same three folders** — `controllers/`, `models/`,
`routers/` — no exceptions, no extra folders inside a module unless the module truly
needs one (for example a chat module that also serves embeddable widgets may add a
`widgets/` folder — nothing else).

A module may nest a sub-module when one area has its own clearly separate sub-product;
the sub-module again carries the same three folders and its own `routers` aggregator.

### 2.3 Rules that apply to both

- Anything shared by two or more modules goes to `common/`, never duplicated.
- A module never imports another module's `models` unless the relation is real. An
  entity needed by two modules (Employee, Company, Customer) belongs in
  `common/models` and is imported from there.
- **Graduation rule:** a feature starts in the flat/root folders; the moment it grows
  past ~3 entities, or gains its own user surface, it moves into `modules/<Name>/`
  with the three folders. Move all three files (controller, model, router) together.
- `config/`, `auth/`, `migrations/`, `scheduler/`, `templates/` are **always at the
  root** in both layouts. They are never duplicated inside a module.
- The framework's own conventional folders (`src/`, `app/`, `dto/`, `services/`,
  `repositories/`, `providers/`) do **not** replace these three. If the framework
  forces a wrapper folder such as `src/` or `app/`, the three folders live inside it —
  the structure below `src/` is exactly the structure in §3.

---

## 3. Complete folder structure reference

`.<ext>` below is the project's source extension — `.ts`, `.js`, `.py`, `.php`, `.rb`,
`.java`, `.cs`. Every file keeps the base name shown.

### 3.1 Flat layout (single-surface project)

```
<project>/
├── .env                              # local env vars, never committed
├── .env.example                      # same keys, empty values, committed
├── <dependency manifest>
├── <entry point>                     # entry point only — no logic
│
├── auth/
│   └── auth.<ext>                    # token load/parse + middleware definitions
│
├── common/                           # cross-cutting pure helpers (no HTTP, no DB writes)
│   ├── jwt.<ext>                     # claim types
│   ├── regex.<ext>                   # validation regexes
│   └── security.<ext>                # hashing, random tokens
│
├── config/                           # one file per external concern (only the ones used)
│   ├── database.<ext>                # required — initDb(), the shared handle, runs migrations
│   ├── email.<ext>                   # optional — SMTP sender + template parsing
│   ├── storage.<ext>                 # optional — file upload / delete
│   └── regex.<ext>                   # optional — shared validation patterns
│
├── controllers/                      # one file per entity — all HTTP handlers
│   ├── activity_log.<ext>
│   ├── dashboard.<ext>
│   ├── department.<ext>
│   ├── designation.<ext>
│   ├── global_search.<ext>
│   ├── login.<ext>
│   └── reports.<ext>
│
├── models/                           # one file per entity — type/schema declarations only
│   ├── activity_log.<ext>
│   ├── department.<ext>
│   ├── designation.<ext>
│   └── staff.<ext>
│
├── routers/                          # one file per entity + one aggregator
│   ├── route.<ext>                   # initRoutes(app) — CORS + calls every xRoutes(app)
│   ├── dashboard.<ext>
│   ├── department.<ext>
│   ├── designation.<ext>
│   └── login.<ext>
│
├── migrations/                       # NNNN_<verb>_<subject>.sql, sequential
│   ├── 0001_create_role.sql
│   ├── 0002_create_department.sql
│   └── 0003_alter_department.sql
│
├── scheduler/
│   └── scheduler.<ext>               # startCronJobs() + one function per domain
│
└── templates/                        # flat .html email templates
    ├── forgot_password.html
    ├── new_user_created.html
    └── reset_password.html
```

### 3.2 Modular layout (multiple modules / role-based surfaces)

```
<project>/
├── .env
├── .env.example
├── <dependency manifest>
├── <entry point>
│
├── auth/
│   └── auth.<ext>
│
├── common/                           # shared across every module
│   ├── controllers/
│   │   ├── company.<ext>
│   │   ├── department.<ext>
│   │   ├── employee.<ext>
│   │   ├── login.<ext>
│   │   └── shift.<ext>
│   ├── models/
│   │   ├── company.<ext>
│   │   ├── department.<ext>
│   │   ├── employee.<ext>
│   │   └── shift.<ext>
│   └── routers/
│       ├── routers.<ext>             # commonRoutes(app) aggregator
│       ├── company.<ext>
│       ├── department.<ext>
│       ├── employee.<ext>
│       └── shift.<ext>
│
├── config/                           # only the files this project needs
│   ├── database.<ext>
│   ├── email.<ext>
│   ├── regex.<ext>
│   ├── storage.<ext>                 # optional — file upload / delete
│   └── ws_notification.<ext>         # optional — websocket hub config
│
├── modules/
│   ├── CRM/
│   │   ├── controllers/
│   │   │   ├── customer.<ext>
│   │   │   ├── invoices.<ext>
│   │   │   ├── leads.<ext>
│   │   │   └── payment.<ext>
│   │   ├── models/
│   │   │   ├── customer.<ext>
│   │   │   ├── invoices.<ext>
│   │   │   └── leads.<ext>
│   │   └── routers/
│   │       ├── routers.<ext>         # crmRoutes(app) — calls the module's xRoutes(app)
│   │       ├── customer.<ext>
│   │       └── leads.<ext>
│   │
│   ├── Projects/
│   │   ├── controllers/
│   │   │   ├── milestone.<ext>
│   │   │   ├── project.<ext>
│   │   │   ├── project_task.<ext>
│   │   │   └── subtask.<ext>
│   │   ├── models/
│   │   └── routers/
│   │       └── routers.<ext>         # projectsRoutes(app)
│   │
│   ├── HumanResource/
│   │   ├── controllers/
│   │   ├── models/
│   │   └── routers/
│   │       └── routers.<ext>         # humanResourceRoutes(app)
│   │
│   ├── Agent/
│   │   ├── controllers/
│   │   │   ├── agent.<ext>
│   │   │   ├── helper.<ext>          # helpers shared by this module's controllers
│   │   │   └── work_diary.<ext>
│   │   ├── models/
│   │   └── routers/
│   │       └── routers.<ext>         # agentsRoutes(app)
│   │
│   └── Supports/                     # a module may nest a sub-module
│       ├── controllers/
│       ├── models/
│       ├── routers/
│       │   └── routers.<ext>         # supportRoutes(app)
│       └── VendorSupport/            # sub-module: same three folders again
│           ├── controllers/
│           ├── models/
│           └── routers/
│               └── routers.<ext>     # vendorSupportRoutes(app)
│
├── routers/
│   └── routes.<ext>                  # initRoutes(app) — CORS + every module aggregator
│
├── migrations/                       # main database
│   ├── 0001_create_company.sql
│   └── 0088_create_milestone.sql
│
├── migrations_agent/                 # a second database gets its own migrations folder
│   └── 0001_create_agent_tables.sql
│
├── scheduler/
│   └── scheduler.<ext>
│
└── templates/
    ├── forgot_password.html
    ├── new_user_created.html
    └── support_ticket_email.html
```

### 3.3 Worked example — a filled-in modular project

This is what §3.2 looks like once it is filled with real files, for a project that has
purchasing, assets, finance and activity-log areas. Use it as the model when laying out
your own repository.

```
<project>/
└── backend/
    ├── .env
    ├── .env.example
    ├── <dependency manifest>
    ├── <entry point>
    │
    ├── auth/
    │   └── auth.<ext>
    │
    ├── common/                       # entities used by every module
    │   ├── controllers/
    │   │   ├── banks.<ext>
    │   │   ├── company.<ext>
    │   │   ├── currency.<ext>
    │   │   ├── customers.<ext>
    │   │   ├── employees.<ext>
    │   │   ├── global_search.<ext>
    │   │   ├── login.<ext>
    │   │   ├── notification_hub.<ext>
    │   │   ├── project.<ext>
    │   │   ├── scope.<ext>
    │   │   ├── subtask.<ext>
    │   │   ├── vendors.<ext>
    │   │   └── ws_hub.<ext>
    │   ├── models/
    │   │   ├── banks.<ext>
    │   │   ├── company.<ext>
    │   │   ├── customers.<ext>
    │   │   ├── employees.<ext>
    │   │   ├── project.<ext>
    │   │   ├── scope.<ext>
    │   │   ├── subtask.<ext>
    │   │   └── vendors.<ext>
    │   └── routers/
    │       ├── routers.<ext>         # commonRoutes(app)
    │       ├── banks.<ext>
    │       ├── company.<ext>
    │       ├── customers.<ext>
    │       ├── employees.<ext>
    │       └── login.<ext>
    │
    ├── config/                       # only the files this project needs
    │   ├── database.<ext>
    │   ├── email.<ext>
    │   ├── integration_client.<ext>
    │   └── regex.<ext>
    │
    ├── modules/
    │   ├── Purchase/                 # purchase orders, specs, approval config
    │   │   ├── controllers/
    │   │   │   ├── purchase_order.<ext>
    │   │   │   ├── specification.<ext>
    │   │   │   └── helper.<ext>      # helpers shared by the two files above
    │   │   ├── models/
    │   │   │   └── purchase_order.<ext>
    │   │   └── routers/
    │   │       ├── routers.<ext>     # purchaseRoutes(app)
    │   │       └── purchase_order.<ext>
    │   │
    │   ├── Assets/
    │   │   ├── controllers/assets.<ext>
    │   │   ├── models/assets.<ext>
    │   │   └── routers/
    │   │       ├── routers.<ext>     # assetRoutes(app)
    │   │       └── assets.<ext>
    │   │
    │   ├── Finance/                  # invoices, expenses, payscale, currency convert
    │   │   ├── controllers/
    │   │   ├── models/
    │   │   └── routers/routers.<ext> # financeRoutes(app)
    │   │
    │   └── ActivityLog/
    │       ├── controllers/activity_log.<ext>
    │       ├── models/activity_log.<ext>
    │       └── routers/
    │           ├── routers.<ext>     # activityLogRoutes(app)
    │           └── activity_log.<ext>
    │
    ├── routers/
    │   └── routes.<ext>              # initRoutes(app) — CORS + every module aggregator
    │
    ├── migrations/
    │   ├── 0001_create_customer.sql
    │   ├── 0002_create_company.sql
    │   └── 0017_create_activity_logs.sql
    │
    ├── migrations_agent/
    │
    ├── scheduler/
    │   └── scheduler.<ext>
    │
    └── templates/
        ├── forgot_password.html
        ├── new_user_created.html
        ├── po_approval.html
        └── po_status.html
```

**Migrating a flat project into this shape:** if an existing project keeps
`purchase_order`, `assets` and `activity_log` as flat root-level `controllers/`,
`models/`, `routers/` files, each of those becomes a module folder under `modules/`
with its own three folders and a `routers` aggregator. Move the controller, model and
router of one entity together, in one commit. The root `routers/routes.<ext>` stays as
the single `initRoutes(app)` entry that mounts CORS and calls `commonRoutes(app)` plus
each module aggregator.

---

## 4. File naming

| Item | Rule | Example |
|---|---|---|
| Source file | named after the **entity**, singular, in the repo's one chosen case | `purchase_order`, `activity_log` |
| Triplet | **the same base name in all three folders** | `models/leads` ↔ `controllers/leads` ↔ `routers/leads` |
| Aggregator | `routers` inside `common/` and inside every module; `routes` at the project root | `modules/CRM/routers/routers.<ext>`, `routers/routes.<ext>` |
| Module folder | `PascalCase`, singular or natural product name | `CRM/`, `Projects/`, `HumanResource/`, `Purchase/` |
| Shared helper file | `helper`, one per controllers folder, for helpers used by two or more controller files (§5.6.1) | `modules/Purchase/controllers/helper.<ext>` |
| Config file | one per external concern, lowercase; only the ones the project uses (§11) | `database`, `email`, `storage` |
| Migration | `NNNN_<verb>_<subject>.sql`, zero-padded to 4 | `0088_create_milestone.sql` |
| Template | `snake_case.html`, describing the email | `po_approval.html`, `forgot_password.html` |

### 4.1 The one thing that never changes: the triplet

Whatever case or suffix the language uses, **one entity produces exactly three files
that share a base name**, one in each folder. Given the entity `purchase_order`:

| Stack | `models/` | `controllers/` | `routers/` |
|---|---|---|---|
| TypeScript / NestJS | `purchase-order.entity.ts` | `purchase-order.controller.ts` | `purchase-order.router.ts` |
| JavaScript / Express | `purchase-order.js` | `purchase-order.js` | `purchase-order.js` |
| Python / Django / FastAPI | `purchase_order.py` | `purchase_order.py` | `purchase_order.py` |
| PHP / Laravel | `PurchaseOrder.php` | `PurchaseOrderController.php` | `PurchaseOrderRoutes.php` |
| Ruby / Rails | `purchase_order.rb` | `purchase_orders_controller.rb` | `purchase_orders.rb` |
| Java / Spring | `PurchaseOrder.java` | `PurchaseOrderController.java` | `PurchaseOrderRoutes.java` |

Rules for the amendment:

- **The base name is identical across the three folders.** A reader who opens
  `controllers/` and `models/` sees the same list of entity names.
- **Pick one case convention and one suffix convention for the whole repo** — the
  language's idiomatic one — and never mix. Half the files in `kebab-case` and half in
  `snake_case` is a violation.
- The framework's mandatory suffix (`.controller.ts`, `Controller.php`) is allowed and
  expected; an *optional* decorative suffix is not.
- **The folder names are never translated.** They are `controllers/`, `models/`,
  `routers/`, `common/`, `modules/`, `config/`, `auth/`, `migrations/`, `scheduler/`,
  `templates/` in every language, even where the framework would call them `entities/`,
  `schemas/`, `views/`, `routes/`, `resources/` or `apps/`.

### 4.2 Additional rules

- **One entity per file.** If `purchase_order` also handles specifications and approval
  configs, split it: `purchase_order`, `specification`, `approval_config`.
- **Never** `utils`, `misc`, `common`, `shared` or `index` as a controllers-folder
  helper file — the name is `helper`.
- Test files use the language's own convention (`*.spec.ts`, `test_*.py`,
  `*Test.java`), placed as the language expects.
- No spaces in file names.

---

## 5. In-file ordering — the house format

This is the part every file must obey. The order is fixed; readers should always find
the same thing in the same place.

### 5.1 Universal order

```
1. module/package declaration      where the language has one
2. imports                         std lib first, then third-party, then internal
3. module-level const / var        route paths, status maps, singletons
4. type declarations               request/input types, response types
5. helper functions                private, small, no request/response object
6. exported handlers / API funcs   the real work
```

**Import grouping** — three blocks separated by one blank line, in this order:

```
<standard library / runtime imports>

<third-party framework and ORM imports>

<internal project imports, absolute from the project root>
```

Where the language has no import blocks (or the tooling sorts them automatically),
accept the tool's output — but never hand-write a fourth grouping scheme.

### 5.2 `models/<entity>.<ext>`

Only imports, then the type/schema declarations. Nothing else — no methods, no DB
calls, no validation, no serialisation logic.

```
# models/purchase_order

# Parent entity first, then its children, then join/lookup types.
TYPE PurchaseOrder:
	id           string       -> json "id"           primary key
	vendor_id    int          -> json "vendor_id"
	vendor       Vendor       -> json "vendor"       relation: belongs-to vendor_id
	status       string       -> json "status"
	items        [PurchaseOrderItem] -> json "items" relation: has-many purchase_order_id
	is_active    bool?        -> json "status_active"    # nullable / tri-state
	created_at   timestamp    -> json "created_at"

TYPE PurchaseOrderItem:
	id                int     -> json "id"           primary key, auto-increment
	purchase_order_id string  -> json "purchase_order_id"
	description       string  -> json "description"
	quantity          int     -> json "quantity"
	unit_price        decimal -> json "unit_price"
```

If a model file needs a function, it is in the wrong place — move it to the controller.

### 5.3 `routers/<entity>.<ext>`

Order: imports → path variables → the `xRoutes(app)` function.

**Start here — no middleware yet.** At the beginning of a project, or while the
endpoints are still being tested, auth is usually not wired up. Write the routes with
just the handler; nothing else about the file changes:

```
# routers/purchase_order

specPath     = "/api/v1/users/:user_id/purchase/spec"
purchasePath = "/api/v1/users/:user_id/purchase-order"
approvalPath = "/api/v1/users/:user_id/purchase/approval"

FUNC purchaseOrderRoutes(app):
	# Specification
	app.POST(specPath, createSpecification)
	app.GET(specPath, listAllSpecifications)
	# Purchase Order
	app.POST(purchasePath, createPurchaseOrder)
	app.GET(purchasePath, listPurchaseOrders)
	app.GET(purchasePath + "/:id", getPurchaseOrderById)
	app.PATCH(purchasePath + "/:id/update", updatePurchaseOrder)
	app.DELETE(purchasePath + "/:id/delete", deletePurchaseOrder)
	RETURN app
```

**Later — the same file with auth added.** When the auth layer is ready, the middleware
is appended as the **last argument** of each line. No path, no handler and no line order
changes; only the `auth` import is added:

```
	app.POST(purchasePath, createPurchaseOrder, adminMiddleware("..."))
	app.GET(purchasePath, listPurchaseOrders, adminMiddleware("..."))
	app.GET(purchasePath + "/:id", getPurchaseOrderById, adminMiddleware("..."))
```

Where the framework attaches middleware by decorator or by a guard list rather than by
argument, the equivalent rule applies: the guard is added to the existing line or
declaration, and nothing else about the route moves.

Because of this, **controllers must never depend on middleware having run.** A handler
always reads `:user_id` from the path and validates it against the database itself
(§6) — that way the same handler works with or without auth in front of it.

Do not leave routes commented out to "disable auth", and do not keep two versions of a
route line. One line per endpoint; add the middleware argument when it exists.

Rules: route strings are **only** built from the path variables + a suffix; never repeat
the full literal on each line. Group related lines with a one-line comment. Always
return the app object where the language expects it.

A router file contains **no** conditional, no DB call, no response write — only path
variables and route registrations.

### 5.4 `routers/routers.<ext>` (module aggregator)

Nothing but calls:

```
FUNC humanResourceRoutes(app):
	holidayRoutes(app)
	leaveRoutes(app)
	workflowRoutes(app)
	overtimeRoutes(app)
	jobApplicationRoutes(app)
```

One line per entity router in the module. Nothing else belongs in this file.

### 5.5 `routers/routes.<ext>` (root aggregator)

CORS first, then every module aggregator. **No route is ever declared here.**

```
FUNC initRoutes(app):
	app.use(cors({ origins: ["*"], methods: ["*"], headers: ["*"] }))
	commonRoutes(app)
	purchaseRoutes(app)
	assetRoutes(app)
	activityLogRoutes(app)
```

In the flat layout this same file is `routers/route.<ext>` and it calls the entity
routers (`designationRoutes(app)`, `staffRoutes(app)`, …) directly instead of module
aggregators.

### 5.6 `controllers/<entity>.<ext>`

The controller is the only place with real logic. Fixed order:

```
1. imports
2. module-level var / const        status maps, cached config, exported globals
3. request/input types             everything the handlers parse the body into
4. private helpers                 small pure funcs + transaction helpers (no request object)
5. exported handlers               Create → List → Get → Update → UpdateStatus → Delete → extras
```

Skeleton:

```
# controllers/purchase_order

# --- module-level state
PURCHASE_STATUSES = { draft, pending, approved, rejected }

# --- request types
TYPE PurchaseOrderInput:
	vendor_id int          -> json "vendor_id"
	items     [ItemInput]  -> json "items"

TYPE ItemInput:
	description string     -> json "description"
	quantity    int        -> json "quantity"
	unit_price  decimal    -> json "unit_price"

# --- helpers
FUNC poNumberTaken(tx, poNumber, excludeId) -> bool
FUNC buildPaymentTerms(poId, terms) -> [PaymentTerm]

# --- handlers
HANDLER createPurchaseOrder(request)
HANDLER listPurchaseOrders(request)
HANDLER getPurchaseOrderById(request)
HANDLER updatePurchaseOrder(request)
HANDLER updatePurchaseOrderStatus(request)
HANDLER deletePurchaseOrder(request)
```

Where the framework requires the handlers to be methods of a controller class, the same
order applies **inside the class**, and the helpers and input types sit above the class
in the same file.

**Large files (>1000 lines):** the same triad may repeat per feature block —
`types → helpers → handlers` for specifications, then `types → helpers → handlers` for
the purchase order itself, then for approval config. Never interleave: a helper must
never appear between two handlers of the same block. Mark each block with a
**one-line** comment naming it (`// Specification`, `// Purchase Order`,
`// Approval Config`) — nothing longer, no drawn separators.

### 5.6.1 `helper.<ext>` — shared helpers of a module

A module usually has several controller files (`dashboard`, `expense`,
`purchase_order`, `specification` …), and some of them grow big helper functions that
**more than one of those files needs**. Those shared helpers do not get copied, and
they do not sit in whichever controller happened to need them first — they move into a
single `helper` file inside the same `controllers` folder.

```
modules/
└── Purchase/
    └── controllers/
        ├── purchase_order.<ext>     # handlers + helpers used only here
        ├── specification.<ext>      # handlers + helpers used only here
        └── helper.<ext>             # helpers shared by BOTH files above
```

```
# modules/Purchase/controllers/helper

# Shared by purchase_order, specification and expense
FUNC formatHHMMSS(duration) -> string
FUNC parseDuration(text) -> int
FUNC secondsToDecimalHours(seconds) -> decimal
FUNC combineDateAndTime(date, time) -> timestamp
```

**When a helper goes into `helper.<ext>`:**

- two or more controller files in the module use it, **or**
- it is long enough that repeating it anywhere would be duplication, **or**
- it is a pure utility with no domain logic (time formatting, duration parsing,
  number/string conversion).

**When a helper stays inside its own controller file:**

- only that one file uses it — small one- or two-use helpers are fine where they are;
  do not create a file for them. Keep them in the helper block above the handlers
  (§5.6).

Rules for `helper.<ext>`:

- One file per module's controllers folder — named exactly `helper`
  (never `utils`, `common`, `misc`, `shared`).
- Helpers take plain values, never the request/response object, and never write a
  response.
- A helper that touches the DB inside a transaction takes the **transaction handle as
  its first parameter**.
- If the helper file itself grows past a few hundred lines, split it by concern —
  `helper` + `helper_calculation` — not by controller.
- The same rule applies to `models/` and `routers/` if they ever need shared code, but
  in practice they should not.

### 5.7 `config/<concern>.<ext>`

Order: imports → constants → module-level singletons → template-data types →
init/loader functions → send/perform functions.

```
# config/email

MAILGUN_DOMAIN = "..."

smtpHost = env("SMTP_HOST")
smtpPort = env("SMTP_PORT")

TYPE EmailTemplateData:
	name  string
	email string
	year  int

FUNC getPasswordEmailTemplateFromFile(name, email, password) -> (string, error)
FUNC sendMailgunEmail(to, subject, htmlBody) -> error
```

A config file exposes what the rest of the app needs as module-level values
(`config.db`, `config.apiUrl`) and keeps the wiring details private.

### 5.8 Formatting, comments and blank lines

Files must stay compact and must look identical on every machine. Three rules, applied
everywhere.

#### Indentation — tabs, never spaces

- **Indent with tabs.** Never use the space bar to line up code — the same file then
  renders with different widths on different editors and operating systems, and diffs
  fill up with whitespace-only changes.
- Tab width is a personal editor setting (2, 4, 8 — your choice); because the file
  stores a tab, everyone sees their own preferred width and the bytes stay the same.
- Alignment inside a line is done by the project's formatter — run it and do not
  hand-align with spaces afterwards.
- Do not mix: a line indented with a tab followed by spaces is the worst case. Set the
  editor once and forget it.
- `.sql`, `.html` and every other source file in the repo follow the same rule; what
  matters most is that a single file never mixes both.
- **Exception — languages where indentation is syntax or where the ecosystem formatter
  is not configurable to tabs** (Python with an opinionated formatter, YAML): follow the
  ecosystem default there, set it once in `.editorconfig` and in the formatter config,
  and keep it identical across every file of that type in the repo. Never leave the
  choice to the individual developer.

```
// Bad  →  ····createHoliday(...)      (4 space characters)
// Good →  ⇥createHoliday(...)         (one tab character)
```

Add this to `.editorconfig` at the repo root so nobody has to remember, listing the
repo's own extensions:

```ini
[*.{ts,js,php,sql}]
indent_style = tab
trim_trailing_whitespace = true
insert_final_newline = true
```

Configure the project's formatter to agree with it (`prettier`, `php-cs-fixer`,
`eslint`, `black`, `spotless` — whichever the stack uses) and run it before every
commit. The formatter fixes indentation and alignment; it does **not** remove extra
blank lines or useless comments. That part is on you.

#### Comments — only when they add something

- **Do not comment obvious code.** A comment saying "create the holiday" above the
  create call adds nothing. Delete it.
- A comment is written **only** when the reason is not visible in the code: a business
  rule, a non-obvious formula, a workaround, a unit, or a warning.
- Maximum **1–2 lines**. Never a paragraph, never a block of explanation above a
  function.
- No decorative separators of many lines, no `// ---- end of function ----`, no
  commented-out old code (delete it — git has it).
- No auto-generated boilerplate headers (author, date, description) at the top of a file.
- No generated doc-comment blocks on every function just because the tooling can
  produce them. A doc comment is written where a public contract genuinely needs
  explaining, and it is one or two lines.

```
# Bad — a paragraph nobody reads, restating the code
/*
 * This function creates a new holiday. It first checks that the employee
 * exists, then binds the request body, then validates the fields, then
 * saves the record to the database and finally returns the response.
 */
HANDLER createHoliday(request):
	# get the user id from the path
	employeeId = request.path("user_id")
	# declare the variables
	DECLARE holiday
```

```
# Good — one short comment, only where the reason is not obvious
HANDLER createHoliday(request):
	employeeId = request.path("user_id")
	DECLARE holiday, employee
	...
	# Day is derived, never accepted from the client
	holiday.day = weekdayName(holiday.date)
```

Short section markers inside a long controller are allowed and useful — one line only:

```
// Specification
// Purchase Order
// Approval Config
```

#### Blank lines — one, never two

| Place | Blank lines |
|---|---|
| Inside a function | **0** — no blank rows between statements |
| Between two functions | **1** |
| Between import groups (std / third-party / internal) | **1** |
| Between type declarations | **1** |
| After the module/package declaration | **1** |
| End of file | 1 newline, nothing more |

- Never two or more blank lines in a row, anywhere.
- No blank line right after an opening brace or right before a closing brace.
- No trailing spaces at the end of a line.
- Route registrations in a router file are written as consecutive lines; use at most
  one blank line to separate route groups, with a one-line comment naming the group.

```
# Bad — blank rows scattered through the body, double blank line, padded braces
HANDLER listHoliday(request):

	employeeId = request.path("user_id")

	DECLARE holidays


	employee = DB.first(Employee, id = employeeId)

	IF NOT employee:

		RETURN 400 { "success": false, "error": "Not found" }

```

```
# Good
HANDLER listHoliday(request):
	employeeId = request.path("user_id")
	DECLARE holidays, employee
	employee = DB.first(Employee, id = employeeId)
	IF NOT employee:
		RETURN 400 { "success": false, "error": "Not found" }
	...
```

---

## 6. Handler body structure

Every handler follows the same top-to-bottom sequence. This is non-negotiable —
it is what makes any controller in any of our projects readable at a glance, whatever
it is written in.

```
1. read path params                     request.path("user_id"), request.path("id")
2. read query params                    page, limit, search, filters
3. declare all vars                     (model vars, input var, counters)
4. fixed values, conversions, defaults  numeric casts, totalPages = 1, page/limit floors
5. resolve + validate the acting user   fetch employee/staff by user_id
6. fetch the target record              for Update/Delete/Get
7. parse the body                       into the input type
8. field-level validation               required, trim, duplicate check, FK exists
9. DB operation                         create / save / update / delete (transaction if multi-table)
10. activity log                        after success, before response
11. return the response                 the standard envelope
```

Steps 1–4 are the **input block**: everything the handler reads and everything with a
fixed or derived value is settled at the top, before a single database call or check
that can return. Nothing below the input block introduces a new variable out of thin
air, so a reader knows every value in play by the time the checks start.

Every failure **returns immediately with a status code and the envelope** — no
exception thrown out of the handler, no framework error object, no bare error
propagated to a global handler that turns it into a 500.

> If the framework's idiom is to throw a typed HTTP exception rather than return a
> response (NestJS, Laravel, Spring), the throw must carry the §6.7 status code **and**
> the §7 envelope body, and the exception filter must not reshape it. The wire format
> is what is being standardised, not the mechanism.

### 6.1 Create

```
HANDLER createHoliday(request):
	employeeId = request.path("user_id")
	DECLARE holiday, employee
	employee = DB.first(Employee, id = employeeId)
	IF NOT employee:
		RETURN 400 { "success": false, "error": "Not found, Please check the login" }
	holiday = parse(request.body()) OR RETURN 400 { "success": false, "error": "Invalid input" }
	IF isEmpty(holiday.date) OR trim(holiday.holiday) == "":
		RETURN 400 { "success": false, "error": "Date and Holiday fields are mandatory" }
	# Day is derived, never accepted from the client
	holiday.day = weekdayName(holiday.date)
	IF NOT DB.create(holiday):
		RETURN 400 { "success": false, "error": "Failed to create holiday" }
	createActivityLog(employee.id, "create", "holiday", holiday.id,
		"Added new holiday: " + holiday.holiday, "Success")
	RETURN 200 { "success": true, "response": { "data": holiday } }
```

**Duplicate check before create**, when the entity has a unique name:

```
	designation.name = trim(designation.name)
	existing = DB.first(Designation, WHERE "LOWER(TRIM(name)) = LOWER(?)", designation.name)
	IF existing:
		RETURN 400 { "success": false, "error": "Designation Already Exists" }
```

**FK existence check before create:**

```
	IF designation.reports_to IS NOT NULL:
		parent = DB.first(Designation, id = designation.reports_to)
		IF NOT parent:
			RETURN 400 { "success": false, "error": "Parent Designation Not Found" }
```

**Default for a tri-state nullable flag** — only when the client sent nothing:

```
	IF designation.is_active IS NULL:
		designation.is_active = true
```

### 6.2 List — pagination + search + filter

The list handler always supports `page`, `limit`, `search`, plus entity-specific
filters. `page=0` or `limit=0` means "return everything" — this is only for endpoints
that feed dropdowns and small lookup lists. A list that can grow unbounded caps `limit`
at a sane maximum (§6.9) and does not honour `limit=0`.

Note the input block at the top: path param, then every query param, then the
declarations, then the conversions and defaults (`userIdInt`, `totalPages = 1`, the
`page`/`limit` floors). Only after all of that does the first check that can return
appear. **Never read a query param halfway down the handler.**

```
HANDLER listDesignations(request):
	userId        = request.path("user_id")
	page          = toInt(request.query("page"))
	limit         = toInt(request.query("limit"))
	search        = request.query("search")
	isActiveParam = request.query("is_active")
	DECLARE staff, designations, totalRoles, totalPages, query, offset
	userIdInt  = toInt(userId)
	totalPages = 1
	IF page  <= 0: page  = 0
	IF limit <= 0: limit = 0
	IF userIdInt IS INVALID:
		RETURN 400 { "success": false, "error": "Staff not found, please try again" }
	staff = DB.first(Staff, id = userIdInt)
	IF NOT staff:
		RETURN 400 { "success": false, "error": "Staff Not Found, Please check the login" }
	query = DB.query(Designation).with("sub_roles").orderBy("id ASC")
	IF search != "":
		query = query.where("(name ILIKE ? OR description ILIKE ?)", "%"+search+"%", "%"+search+"%")
	IF isActiveParam != "":
		query = query.where("is_active = ?", isActiveParam == "true")
	offset = (page - 1) * limit
	IF limit == 0 OR page == 0:
		designations = DB.list(query)
		IF FAILED:
			RETURN 400 { "success": false, "error": "No designations Found" }
	ELSE:
		totalRoles = DB.count(query)
		totalPages = totalRoles / limit
		IF totalRoles % limit != 0: totalPages = totalPages + 1
		designations = DB.list(query.limit(limit).offset(offset))
		IF FAILED:
			RETURN 400 { "success": false, "error": "Couldn't list the designations" }
	RETURN 200 {
		"success": true,
		"message": {
			"page": page, "limit": limit,
			"total_pages": totalPages,
			"data": designations
		}
	}
```

### 6.3 Update — field-by-field diff with a change log

Update **never blind-saves the parsed body.** Each field is compared, validated,
applied, and appended to `changes` so the activity log records what actually changed.
This is also the security rule: a field the client is not allowed to set can never be
written, because only named fields are copied.

```
HANDLER updateDesignation(request):
	userId  = request.path("user_id")
	idParam = request.path("id")
	DECLARE staff, designation, input, changes
	userIdInt = toInt(userId)
	id        = toInt(idParam)
	# ... invalid-id checks, resolve staff by userIdInt, load designation by id ...
	input = parse(request.body()) OR RETURN 400 { "success": false, "error": "Invalid input format" }
	IF trim(input.name) != "" AND trim(input.name) != designation.name:
		count = DB.count(Designation, "LOWER(TRIM(name)) = LOWER(?) AND id <> ?", trim(input.name), id)
		IF count > 0:
			RETURN 400 { "success": false, "error": "Designation already exists" }
		oldName = designation.name
		designation.name = trim(input.name)
		changes.append("Name changed from '" + oldName + "' to '" + designation.name + "'")
	# ... one block like the above per updatable field ...
	IF NOT DB.save(designation):
		RETURN 400 { "success": false, "error": "Failed to Update Designation" }
	createActivityLog(staff.id, "update", "designation", designation.id,
		"Designation updated: " + join(changes, "; "))
	RETURN 200 {
		"success": true,
		"message": "Designation Updated Successfully",
		"data": designation
	}
```

### 6.4 Status toggle

A status-only endpoint declares its tiny input type **inside** the function (it is used
nowhere else). Where the language cannot declare a type inside a function, it sits
immediately above the handler and is not exported.

```
HANDLER updateDesignationStatus(request):
	userId  = request.path("user_id")
	idParam = request.path("id")
	TYPE Status: is_active bool -> json "status"
	DECLARE staff, designation, status
	userIdInt = toInt(userId)
	id        = toInt(idParam)
	# ... invalid-id checks, resolve staff, load designation, parse status ...
	IF NOT DB.update(Designation, WHERE id = id, SET is_active = status.is_active):
		RETURN 400 { "success": false, "error": "Failed to save Status" }
	statusStr = status.is_active ? "activated" : "inactivated"
	createActivityLog(staff.id, "Update Active Status", "designation", designation.id,
		"Designation '" + designation.name + "' status " + statusStr)
	RETURN 200 { "success": true, "message": "Status updated Successfully" }
```

### 6.5 Delete — dependency guards first

Never delete before checking what depends on the record. **The error message names the
blocking rows** so the user knows what to fix.

```
HANDLER deleteDesignation(request):
	userId  = request.path("user_id")
	idParam = request.path("id")
	DECLARE staff, designation, childDesignations, names
	userIdInt = toInt(userId)
	id        = toInt(idParam)
	# ... invalid-id checks, resolve staff by userIdInt, load designation by id ...
	childDesignations = DB.list(Designation, reports_to = id)
	IF count(childDesignations) > 0:
		names = pluck(childDesignations, "name")
		RETURN 400 {
			"success": false,
			"error": "Cannot delete: This designation is 'Reports To' for the following designations: " + join(names, ", ")
		}
	IF NOT DB.delete(designation):
		RETURN 400 { "success": false, "error": "Failed to delete Designation" }
	# ... activity log + success response
```

### 6.6 Transactions

Multi-table writes run inside one transaction, and **every helper that participates
takes the transaction handle as its first parameter**:

```
FUNC poNumberTaken(tx, poNumber, excludeId) -> bool
FUNC seedRecurringReceivedInvoice(tx, po) -> string
FUNC emitPurchaseExpenses(tx, po) -> error
```

```
	DB.transaction(tx => {
		tx.create(po) OR FAIL
		emitPurchaseExpenses(tx, po) OR FAIL
	})
```

Inside a transaction always use the transaction handle, never the global connection —
mixing the two silently writes outside the transaction and breaks the rollback. This
applies equally to frameworks that manage the transaction with a decorator or a context
variable: the rule is that no write inside the block escapes it.

### 6.7 Error message style and status codes

- Sentence case, human readable, safe to show a user:
  `"Staff Not Found, Please check the login"`, `"Date and Holiday fields are mandatory"`.
- Never leak raw driver errors, SQL, table names, or stack traces into the response.
  Log them on the server, return a clean sentence to the client.
- Every error says **what is wrong and what to do**, never just `"error"` or `"failed"`.

**Do not return `500 Internal Server Error`.** A 500 tells the frontend nothing, cannot
be handled, and usually means we did not classify the failure. Pick the code that
describes the real problem:

| Situation | Code | Use |
|---|---|---|
| Validation failed, parse failed, business rule rejected, DB write failed | `400 Bad Request` | the default for almost everything |
| The addressed record does not exist | `404 Not Found` | `GET/PATCH/DELETE /:id` on a missing row |
| Token missing / invalid / expired | `401 Unauthorized` | raised by middleware, not controllers |
| Caller is known but not allowed to do this | `403 Forbidden` | ownership or access rejection |
| Duplicate record, or state conflict (already approved, already paid) | `409 Conflict` | uniqueness and state-machine violations |
| Body parsed fine but the values are semantically wrong | `422 Unprocessable Entity` | optional, when 400 is too vague |
| Any success, including create and delete | `200 OK` | we do not use 201/204 |

```
# Bad
	IF NOT DB.create(po):
		RETURN 500 { "success": false, "error": rawDriverError }
```

```
# Good
	IF NOT DB.create(po):
		log("create purchase order:", rawDriverError)
		RETURN 400 { "success": false, "error": "Failed to create the purchase order, please try again" }
```

If a query genuinely cannot be classified (a raw SQL call blew up), still return `400`
with a clean message and log the detail — the client cannot act on a 500 either way.

**Turn off the framework's default error page and default exception mapper.** Most
frameworks return their own HTML or JSON on an unhandled error, and most of them return
`201` on create and `204` on delete by default. Both are violations. Configure the
framework once so that every route returns `200` on success and the §7 envelope on
failure, and verify it with an actual request.

### 6.8 Reading input — query params, JSON body and form-data

There are exactly three ways a request carries data. Use the one that matches the
content type, and never mix two of them in the same endpoint.

#### 1. Path parameters — identity only

```
	userId = request.path("user_id")
	poId   = request.path("id")
```

Path params carry **who** and **which record**, nothing else. They are always validated
before use (numeric cast, then a DB lookup).

#### 2. Query parameters — list controls and filters (`GET` only)

Query params are used for pagination, search, filtering and sorting. Every one of them
is optional and every one has a defined default.

```
	page     = toInt(request.query("page"))
	limit    = toInt(request.query("limit"))
	search   = request.query("search")
	status   = request.query("status")
	fromDate = request.query("from_date")
```

```
GET /api/v1/users/12/purchase-order?page=2&limit=20&search=cable&status=approved
```

Rules:
- Names are `snake_case` and identical across every module: `page`, `limit`, `search`,
  `from_date`, `to_date`, `status`, `is_active`, `sort`, `order`.
- Ignore an unrecognised or empty param — never fail the request because of it. If the
  framework validates query params strictly by default (rejecting unknown keys), relax
  that setting.
- Never send a body with `GET`; never accept a filter through the body.

#### 3. Request body

**a) Plain JSON — the default for `POST` / `PATCH`.**
Content-Type `application/json`, parsed into the input type:

```
	DECLARE input
	input = parse(request.body()) OR RETURN 400 { "success": false, "error": "Invalid input" }
```

```json
{
  "vendor_id": 8,
  "items": [ { "description": "Cable", "quantity": 10, "unit_price": 45.5 } ]
}
```

**b) Multipart form-data — only when files are uploaded.**
The JSON payload is sent as one text field named `data`, and the binaries come in named
file fields. Never spread the record's fields across dozens of form keys.

```
Content-Type: multipart/form-data

data    = {"vendor_id":8,"title":"Annual contract","items":[...]}   ← one JSON string
files   = contract.pdf
files   = annexure.pdf
images  = site_photo.jpg
```

```
HANDLER createPurchaseOrder(request):
	userId = request.path("user_id")
	DECLARE input, employee, files, images
	employee = DB.first(Employee, id = userId)
	IF NOT employee:
		RETURN 400 { "success": false, "error": "Not found, Please check the login" }
	input = parseJson(request.form("data")) OR RETURN 400 { "success": false, "error": "Invalid input" }
	files  = request.files("files")
	images = request.files("images")
	...
```

Rules for form-data:
- The JSON part is **always** the field named `data` — same name in every endpoint.
- Documents go in `files`, pictures go in `images`; repeat the key for multiple
  uploads. Do not invent `file1`, `file2`, `attachment_a`.
- Validate every upload before saving: extension, MIME type and size. Reject with
  `400` and a message naming the limit.
- **Never use the client-supplied filename as-is.** Always pass it through
  `sanitizeFileName(...)` before it becomes part of a storage key or a path — a browser
  filename can carry spaces, `/`, `#`, `?` and `..` (§11.2).
- Store the saved paths/URLs on the record; the response returns the URLs, never the
  bytes.
- An endpoint that has no upload must not be multipart — send plain JSON.

Whatever the input format, the **response format never changes** — it is always the
envelope in §7.

### 6.9 Fast queries — pagination, filters and joins

List endpoints are where a backend gets slow. The rules below are mandatory for every
`List` handler.

**Always paginate at the database.** Never load everything and slice it in application
code:

```
# Bad — pulls the whole table into memory
	orders = DB.list(Order)
	paged  = orders[offset : offset+limit]
```

```
# Good — the database does the work
	orders = DB.list(query.limit(limit).offset(offset))
```

**Count with the same filters, on the same query, before applying limit/offset** — the
`total_pages` in the response must match what the filters actually return:

```
	query = DB.query(PurchaseOrder)
	IF search != "":
		query = query.where("(po_number ILIKE ? OR title ILIKE ?)", "%"+search+"%", "%"+search+"%")
	IF status != "":
		query = query.where("status = ?", status)
	total  = DB.count(query)
	orders = DB.list(query.limit(limit).offset(offset))
```

**Build filters conditionally, never as one giant `WHERE`.** Each condition is added
only when the param was sent, so the database can still use its indexes.

**Search:**
- `ILIKE` with `%term%` for case-insensitive matching on a few named columns only —
  never on every column of the table.
- Trim the term and skip the clause when it is empty.
- Search on indexed columns; a wildcard on both sides cannot use a normal index, so
  keep the searched column list short and add a trigram/`GIN` index if a table gets big.

**Joins and eager loading — the main cause of slow lists:**

| Do not | Do instead |
|---|---|
| Eager-load five relations on a list endpoint | load only what the list actually displays; load the rest in the detail endpoint |
| Nested eager loads (`A.B.C`) on a list | fetch the child rows in one extra query keyed by the parent IDs |
| Query inside a loop (the N+1 problem) | one `WHERE parent_id IN (?)` query, then map the results in memory |
| Join several big tables just to show two columns | select only the needed columns, or a small raw query returning a flat row type |
| `SELECT *` on a wide table | select `id, po_number, status, total` |

```
# Bad — N+1: one query per order
	FOR o IN orders:
		o.items = DB.list(Item, purchase_order_id = o.id)
```

```
# Good — two queries in total
	items = DB.list(Item, WHERE "purchase_order_id IN (?)", orderIds)
	itemsByOrder = groupBy(items, "purchase_order_id")
	FOR o IN orders:
		o.items = itemsByOrder[o.id]
```

Watch for the framework's own N+1 traps: lazy-loaded relations touched inside a
serializer or a template, a computed property that queries, and an ORM that issues one
query per row when a relation is accessed. Load what you need up front, in one query.

More rules:
- **Filter in SQL, never in application code.** No loop that skips rows after fetching —
  that row should not have been fetched.
- **Sort in SQL** with an explicit `ORDER BY id ASC`; without it Postgres may return
  rows in a different order on every page and records will repeat or disappear.
- **Aggregate in SQL** (`COUNT`, `SUM`, `AVG`) — never sum an array in application code
  that the database could have summed.
- **Index every column used in `WHERE`, `JOIN` or `ORDER BY`** — add the index in the
  migration that creates the table.
- Cap `limit` at a sane maximum (e.g. 100) so one caller cannot ask for the whole table.
- A dashboard or report that needs many aggregates uses **one raw query returning a
  flat result type**, not several ORM round-trips.

---

## 7. Response envelope

Every endpoint returns a JSON object with a boolean `success`. Nothing is ever returned
bare (no top-level arrays, no plain strings).

**This section is literal and identical in every language.** The frontend must not be
able to tell what the backend is written in.

**Single object:**
```json
{
  "success": true,
  "message": "Designation Created Successfully",
  "data": { "id": 12, "name": "Team Lead" }
}
```

**Nested response variant** — some modules wrap the payload in `response`. Both forms
are accepted; pick one per module and stay consistent inside that module:
```json
{
  "success": true,
  "response": { "data": { "id": 12, "holiday": "Onam" } }
}
```

**List with pagination** — note the list payload sits under `message`:
```json
{
  "success": true,
  "message": {
    "page": 1,
    "limit": 20,
    "total_pages": 7,
    "data": [ { "id": 1 }, { "id": 2 } ]
  }
}
```

**Delete / action confirmation:**
```json
{ "success": true, "message": "Holiday deleted successfully" }
```

**Error** — one string in `error`, with the status code chosen per §6.7:
```json
{ "success": false, "error": "Holiday not found" }
```

**Field-level errors**, when the frontend must highlight inputs — still the same
envelope, with a map instead of a sentence:
```json
{
  "success": false,
  "error": "Please correct the highlighted fields",
  "errors": { "vendor_id": "Vendor is required", "quantity": "Must be greater than 0" }
}
```

Rules:
- `error` appears **only** when `success` is `false`; `data`/`message` only when `true`.
- The envelope is **identical for every input format** — JSON body, query params or
  multipart form-data all return this same shape.
- Never return a bare array, a bare string, an empty body, or a raw framework error.
- An empty list is a success: `"data": []` with `200`, never `404`.
- Never return `500` (§6.7).
- Field names in JSON are `snake_case`, whatever case the language uses internally. If
  the language is camelCase (TypeScript, Java, PHP), the serialisation layer maps the
  field to a `snake_case` JSON key — set that mapping once, globally, rather than
  annotating every field by hand where the framework allows it.
- Never return password hashes, tokens, or internal columns; if a model holds one, strip
  it before responding.
- **The framework's built-in serializer, response interceptor or resource class must be
  configured to emit exactly this shape** — not wrapped in an extra `result`, not with
  an added `statusCode`, `timestamp` or `path` field. If the framework insists on
  wrapping, replace the wrapper.

---

## 8. Model conventions

```
TYPE Designation:
	id          int             -> json "id"          primary key
	name        string          -> json "name"        unique
	description string          -> json "description"
	is_active   bool?           -> json "status"      nullable / tri-state
	reports_to  int?            -> json "reports_to"  nullable FK
	sub_roles   [Designation]   -> json "children"    relation: has-many reports_to
```

Rules:

- **Declaration order inside the file:** parent entity first, then child entities, then
  join/lookup types.
- **No methods on models.** No `validate()`, no lifecycle hooks with business rules
  (`beforeSave`, `@PrePersist`, `save()` overrides), no DB calls, no computed
  properties that query, no serialisation logic. A model is a shape, nothing more.
- **Nullable / tri-state fields are explicitly optional.** Use the language's optional
  type when "unset" must be distinguishable from `false`, `0` or `""` — a nullable
  boolean flag, a nullable FK, an optional date.
- **Relations** are declared with the ORM's own mechanism (decorator, attribute,
  annotation, relation helper). Keep them on the field, in the field's declaration
  order, and keep the JSON name `snake_case`.
- **Request-only fields** — a list of IDs the client sends that the handler expands into
  real relations — are marked as not-a-column with the ORM's ignore mechanism.
- **ID strategy:**
  - integer surrogate key → an integer `id`, backed by `SERIAL`.
  - human-readable business key → a string `id` with a **database-side default**, so
    the number is generated by Postgres and never by application code:
    ```sql
    'LEAD-' || EXTRACT(YEAR FROM CURRENT_DATE)::text || '-' || LPAD(nextval('lead_seq')::text, 3, '0')
    ```
    Use this style for identifiers the user reads and quotes, such as `PO-2026-001`.
- **Cross-module models:** import the shared type from `common/models` and reference it;
  never redeclare the same entity in two modules.
- **The model never defines the schema.** Column types, defaults, constraints and
  indexes live in the migration (§10). Where the ORM requires column metadata on the
  model to map correctly, that metadata must **match** the migration exactly — the
  migration is the source of truth and the model follows it.

---

## 9. Routing conventions

**This section is literal.** The URLs are identical in every language.

### 9.1 URL grammar

```
/api/v1/users/:user_id/<entity>                       collection
/api/v1/users/:user_id/<entity>/:id                   single record
/api/v1/users/:user_id/<entity>/:id/<action>          action on a record
/api/v1/users/:user_id/<parent>/:parent_id/<child>    nested resource
```

- Prefix is always `/api/v1`.
- The acting user is always in the path (`:user_id`, or `:customer_id` for a customer
  surface) — middleware validates it against the token.
- Entity segment is lowercase, hyphenated: `purchase-order`, `asset-type`, `payment-term`.
- Path variables are `snake_case`: `:user_id`, `:spec_id`, `:custom_id`, `:term_id`.
- Where the framework writes path variables differently (`{user_id}`, `<int:user_id>`,
  `:user_id`), use its syntax — **the name and the segment order do not change.**
- Do not let the framework pluralise, auto-generate or prefix routes for you. Resource
  generators that produce `/designations/:id` are turned off; every path is written out.

### 9.2 Verb table

| Action | Method + path suffix | Handler name |
|---|---|---|
| Create | `POST` `""` | `createX` |
| List | `GET` `""` | `listXs` / `listAllXs` |
| Filtered list | `GET` `"/filter"` | `xFilterList` |
| Get one | `GET` `"/:id"` | `getXById` |
| Update | `PATCH` `"/:id/update"` | `updateX` |
| Toggle active | `PATCH` `"/:id/is_active"` | `updateXStatus` |
| Change status | `PATCH` `"/:id/status"` | `updateXStatus` |
| Delete | `DELETE` `"/:id/delete"` | `deleteX` |
| Custom action | `POST` `"/:id/<verb>"` | `xVerb` (e.g. `purchaseOrderApproval`) |

Handler names follow the language's casing (`createX`, `CreateX`, `create_x`) but keep
the same words in the same order.

`PUT` is not used. Deletes are explicit (`/delete`) so they can't be hit accidentally.

### 9.3 Middleware placement

Middleware is **optional at the start and appended last when it exists.**

Before auth is set up — while the endpoints are being built and tested — the route is
just path + handler:

```
	app.POST(purchasePath, createPurchaseOrder)
	app.GET(purchasePath, listPurchaseOrders)
	app.GET(purchasePath + "/:id", getPurchaseOrderById)
```

Once auth exists, the middleware becomes the **last argument** of the same line:

```
	app.POST(purchasePath, createPurchaseOrder, adminMiddleware("..."))
	app.GET(purchasePath, listPurchaseOrders, adminMiddleware("..."))
	app.GET(purchasePath + "/:id", getPurchaseOrderById, adminMiddleware("..."))
```

Nothing else moves — same path variables, same handler names, same order. Adding auth
to a module is a one-argument change per line plus the `auth` import. Where the
framework attaches guards by decorator or attribute, the guard is added to the existing
declaration and nothing else changes.

Middleware functions live in `auth/` (§12). Because they may not be in place yet, a
handler never assumes the request was already checked: it reads `:user_id` and
validates it itself (§6).

### 9.4 Wiring levels

```
<entry point>
 └── initRoutes(app)                     root: CORS + aggregators
      ├── commonRoutes(app)              common: calls each common xRoutes(app)
      └── <module>Routes(app)            module: calls each module xRoutes(app)
           └── xRoutes(app)              entity: the actual POST/GET/PATCH/DELETE lines
```

Adding a new entity touches exactly one aggregator line.

If the framework has its own module/registration system (NestJS modules, Django
`INSTALLED_APPS` + `urls.py` includes, Laravel service providers, Spring
configuration), that system **is** the aggregator — it holds one registration line per
entity router and nothing else. Do not run both the framework's auto-discovery and a
hand-written aggregator.

---

## 10. Migrations

Migrations are plain SQL files. **This section is identical in every language** — only
the tool that executes the folder changes.

The ORM's auto-migration is **not** used, in any form: no `AutoMigrate`, no
`synchronize: true`, no `db push`, no `makemigrations` generating schema from models,
no `update` DDL strategy. **The SQL files are the schema source of truth.**

### 10.1 Naming

```
NNNN_<verb>_<subject>.sql
```

| Verb | Use | Example |
|---|---|---|
| `create_` | new table(s) | `0088_create_milestone.sql` |
| `alter_` | change existing table | `0089_alter_customer_table.sql` |
| `insert_` | seed data | `0101_insert_currency_defaults.sql` |

- 4-digit zero-padded, strictly increasing. Never reuse a number.
- One logical change per file; closely-related tables (a table + its join table) may
  live in the same file.
- A second database gets its own folder: `migrations_agent/`.
- **Do not use the runner's timestamp-based default name** (`20260812143355-create-x`).
  Rename to the 4-digit form; the runner sorts lexically either way.

### 10.2 File templates

Every migration file has exactly two halves: an **Up** section and a **Down** section,
separated by the runner's marker comment. The markers below are the house default; if
the project's runner uses different markers, use those — the split, the order and the
content do not change.

Nothing else belongs in the file — no `BEGIN`/`COMMIT` (the runner wraps each file in
its own transaction), no `\c`, no client meta-commands.

**a) `create_` — a table with its child and its indexes**

```sql
-- +migrate Up

CREATE TABLE milestones (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
	title TEXT NOT NULL,
	description TEXT,
	status TEXT NOT NULL DEFAULT 'open',
	start_date TIMESTAMP,
	end_date TIMESTAMP,
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE milestone_assignees (
	id SERIAL PRIMARY KEY,
	milestone_id INTEGER NOT NULL REFERENCES milestones(id) ON DELETE CASCADE,
	employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
	UNIQUE (milestone_id, employee_id)
);

CREATE INDEX idx_milestones_project_id ON milestones(project_id);
CREATE INDEX idx_milestones_status ON milestones(status);

-- +migrate Down

DROP TABLE IF EXISTS milestone_assignees;
DROP TABLE IF EXISTS milestones;
```

**b) `create_` with a human-readable business id**

The sequence is created in the same file so the default can use it, and dropped in
`Down` after the table.

```sql
-- +migrate Up

CREATE SEQUENCE purchase_order_seq START 1;

CREATE TABLE purchase_orders (
	id TEXT PRIMARY KEY DEFAULT (
		'PO-' || EXTRACT(YEAR FROM CURRENT_DATE)::text || '-' ||
		LPAD(nextval('purchase_order_seq')::text, 3, '0')
	),
	vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE RESTRICT,
	status TEXT NOT NULL DEFAULT 'draft',
	total_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
	issue_date TIMESTAMP,
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_purchase_orders_vendor_id ON purchase_orders(vendor_id);

-- +migrate Down

DROP TABLE IF EXISTS purchase_orders;
DROP SEQUENCE IF EXISTS purchase_order_seq;
```

**c) `alter_` — adding, changing and dropping columns**

Always `IF NOT EXISTS` / `IF EXISTS` so a re-run on a partially migrated database does
not fail.

```sql
-- +migrate Up

ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS quote_number TEXT;
ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;
ALTER TABLE purchase_orders ALTER COLUMN status SET DEFAULT 'draft';
UPDATE purchase_orders SET status = 'draft' WHERE status IS NULL;
ALTER TABLE purchase_orders ALTER COLUMN status SET NOT NULL;

-- +migrate Down

ALTER TABLE purchase_orders ALTER COLUMN status DROP NOT NULL;
ALTER TABLE purchase_orders DROP COLUMN IF EXISTS approved_at;
ALTER TABLE purchase_orders DROP COLUMN IF EXISTS quote_number;
```

When a column is made `NOT NULL`, backfill the existing rows in the same file first —
otherwise the migration fails on any database that already has data.

**d) `insert_` — seed / lookup data**

Idempotent, so re-running is harmless.

```sql
-- +migrate Up

INSERT INTO currencies (code, name, symbol) VALUES
	('INR', 'Indian Rupee', '₹'),
	('USD', 'US Dollar', '$'),
	('EUR', 'Euro', '€')
ON CONFLICT (code) DO NOTHING;

-- +migrate Down

DELETE FROM currencies WHERE code IN ('INR', 'USD', 'EUR');
```

**e) Enum-style values**

Prefer a `TEXT` column plus a `CHECK`, which is far easier to extend than a real
Postgres enum type.

```sql
-- +migrate Up

ALTER TABLE purchase_orders
	ADD CONSTRAINT chk_purchase_orders_status
	CHECK (status IN ('draft', 'pending', 'approved', 'rejected', 'closed'));

-- +migrate Down

ALTER TABLE purchase_orders DROP CONSTRAINT IF EXISTS chk_purchase_orders_status;
```

### 10.3 Column standards

| Concern | Standard |
|---|---|
| PK | `id SERIAL PRIMARY KEY` (or `TEXT PRIMARY KEY DEFAULT (...)` for business IDs) |
| FK owned child | `REFERENCES parent(id) ON DELETE CASCADE` |
| FK reference to a person/lookup | `REFERENCES employees(id) ON DELETE RESTRICT` |
| Free text | `TEXT` |
| Short fixed text | `VARCHAR(n)` |
| Timestamps | `TIMESTAMP`, created columns as `created_at TIMESTAMP NOT NULL DEFAULT NOW()` |
| Money | `NUMERIC(<p>,2)` |
| Uniqueness across two columns | `UNIQUE (a_id, b_id)` on the join table |
| Table names | plural, `snake_case` (`purchase_orders`, `milestone_assignees`) |
| Column names | singular, `snake_case`, matching the model's JSON name |
| Index name | `idx_<table>_<column>` |
| Constraint name | `chk_<table>_<column>` / `uq_<table>_<columns>` |

Every `Up` must have a matching `Down` that reverses it, dropping children first.

**Index every column used in a `WHERE`, `JOIN` or `ORDER BY`** — every foreign key,
every status column, every column the list endpoint filters or sorts on. Add them in
the migration that creates the table, not months later when the list is already slow
(§6.9).

Do not let the ORM's naming strategy rename tables or columns. If the ORM would map
`purchaseOrder` to `purchase_order` or `purchaseorders`, configure it to use the exact
names above.

### 10.4 Rules

- **Never edit a migration that has already been applied** anywhere. Write a new
  `alter_` file instead.
- Never renumber existing files.
- The model and the SQL must agree; if you add a column, add the model field in the
  same commit.
- Never let the ORM create, drop or alter a table at runtime.

### 10.5 How they run

Migrations run **at application startup**, from the database init in `config/`, before
the server starts listening. The folder is env-driven so nobody has to edit code:

```
	migrationsDir = env("MIGRATIONS_DIR") OR "./migrations"
	n = migrationRunner.applyUp(connection, "postgres", migrationsDir)
	print("✅ Applied " + n + " migrations")
```

For local runs `MIGRATIONS_DIR` must resolve to the repo folder (`./migrations`), not
an absolute container path. Print the applied count at startup so a developer can see
at a glance whether the schema moved.

### 10.6 Choosing and adapting the runner

Pick the runner the stack already has, and point it at `migrations/`:

| Stack | Typical runner |
|---|---|
| Node / TypeScript | `node-pg-migrate`, `umzug`, `db-migrate`, Knex migrations |
| NestJS + TypeORM | TypeORM migrations configured to read raw `.sql` |
| PHP / Laravel | Laravel migrations executing raw SQL, or Phinx |
| Python | Alembic (raw SQL in `op.execute`), or `yoyo-migrations` |
| Java / Spring | Flyway or Liquibase with SQL changelogs |
| Ruby / Rails | Rails migrations executing raw SQL |

Adaptation rules, in priority order:

1. **The file name never changes:** `NNNN_<verb>_<subject>.sql`, 4-digit, sequential.
2. **The Up/Down split never changes.** If the runner wants two files, they are
   `NNNN_<verb>_<subject>.up.sql` and `NNNN_<verb>_<subject>.down.sql` — same base name.
   If the runner wants a wrapper class or function, it holds nothing but the SQL.
3. **The SQL stays SQL.** Do not rewrite the migration as ORM schema-builder calls
   (`table.string('name')`, `Schema::create(...)`, `op.create_table(...)`). Those hide
   the constraints and indexes that §10.3 requires. Read the `.sql` file and execute it.
4. **Nothing is auto-generated from the models.** If the tool has a
   generate-from-entities command, it is not used.
5. Whatever the runner, migrations run **before the server accepts traffic**, and a
   failed migration stops startup.

---

## 11. `config/` folder

One file per external concern. Everything the app needs from the outside world is
initialised here and exposed as a module-level value.

| File | Required? | Responsibility |
|---|---|---|
| `database` | **always** | `initDb()`, the exported connection handle (and a second handle if a second database exists), migration execution |
| `email` | only if the project sends email | SMTP sender, template parsing, one `sendXEmail` per email type |
| `regex` | only if there is shared validation | validation regex constants |
| `storage` | only if the project uploads files | object-storage upload/delete (S3-compatible bucket) |
| `storage_b2` | only if that bucket API is used | object-storage upload/delete (Backblaze B2 style API) |
| `<vendor>_client` | only per integration actually used | one file per third-party API client |
| `ws_notification` | only if the project uses websockets | websocket notification config |

**Only `database` is mandatory.** Everything else in this section is optional — add the
file when the project actually needs that capability, and leave it out otherwise. A
project with no uploads has no `storage`; a project that never sends mail has no
`email`; a project using one bucket provider does not carry the other one's file. Do
not copy files "just in case" — an unused config file still needs env variables, still
gets read during review, and still rots.

What is fixed is the **shape and the contract**: when the project does need one of
these, it is written once, in `config/`, with the exported surface below, rather than a
new invention each time or a call scattered through the controllers. The same applies
to capabilities not listed here — a payment gateway, an SMS sender, a PDF service each
get their own `config/<concern>` following the same pattern.

**Credentials are read from `.env`, never written in the code.** Hardcoded keys end up
in git history and cannot be rotated. Every value below comes from the environment, and
`.env` only carries the variables the project actually uses.

Use the stack's own client libraries inside these files (the official SDK, the
framework's mailer, its filesystem abstraction). What must not vary is the **exported
function names, their parameters and their behaviour** — so a controller written for
one project reads identically in the next.

### 11.1 `config/database` — required

Exported surface:

| Export | Contract |
|---|---|
| `db` | the single shared connection/ORM handle used by every controller |
| `apiUrl` | the frontend URL, read from `FRONTEND_URL`, used to build links in emails |
| `initDb()` | called once from the entry point, before anything else |
| `runMigrations()` | called at the end of `initDb()` |

`initDb()` must:

1. Load `.env` (only in local/dev; in production the environment is already set).
2. Read `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `SSL_MODE`.
3. **Fail fast and exit** if any of them is missing — do not start with a half
   configuration and do not fall back to a default host.
4. Open the connection, print `✅ Successfully connected to the database` (or `❌` plus
   the reason and exit).
5. Assign the handle to the exported `db`.
6. Call `runMigrations()`, print `✅ Applied N migrations`, and exit on failure.

Rules:

- **Controllers never open their own connection**, never construct their own ORM client
  and never read a `DB_*` variable. They use the exported handle.
- Turn off the ORM's schema synchronisation here, explicitly, in the same options object
  where the connection is configured (§10).
- A project with a second database repeats the block in the same file as
  `initSecondDb()` with its own `SECOND_DB_*` variables, its own exported handle and its
  own migrations folder.
- Where the framework owns the connection lifecycle (a DI container, a settings module,
  a service provider), `config/database` is still the one file that configures it, and
  it still exposes the same names.

### 11.2 `config/storage` — optional, S3-compatible object storage

Exported surface:

| Export | Contract |
|---|---|
| `sanitizeFileName(name)` | returns a safe file name — see the table below |
| `uploadFile(file, key)` | uploads and returns the public URL |
| `removeFile(key)` | deletes the object, returns success/failure |

Environment: `STORAGE_REGION`, `STORAGE_BUCKET`, `STORAGE_ENDPOINT`,
`STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`. Only these five change between projects.

**`sanitizeFileName` behaviour** — replace whitespace and every character that breaks
an object key or a URL with `_`, collapse runs of `_`, and trim leading/trailing `.`
and `_`:

| Incoming filename | After |
|---|---|
| `Quote #12 (final).pdf` | `Quote_12_final.pdf` |
| `../../etc/passwd` | `etc_passwd` |
| `site photo 2026.jpg` | `site_photo_2026.jpg` |
| `report&summary%.xlsx` | `report_summary.xlsx` |

Rules:

- **The object key always starts with the entity and its id** — `invoice/INV-2026-014/scan.pdf`
  — so the bucket stays browsable and one record's files are together.
- The database stores the returned **URL**, never the bytes.
- Keep the user's original filename in a `file_name` column for display; sanitise only
  the key.
- Deleting a record deletes its objects.
- **One copy of `sanitizeFileName` in the whole repo**, in this file. Never a second
  copy inside a module.

### 11.3 `config/storage_b2` — optional

Same three exports, same contract, for a Backblaze-B2-style API. A project carries this
file **or** `storage`, not both.

### 11.4 `config/email` — optional

Exported surface: **one `sendXEmail(...)` function per email type**, and nothing else.
Everything below it is private to the file:

- a private email type holding `template path`, `subject`, `data map`, `rendered body`;
- a private `parse()` that renders the template file with the data map;
- a private `send(to)` that talks to SMTP.

```
FUNC sendEmployeeEmail(employee, emailType) -> error:
	data = { "Username": employee.name, "Link": apiUrl + "/reset-password?token=" + employee.token }
	SWITCH emailType:
		"forgot_password" -> template = "templates/forgot_password.html", subject = "Reset Your Password"
		"user_created"    -> template = "templates/new_user_created.html", subject = "Welcome! Please Set Your Password"
		default           -> RETURN error("invalid email type")
	render(template, data)
	send(employee.email)
```

Environment: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_SENDER`,
`MAIL_FROM`.

Rules: templates are referenced by path, never inlined as strings in code; rendering and
sending are separate steps; the controller ignores the returned error only when the
email is not critical to the request; never block a response on a slow mail server for
bulk sends — call it from the scheduler instead.

### 11.5 `config/regex` — optional

Plain constants, one per rule, compiled where used. A short comment is allowed when the
pattern is not obvious.

```
EMAIL_REGEX    = ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
# Accepts international and local forms: optional '+', then 7-20 digits,
# spaces, dots, hyphens or brackets.
PHONE_REGEX    = ^\+?[0-9][0-9\s().-]{6,19}$
GST_REGEX      = ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$
PASSWORD_REGEX = ^.{8,}$
```

```
	IF NOT matches(EMAIL_REGEX, input.email):
		RETURN 400 { "success": false, "error": "Please enter a valid email address" }
```

### 11.6 `.env`

Only the database block is always present. Keep the block for a capability **only if the
project has that `config` file** — an empty `SMTP_*` block in a project that never sends
mail is noise.

```
# required
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=****
DB_NAME=myproject
SSL_MODE=disable
MIGRATIONS_DIR=./migrations
FRONTEND_URL=http://localhost:5173

# only with config/storage
STORAGE_REGION=
STORAGE_BUCKET=
STORAGE_ENDPOINT=
STORAGE_ACCESS_KEY=
STORAGE_SECRET_KEY=

# only with config/email
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
MAIL_SENDER=
MAIL_FROM=
```

`.env` is git-ignored and a `.env.example` with empty values is committed in its place.
Any new variable is read in `config/`, never scattered through controllers (the one
accepted exception is entry-point wiring). If the framework has its own settings/config
object, `config/` is what populates it — the variable is still read in exactly one
place.

---

## 12. `auth/` folder

`auth/auth.<ext>` holds key loading, claim types, token extraction and the middleware
constructors. Structural rules only (permission design lives in its own document):

- Module-level key material — the private key and public key — loaded once from the
  entry point at startup via `loadPrivateKey(...)` / `loadPublicKey(...)`.
- Claim types are declared next to the extractor that uses them:
  ```
  TYPE CustomClaims:
  	user_id   int    -> json "user_id"
  	role_id   int    -> json "role_id"
  	user_type string -> json "user_type"
  	+ the standard registered claims (iss, sub, exp, ...)
  ```
- File order: imports → key vars → shared types → `loadXKey` funcs → middleware
  constructors → claim types + `extractX` helpers (private parsing helpers such as
  `cleanPublicKey` / `parsePublicKey` sit immediately above the extractors that use
  them).
- Two middleware shapes exist:
  - a **plain gate** — takes the next handler, returns a handler;
  - a **parameterised gate** — takes an argument (a permission name, a role) and
    returns the middleware.
  Where the framework uses guard classes or attributes instead, the same two shapes
  apply: one that gates, one that gates with an argument.
- Middleware returns `401` with `{"error": "..."}` and never continues on failure.
- Controllers never parse tokens themselves; they trust `:user_id` after middleware, and
  still validate it against the database (§6).

---

## 13. `scheduler/` folder

```
FUNC startCronJobs():
	paymentVerificationCron()
	invoiceCronJobs()
	emailCronJobs()

FUNC paymentVerificationCron():
	cron = newScheduler()
	cron.add("*/5 * * * *", () => oneTimePaymentVerificationCron())
	cron.start()

FUNC invoiceCronJobs():
	cron = newScheduler(timezone: "Asia/Kolkata")
	cron.add("1 0 * * *", () => {
		log("Running daily invoice job")
		createUpcomingInvoices()
	})
	cron.start()
```

Rules:

- `startCronJobs()` is the only exported entry point, called once from the entry point;
  it does nothing but call one `xCronJobs()` per domain.
- Each domain function builds **its own** scheduler instance and starts it.
- **No business logic in the scheduler.** The closure only calls exported controller
  functions; the logic lives in `controllers/`.
- Set the timezone explicitly when the schedule is business-time sensitive — never rely
  on the server's local zone.
- Log a one-line start message inside the job so local runs are traceable.
- If the framework has its own scheduling mechanism (decorators, a queue worker, a task
  registry), it is registered from `scheduler/` and still calls a controller function
  and nothing more.

---

## 14. `templates/` and email

- Flat folder, `snake_case.html`, one file per email: `po_approval.html`,
  `po_status.html`, `new_user_created.html`, `forgot_password.html`.
- **No sub-folders, no partials, no layout inheritance.** One email, one file.
- Parsed by `config/email` (§11.4), path relative to the working directory:
  `templates/po_approval.html`.
- The values a template needs are passed as a **flat key/value map** built in the
  `sendXEmail` function. Placeholders in the HTML use the same keys:
  ```html
  <p>Hello {{Username}},</p>
  <p>Purchase order <b>{{PO_ID}}</b> for {{Vendor}} is awaiting your approval.</p>
  <a href="{{Link}}">Open the purchase order</a>
  ```
  (Use the template engine's own placeholder syntax; the **keys** are what must match.)
- Rendering and sending are separate steps, so a template can be rendered and checked
  without sending anything.
- Controllers call `sendXEmail(...)` only; they never render a template or open an SMTP
  connection directly.
- **Every placeholder the template uses must be set in the data map** — a missing key
  renders as empty text with no error, which is how blank emails go out.
- Keep the HTML simple: inline styles, tables for layout, no external CSS or JS — mail
  clients strip them.
- Do not put the app's web views in this folder. `templates/` is email only.

---

## 15. The entry point

The entry point file (`main.ts`, `index.js`, `app.py`, `Application.java`, `bootstrap`
— whatever the stack names it) does **wiring only** — no logic, no route declarations,
no queries.

```
FUNC main():
	config.initDb()                        # connects + runs migrations, exits on failure
	scheduler.startCronJobs()
	auth.loadPrivateKey("./private_ec.pem")   OR exit with ❌
	auth.loadPublicKey("./public_ec.pem")     OR exit with ❌
	app = createApp()
	controllers.frontendUrl = env("FRONTEND_URL")
	routers.initRoutes(app)
	print("Server is running on port 8080")
	app.listen(8080)
```

Fixed order: `initDb` → `startCronJobs` → key loading → create the app → global wiring →
`initRoutes` → listen. **Keep it under ~40 lines.**

The port is `8080` unless the deployment dictates otherwise, and it comes from the
environment with `8080` as the default.

---

## 16. Adding a new feature — end-to-end checklist

Example: adding a **Vendor Contract** entity to the `Purchase` module.

1. **Migration** — `migrations/0031_create_vendor_contract.sql`
   ```sql
   -- +migrate Up
   CREATE TABLE vendor_contracts (
   	id SERIAL PRIMARY KEY,
   	vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
   	title TEXT NOT NULL,
   	start_date TIMESTAMP,
   	end_date TIMESTAMP,
   	is_active BOOLEAN DEFAULT TRUE,
   	created_at TIMESTAMP NOT NULL DEFAULT NOW()
   );
   CREATE INDEX idx_vendor_contracts_vendor_id ON vendor_contracts(vendor_id);
   -- +migrate Down
   DROP TABLE IF EXISTS vendor_contracts;
   ```

2. **Model** — `modules/Purchase/models/vendor_contract.<ext>`
   ```
   TYPE VendorContract:
   	id         int        -> json "id"          primary key
   	vendor_id  int        -> json "vendor_id"
   	title      string     -> json "title"
   	start_date timestamp? -> json "start_date"
   	end_date   timestamp? -> json "end_date"
   	is_active  bool?      -> json "is_active"
   	created_at timestamp  -> json "created_at"
   ```

3. **Controller** — `modules/Purchase/controllers/vendor_contract.<ext>`
   Order: imports → input types → helpers → `createVendorContract`,
   `listVendorContracts`, `getVendorContractById`, `updateVendorContract`,
   `updateVendorContractStatus`, `deleteVendorContract`. Each handler follows §6.

4. **Router** — `modules/Purchase/routers/vendor_contract.<ext>`
   ```
   vendorContractPath = "/api/v1/users/:user_id/vendor-contract"

   FUNC vendorContractRoutes(app):
   	app.POST(vendorContractPath, createVendorContract)
   	app.GET(vendorContractPath, listVendorContracts)
   	app.GET(vendorContractPath + "/:id", getVendorContractById)
   	app.PATCH(vendorContractPath + "/:id/update", updateVendorContract)
   	app.PATCH(vendorContractPath + "/:id/is_active", updateVendorContractStatus)
   	app.DELETE(vendorContractPath + "/:id/delete", deleteVendorContract)
   	RETURN app
   ```
   Once the auth layer exists, append the middleware as the last argument of each line
   (§5.3, §9.3) — nothing else in the file changes.

5. **Module aggregator** — add one line to `modules/Purchase/routers/routers.<ext>`
   ```
   FUNC purchaseRoutes(app):
   	purchaseOrderRoutes(app)
   	vendorContractRoutes(app)   # ← new
   ```
   (If the module is new, also add `purchaseRoutes(app)` to `routers/routes.<ext>`.)

6. **Optional pieces**
   - recurring job → new `xCronJobs()` in `scheduler/` calling an exported controller
     function.
   - email → `templates/vendor_contract_expiry.html` + a `sendXEmail` pair in
     `config/email`.

7. **Run and verify**
   - build/typecheck the project and start it;
   - confirm the migration count printed at startup increased;
   - hit each new route and check the response against §7 — status `200`, `success`
     present, list under `message` with `total_pages`;
   - hit one route with a bad id and confirm it returns `400`/`404`, not `500`.

---

## 17. Anti-patterns — do not do these

| Anti-pattern | Do instead |
|---|---|
| Business logic or DB calls in `models/` | models are declarations only; logic in `controllers/` |
| Lifecycle hooks (`beforeSave`, `@PrePersist`) carrying business rules | the rule lives in the handler, where it can return a clean error |
| DB queries in `routers/` | routers only map paths → handlers |
| Repeating the full route literal on every line | one path variable + suffixes |
| Declaring routes inside the root or module aggregator | aggregators only call `xRoutes(app)` |
| Letting the framework auto-generate REST routes for a resource | write every path out per §9 |
| Reading env variables across controllers | read env in `config/`, expose a value |
| API keys, SMTP passwords or bucket secrets written in the code | read them from `.env` (§11) — committed keys cannot be rotated |
| Reinventing the storage/email/database wiring per project | one file per concern in `config/`, same exported names (§11) |
| Copying `storage` / `email` / `ws_notification` into a project that does not use them | only `database` is mandatory (§11) |
| `.env` blocks for capabilities the project does not have | keep only the variables the existing config files read |
| Storing uploaded bytes in the database | upload to the bucket, store the returned URL (§11.2) |
| Using the client-supplied filename directly in a storage key or path | `sanitizeFileName(...)` (§11.2) |
| A second copy of `sanitizeFileName` in a module | one copy in `config/storage`, called everywhere |
| A migration without a working `Down`, or without indexes on its FKs | follow the templates in §10.2 |
| Opening a new DB connection in a controller | always use the shared handle |
| Editing an already-applied migration | add a new `alter_` migration |
| ORM auto-migration / `synchronize` / `db push` alongside SQL migrations | SQL files are the only schema source (§10) |
| Writing migrations as ORM schema-builder calls instead of SQL | keep the SQL in the `.sql` file (§10.6) |
| Returning bare arrays / strings / framework error objects from a handler | the `success` envelope from §7 |
| A response interceptor that wraps the envelope in another object | emit §7 exactly |
| `201 Created` / `204 No Content` from the framework's defaults | `200` for every success (§6.7) |
| Mixing `{"data": ...}` and `{"response": {"data": ...}}` in one module | pick one per module and keep it |
| camelCase keys in the JSON response | `snake_case`, set globally in the serializer (§7) |
| Helper functions interleaved between handlers | helpers above the handler block, or in `helper.<ext>` |
| Reading a query param, or declaring a var, in the middle of a handler | all inputs, vars and defaults in the input block at the top (§6) |
| Copying the same big helper into two controller files of a module | move it once into the module's `helper.<ext>` (§5.6.1) |
| Indenting with the space bar | indent with tabs — formatter + `.editorconfig` (§5.8) |
| Paragraph comments, or comments restating the code | 1–2 line comments, only where the reason is not obvious (§5.8) |
| Generated doc-comment blocks on every function | write one only where a public contract needs it |
| Blank rows inside a function, or two blank lines in a row | no blank line inside a function, exactly one between functions (§5.8) |
| Commented-out old code left in the file | delete it — git keeps the history |
| Creating `helper.<ext>` for a helper only one file uses | keep it in that file's helper block |
| `utils` / `misc` / `common` / `shared` inside a controllers folder | `helper` |
| Framework folder names (`entities/`, `schemas/`, `services/`, `resources/`) replacing the three | `controllers/`, `models/`, `routers/` in every language (§4.1) |
| Deleting a record without checking dependents | dependency guards first (§6.5) |
| Blind save of the parsed body on update | field-by-field diff with `changes` (§6.3) |
| Leaking driver/SQL errors to the client | fixed human-readable messages |
| Returning `500 Internal Server Error` | classify it — `400`, `404`, `403`, `409` (§6.7) |
| Filters or search sent in the request body | query params on `GET` (§6.8) |
| Multipart form-data on an endpoint with no upload | plain JSON body |
| Spreading record fields across many form keys | one JSON string in `data`, binaries in `files` / `images` (§6.8) |
| Fetching everything then slicing/filtering/summing in application code | `WHERE` + `LIMIT`/`OFFSET` + `COUNT`/`SUM` in SQL (§6.9) |
| A DB query inside a loop (N+1) | one `WHERE id IN (?)` query, then map in memory (§6.9) |
| A lazy relation touched inside a serializer or template | load it up front, in one query (§6.9) |
| Eager-loading every relation on a list endpoint | load only what the list shows; full detail in `GET /:id` |
| Listing without an explicit `ORDER BY` | always sort explicitly, or pages repeat rows |
| Multi-table writes without a transaction | one transaction, handle passed as the first parameter (§6.6) |
| Business logic inside a cron closure | the closure calls an exported controller function |
| One giant controller covering several entities | one file per entity |
| Showing the user code from a language the project does not use | detect the stack first, then stay in it (§0) |
