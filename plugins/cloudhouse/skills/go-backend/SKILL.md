---
name: go-backend
description: "Go + Echo backend standard — folder layout, file naming, in-file ordering, handler body structure, response envelope, query params and form-data input, fast queries, migrations, config boilerplate. Use for ANY Go backend work — creating a new backend, adding a module/entity/endpoint, writing or editing controllers, models, routers, migrations, schedulers or config, and for auditing an existing backend against the standard. Invoked as /cloudhouse:go-backend."
---

# Go Backend Skill — build and audit to one fixed standard

You are working under a fixed house standard. **Part B of this file is the standard.**
It is not advice and not a starting point: it is the specification. Do not substitute
your own conventions, do not "improve" the layout, and do not follow patterns you see
elsewhere in the codebase if they contradict Part B.

Read Part B in full before writing or changing a single line of Go or SQL.

---

## 1. Pick the mode

Read what the user typed after `/go-backend` and choose one:

| The user asks for | Mode |
|---|---|
| a new backend, a new module, a new entity/endpoint, a new migration | **A — Build** |
| "update / check / review / restructure the current backend" | **B — Audit** |
| anything else touching backend code (a bug fix, a tweak) | **C — Edit** |

If it is genuinely unclear, ask once, then proceed.

---

## 2. Mode A — Build

1. Decide the layout using §2 of Part B (flat vs `common/` + `modules/`) and say which
   one you picked and why, in one line.
2. Create the files in this order, one entity at a time: **migration → model →
   controller → router → module aggregator → root aggregator**, then scheduler/template
   if the feature needs them (§16).
3. Every file follows its skeleton in §5. Every handler follows the input block and
   body sequence in §6. Every response uses the envelope in §7.
4. Run the self-check in section 5 below before reporting done.

## 3. Mode B — Audit an existing backend

Do **not** change anything until the user approves.

1. List the tree (`find . -name "*.go" -o -name "*.sql"`) and read enough of it to judge
   — at minimum `main.go`, the root router, one full controller, one model, one router,
   two migrations, and `config/`.
2. Compare against Part B and produce this table, most severe first:

   | # | File | Rule broken (§) | What is wrong | Fix |
   |---|---|---|---|---|

   Check at least: folder layout (§2, §3), file naming (§4), in-file ordering (§5),
   shared helpers in `helper.go` (§5.6.1), tabs / blank lines / comments (§5.8),
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
   model and router together), and the code must still build after each entity.
6. Re-run the self-check and report what is now compliant and what the user chose to
   leave.

## 4. Mode C — Edit

Small change, same rules. Before editing a file, check whether the file already
follows Part B. If it does not, fix the part you are touching to be compliant, mention
the rest in one line, and do not silently spread the old pattern.

---

## 5. Self-check — run before saying you are done

Go through this list every time. If any answer is "no", fix it before reporting.

- [ ] Files are in the right folders, named after the entity, `snake_case.go` (§3, §4)
- [ ] Every file's internal order is imports → package vars → structs → helpers →
      handlers (§5)
- [ ] Shared helpers are in the module's `helper.go`, not duplicated (§5.6.1)
- [ ] Indented with **tabs**; no blank line inside any function; exactly one between
      functions; no paragraph comments; no commented-out code (§5.8)
- [ ] Every handler opens with the input block: path params → query params → vars →
      conversions/defaults — and nothing new is declared further down (§6)
- [ ] No `500` anywhere; every error is 400/401/403/404/409 with a clean sentence (§6.7)
- [ ] Filters and pagination come from query params; uploads use `data` + `files` /
      `images`; `file.Filename` always passed through `SanitizeFileName` (§6.8, §11.2)
- [ ] Lists paginate, count and sort in SQL; no query inside a loop; no `Preload` the
      list does not display (§6.9)
- [ ] Every response uses the `success` envelope; no bare arrays or raw errors (§7)
- [ ] Models are struct-only, tags `json` then `gorm`, pointers for nullable (§8)
- [ ] Routes follow `/api/v1/users/:user_id/<entity>/:id/<action>`; paths built from a
      `var`; middleware last (or absent if auth is not set up yet) (§9)
- [ ] Migration numbered `NNNN_verb_subject.sql`, has a working `Down`, indexes every
      FK / filtered / sorted column (§10)
- [ ] No hardcoded keys — everything through `.env` and `config/` (§11)
- [ ] `gofmt` clean; `go build ./...` passes

---

## 6. Non-negotiables

These are the ones that get silently broken. Never break them, whatever the
conversation drifts into:

1. **Tabs, not spaces.** No blank lines inside a function.
2. **No `500`.** Classify the failure.
3. **The `success` envelope on every single response**, including errors and empty lists.
4. **Input block at the top of every handler.** No query param read halfway down.
5. **One entity per file**, matching names across `controllers` / `models` / `routers`.
6. **Aggregators only aggregate.** No route declared in `routes.go`.
7. **Models hold no logic.** Routers hold no logic.
8. **SQL migrations are the schema.** Never `AutoMigrate`. Never edit an applied file.
9. **No secrets in code.**
10. **No N+1 queries. No unpaginated lists.**

If the user explicitly asks for something that breaks a rule, say which rule in one
sentence, then do what they asked.

## 7. Staying on the standard for the whole session

This standard applies to every later message in the conversation, not only the one
that invoked `/go-backend`. Before each new file you write or edit, re-check section 5.
If the conversation has been long, re-read the relevant section of Part B rather than
working from memory.

---
---

# PART B — THE STANDARD

Everything below this line is the specification. Follow it exactly.

# Backend Structure & Coding Standard (Go + Echo)

This document defines **how a Go backend is organised and written** in our team — the
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

---

## 1. Stack baseline

The backend is Go `1.24`. These are the only libraries used; they are declared in
`go.mod`. Throughout this document the module is called `myproject` — substitute your
own module name:

| Purpose | Library |
|---|---|
| HTTP framework | `github.com/labstack/echo/v4` |
| ORM | `gorm.io/gorm` + `gorm.io/driver/postgres` |
| SQL migrations | `github.com/rubenv/sql-migrate` |
| Cron / schedulers | `github.com/robfig/cron/v3` |
| Env loading | `github.com/joho/godotenv` |
| JWT | `github.com/golang-jwt/jwt/v5` |
| WebSocket | `github.com/gorilla/websocket` |
| Money | `github.com/shopspring/decimal` |
| Excel export | `github.com/xuri/excelize/v2` |

Rules:

- **One Go module per backend.** The module name is short, lowercase and
  product-based — here it is `myproject`.
  All internal imports are absolute from the module root — never relative
  (no `"./config"`, no `"../models"`):
  ```go
  import (
  	"myproject/config"
  	"myproject/common/models"
  	"myproject/modules/Purchase/controllers"
  )
  ```
- **Database is PostgreSQL only.** No other driver is configured.
- **Local run:**
  ```bash
  cd <project>/backend
  go run .
  # Server is running on port 8080
  ```
- **Do not add a new third-party library** if the job can be done with the ones above
  or the standard library.

---

## 2. Choosing the layout

There are exactly **two approved layouts**. Pick by the shape of the product, not by
personal preference.

### 2.1 Flat layout — single-surface project

Use when the project has **one module and one kind of user** (no separate
admin/staff/customer sides, no independent product areas).

```
controllers/   models/   routers/
```
sit directly at the project root, next to `config/`, `migrations/` and `main.go`.
Nothing is nested; every controller of the product lives in the one `controllers/`
folder, one file per entity.

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
the sub-module again carries the same three folders and its own `routers.go`.

### 2.3 Rules that apply to both

- Anything shared by two or more modules goes to `common/`, never duplicated.
- A module never imports another module's `models` unless the relation is real. An
  entity needed by two modules (Employee, Company, Customer) belongs in
  `common/models` and is imported from there:
  ```go
  import common "myproject/common/models"
  ```
- **Graduation rule:** a feature starts in the flat/root folders; the moment it grows
  past ~3 entities, or gains its own user surface, it moves into `modules/<Name>/`
  with the three folders. Move all three files (controller, model, router) together.
- `config/`, `auth/`, `migrations/`, `scheduler/`, `templates/` are **always at the
  root** in both layouts. They are never duplicated inside a module.

---

## 3. Complete folder structure reference

### 3.1 Flat layout (single-surface project)

```
<project>/
├── .env                              # local env vars, never committed
├── go.mod
├── go.sum
├── main.go                           # entry point only — no logic
│
├── auth/
│   └── auth.go                       # JWT load/parse + middleware definitions
│
├── common/                           # cross-cutting pure helpers (no HTTP, no DB writes)
│   ├── jwt.go                        # claims structs
│   ├── regex.go                      # validation regexes
│   └── security.go                   # hashing, random tokens
│
├── config/                           # one file per external concern (only the ones used)
│   ├── database.go                   # required — InitDB(), config.DB, runs migrations
│   ├── email.go                      # optional — SMTP sender + template parsing
│   ├── storage.go                    # optional — file upload / delete
│   └── regex.go                      # optional — shared validation patterns
│
├── controllers/                      # one file per entity — all HTTP handlers
│   ├── activity_log.go
│   ├── dashboard.go
│   ├── department.go
│   ├── designation.go
│   ├── global_search.go
│   ├── login.go
│   └── reports.go
│
├── models/                           # one file per entity — struct definitions only
│   ├── activity_log.go
│   ├── department.go
│   ├── designation.go
│   └── staff.go
│
├── routers/                          # one file per entity + one aggregator
│   ├── route.go                      # InitRoutes(e) — CORS + calls every XRoutes(e)
│   ├── dashboard.go
│   ├── department.go
│   ├── designation.go
│   └── login.go
│
├── migrations/                       # NNNN_<verb>_<subject>.sql, sequential
│   ├── 0001_create_role.sql
│   ├── 0002_create_department.sql
│   └── 0003_alter_department.sql
│
├── scheduler/
│   └── scheduler.go                  # StartCronJobs() + one func per domain
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
├── go.mod
├── go.sum
├── main.go
│
├── auth/
│   └── auth.go
│
├── common/                           # shared across every module
│   ├── controllers/
│   │   ├── company.go
│   │   ├── department.go
│   │   ├── employee.go
│   │   ├── login.go
│   │   └── shift.go
│   ├── models/
│   │   ├── company.go
│   │   ├── department.go
│   │   ├── employee.go
│   │   └── shift.go
│   └── routers/
│       ├── routers.go                # CommonRoutes(e) / InitRoutes(e) aggregator
│       ├── company.go
│       ├── department.go
│       ├── employee.go
│       └── shift.go
│
├── config/                           # only the files this project needs
│   ├── database.go
│   ├── email.go
│   ├── regex.go
│   ├── storage.go                    # optional — file upload / delete
│   └── ws_notification.go            # optional — websocket hub config
│
├── modules/
│   ├── CRM/
│   │   ├── controllers/
│   │   │   ├── customer.go
│   │   │   ├── invoices.go
│   │   │   ├── leads.go
│   │   │   └── payment.go
│   │   ├── models/
│   │   │   ├── customer.go
│   │   │   ├── invoices.go
│   │   │   └── leads.go
│   │   └── routers/
│   │       ├── routers.go            # CRMRoutes(e) — calls the module's XRoutes(e)
│   │       ├── customer.go
│   │       └── leads.go
│   │
│   ├── Projects/
│   │   ├── controllers/
│   │   │   ├── milestone.go
│   │   │   ├── project.go
│   │   │   ├── project_task.go
│   │   │   └── subtask.go
│   │   ├── models/
│   │   └── routers/
│   │       └── routers.go            # ProjectsRoutes(e)
│   │
│   ├── HumanResource/
│   │   ├── controllers/
│   │   ├── models/
│   │   └── routers/
│   │       └── routers.go            # HumanResourceRoutes(e)
│   │
│   ├── Agent/
│   │   ├── controllers/
│   │   │   ├── agent.go
│   │   │   ├── helper.go             # helpers shared by this module's controllers
│   │   │   └── work_diary.go
│   │   ├── models/
│   │   └── routers/
│   │       └── routers.go            # AgentsRoutes(e)
│   │
│   └── Supports/                     # a module may nest a sub-module
│       ├── controllers/
│       ├── models/
│       ├── routers/
│       │   └── routers.go            # SupportRoutes(e)
│       └── VendorSupport/            # sub-module: same three folders again
│           ├── controllers/
│           ├── models/
│           └── routers/
│               └── routers.go        # VendorSupportRoutes(e)
│
├── migrations/                       # main database
│   ├── 0001_create_company.sql
│   └── 0088_create_milestone.sql
│
├── migrations_agent/                 # a second database gets its own migrations folder
│   └── 0001_create_agent_tables.sql
│
├── scheduler/
│   └── scheduler.go
│
└── templates/
    ├── forgot_password.html
    ├── new_user_created.html
    └── support_ticket_email.html
```

### 3.3 Worked example — a filled-in modular project

This is what §3.2 looks like once it is filled with real files, for a project that has
purchasing, assets, finance and activity-log areas (`module myproject`). Use it as the
model when laying out your own repository.

```
<project>/
└── backend/
    ├── .env
    ├── go.mod
    ├── go.sum
    ├── main.go
    │
    ├── auth/
    │   └── auth.go
    │
    ├── common/                       # entities used by every module
    │   ├── controllers/
    │   │   ├── banks.go
    │   │   ├── company.go
    │   │   ├── currency.go
    │   │   ├── customers.go
    │   │   ├── employees.go
    │   │   ├── global_search.go
    │   │   ├── login.go
    │   │   ├── notification_hub.go
    │   │   ├── project.go
    │   │   ├── scope.go
    │   │   ├── subtask.go
    │   │   ├── vendors.go
    │   │   └── ws_hub.go
    │   ├── models/
    │   │   ├── banks.go
    │   │   ├── company.go
    │   │   ├── customers.go
    │   │   ├── employees.go
    │   │   ├── project.go
    │   │   ├── scope.go
    │   │   ├── subtask.go
    │   │   └── vendors.go
    │   └── routers/
    │       ├── routers.go            # CommonRoutes(e)
    │       ├── banks.go
    │       ├── company.go
    │       ├── customers.go
    │       ├── employees.go
    │       └── login.go
    │
    ├── config/                       # only the files this project needs
    │   ├── database.go
    │   ├── email.go
    │   ├── integration_client.go
    │   └── regex.go
    │
    ├── modules/
    │   ├── Purchase/                 # purchase orders, specs, approval config
    │   │   ├── controllers/
    │   │   │   ├── purchase_order.go
    │   │   │   ├── specification.go
    │   │   │   └── helper.go         # helpers shared by the two files above
    │   │   ├── models/
    │   │   │   └── purchase_order.go
    │   │   └── routers/
    │   │       ├── routers.go        # PurchaseRoutes(e)
    │   │       └── purchase_order.go
    │   │
    │   ├── Assets/
    │   │   ├── controllers/assets.go
    │   │   ├── models/assets.go
    │   │   └── routers/
    │   │       ├── routers.go        # AssetRoutes(e)
    │   │       └── assets.go
    │   │
    │   ├── Finance/                  # invoices, expenses, payscale, currency convert
    │   │   ├── controllers/
    │   │   ├── models/
    │   │   └── routers/routers.go    # FinanceRoutes(e)
    │   │
    │   └── ActivityLog/
    │       ├── controllers/activity_log.go
    │       ├── models/activity_log.go
    │       └── routers/
    │           ├── routers.go        # ActivityLogRoutes(e)
    │           └── activity_log.go
    │
    ├── routers/
    │   └── routes.go                 # InitRoutes(e) — CORS + every module aggregator
    │
    ├── migrations/
    │   ├── 0001_create_customer.sql
    │   ├── 0002_create_company.sql
    │   └── 0017_create_activity_logs.sql
    │
    ├── migrations_agent/
    │
    ├── scheduler/
    │   └── scheduler.go
    │
    └── templates/
        ├── forgot_password.html
        ├── new_user_created.html
        ├── po_approval.html
        └── po_status.html
```

**Migrating a flat project into this shape:** if an existing project keeps
`purchase_order.go`, `assets.go` and `activity_log.go` as flat root-level
`controllers/`, `models/`, `routers/` files, each of those becomes a module folder
under `modules/` with its own three folders and a `routers.go` aggregator. Move the
controller, model and router of one entity together, in one commit. The root
`routers/routes.go` stays as the single `InitRoutes(e)` entry that mounts CORS and
calls `commonRouters.CommonRoutes(e)` plus each module aggregator.

---

## 4. File naming

| Item | Rule | Example |
|---|---|---|
| Go file | `snake_case.go`, named after the **entity**, singular | `purchase_order.go`, `activity_log.go` |
| Triplet | the same base name in all three folders | `models/leads.go` ↔ `controllers/leads.go` ↔ `routers/leads.go` |
| Aggregator | `routers.go` inside `common/` and inside every module; `routes.go` at the project root | `modules/CRM/routers/routers.go`, `routers/routes.go` |
| Module folder | `PascalCase`, singular or natural product name | `CRM/`, `Projects/`, `HumanResource/`, `Purchase/` |
| Shared helper file | `helper.go`, one per controllers package, for helpers used by two or more controller files (§5.6.1) | `modules/Purchase/controllers/helper.go` |
| Config file | one per external concern, lowercase; only the ones the project uses (§11) | `database.go`, `email.go`, `storage.go` |
| Migration | `NNNN_<verb>_<subject>.sql`, zero-padded to 4 | `0088_create_milestone.sql` |
| Template | `snake_case.html`, describing the email | `po_approval.html`, `forgot_password.html` |

Additional rules:

- **One entity per file.** If `purchase_order.go` also handles specifications and
  approval configs, split it: `purchase_order.go`, `specification.go`,
  `approval_config.go`.
- **Never** use `utils.go`, `misc.go`, `common.go` inside a controllers package —
  the name is `helper.go`.
- Test files (rare, but allowed) use Go's own convention: `rebill_client_rejected_test.go`.
- No spaces in file names.

---

## 5. In-file ordering — the house format

This is the part every file must obey. The order is fixed; readers should always find
the same thing in the same place.

### 5.1 Universal order

```
1. package <name>
2. import ( ... )                 std lib first, then third-party, then internal
3. package-level const / var      route paths, status maps, singletons
4. type declarations              request/input structs, response structs
5. helper functions               unexported, small, no echo.Context
6. exported handlers / API funcs  the real work
```

**Import grouping** — three blocks separated by a blank line, in this order:

```go
import (
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"myproject/common/models"
	"myproject/config"
)
```

### 5.2 `models/<entity>.go`

Only imports, then structs. Nothing else — no methods, no DB calls, no validation.

```go
package models

import "time"

// Parent entity first, then its children, then join/lookup structs.
type PurchaseOrder struct {
	ID          string              `json:"id" gorm:"primaryKey"`
	VendorID    int                 `json:"vendor_id"`
	Vendor      Vendor              `json:"vendor" gorm:"foreignKey:VendorID"`
	Status      string              `json:"status"`
	Items       []PurchaseOrderItem `json:"items" gorm:"foreignKey:PurchaseOrderID"`
	IsActive    *bool               `json:"status_active"`
	CreatedAt   time.Time           `json:"created_at"`
}

type PurchaseOrderItem struct {
	ID              int     `json:"id" gorm:"primaryKey;autoIncrement"`
	PurchaseOrderID string  `json:"purchase_order_id"`
	Description     string  `json:"description"`
	Quantity        int     `json:"quantity"`
	UnitPrice       float64 `json:"unit_price"`
}
```

If a model file needs a `func`, it is in the wrong place — move it to the controller.

### 5.3 `routers/<entity>.go`

Order: imports → `var` path constants → `XRoutes(e)`.

**Start here — no middleware yet.** At the beginning of a project, or while the
endpoints are still being tested, auth is usually not wired up. Write the routes with
just the handler; nothing else about the file changes:

```go
package routers

import (
	"myproject/modules/Purchase/controllers"

	"github.com/labstack/echo/v4"
)

var specPath = "/api/v1/users/:user_id/purchase/spec"
var purchasePath = "/api/v1/users/:user_id/purchase-order"
var approvalPath = "/api/v1/users/:user_id/purchase/approval"

func PurchaseOrderRoutes(e *echo.Echo) *echo.Echo {
	// Specification
	e.POST(specPath, controllers.CreateSpecification)
	e.GET(specPath, controllers.ListAllSpecifications)
	// Purchase Order
	e.POST(purchasePath, controllers.CreatePurchaseOrder)
	e.GET(purchasePath, controllers.ListPurchaseOrders)
	e.GET(purchasePath+"/:id", controllers.GetPurchaseOrderById)
	e.PATCH(purchasePath+"/:id/update", controllers.UpdatePurchaseOrder)
	e.DELETE(purchasePath+"/:id/delete", controllers.DeletePurchaseOrder)
	return e
}
```

**Later — the same file with auth added.** When the auth layer is ready, the
middleware is appended as the **last argument** of each line. No path, no handler and
no line order changes; only the `myproject/auth` import is added:

```go
package routers

import (
	"myproject/auth"
	"myproject/modules/Purchase/controllers"

	"github.com/labstack/echo/v4"
)

var specPath = "/api/v1/users/:user_id/purchase/spec"
var purchasePath = "/api/v1/users/:user_id/purchase-order"
var approvalPath = "/api/v1/users/:user_id/purchase/approval"

func PurchaseOrderRoutes(e *echo.Echo) *echo.Echo {
	// Specification
	e.POST(specPath, controllers.CreateSpecification, auth.AdminMiddleware("..."))
	e.GET(specPath, controllers.ListAllSpecifications, auth.AdminMiddleware("..."))
	// Purchase Order
	e.POST(purchasePath, controllers.CreatePurchaseOrder, auth.AdminMiddleware("..."))
	e.GET(purchasePath, controllers.ListPurchaseOrders, auth.AdminMiddleware("..."))
	e.GET(purchasePath+"/:id", controllers.GetPurchaseOrderById, auth.AdminMiddleware("..."))
	e.PATCH(purchasePath+"/:id/update", controllers.UpdatePurchaseOrder, auth.AdminMiddleware("..."))
	e.DELETE(purchasePath+"/:id/delete", controllers.DeletePurchaseOrder, auth.AdminMiddleware("..."))
	return e
}
```

Because of this, **controllers must never depend on middleware having run.** A handler
always reads `:user_id` from the path and validates it against the database itself
(§6) — that way the same handler works with or without auth in front of it.

Do not leave routes commented out to "disable auth", and do not keep two versions of a
route line. One line per endpoint; add the middleware argument when it exists.

Rules: route strings are **only** built from the `var` paths + a suffix; never repeat
the full literal on each line. Group related lines with a one-line `//` comment.
Always `return e`.

A router file contains **no** `if`, no DB call, no `c.JSON` — only path variables and
route registrations.

### 5.4 `routers/routers.go` (module aggregator)

Nothing but calls:

```go
package routers

import "github.com/labstack/echo/v4"

func HumanResourceRoutes(e *echo.Echo) {
	HolidayRoutes(e)
	LeaveRoutes(e)
	WorkflowRoutes(e)
	OvertimeRoutes(e)
	JobApplicationRoutes(e)
}
```

One line per entity router in the module. Nothing else belongs in this file.

### 5.5 `routers/routes.go` (root aggregator)

CORS first, then every module aggregator. No route is ever declared here.

```go
package routers

import (
	commonRouters "myproject/common/routers"
	activitylog "myproject/modules/ActivityLog/routers"
	assets "myproject/modules/Assets/routers"
	purchase "myproject/modules/Purchase/routers"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// Define the routes
func InitRoutes(e *echo.Echo) {
	e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
		AllowOrigins: []string{"*"},
		AllowMethods: []string{"*"},
		AllowHeaders: []string{"*"},
	}))
	commonRouters.CommonRoutes(e)
	purchase.PurchaseRoutes(e)
	assets.AssetRoutes(e)
	activitylog.ActivityLogRoutes(e)
}
```

In the flat layout this same file is `routers/route.go` and it calls the entity
routers (`DesignationRoutes(e)`, `StaffRoutes(e)`, …) directly instead of module
aggregators.

### 5.6 `controllers/<entity>.go`

The controller is the only place with real logic. Fixed order:

```
1. package controllers
2. imports
3. package-level var / const        status maps, cached config, exported globals
4. request/input structs            everything the handlers bind into
5. unexported helpers               small pure funcs + tx helpers (no echo.Context)
6. exported handlers                Create → List → Get → Update → UpdateStatus → Delete → extras
```

Skeleton:

```go
package controllers

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	common "myproject/common/models"
	"myproject/config"
	"myproject/modules/Purchase/models"
)

// package-level state

var PurchaseStatuses = map[string]bool{
	"draft": true, "pending": true, "approved": true, "rejected": true,
}

// request structs

type PurchaseOrderInput struct {
	VendorID int                     `json:"vendor_id"`
	Items    []PurchaseOrderItemInput `json:"items"`
}

type PurchaseOrderItemInput struct {
	Description string  `json:"description"`
	Quantity    int     `json:"quantity"`
	UnitPrice   float64 `json:"unit_price"`
}

// helpers

func poNumberTaken(tx *gorm.DB, poNumber, excludeID string) (bool, error) { ... }

func buildPaymentTerms(poID string, in []PaymentTermInput) []models.PurchasePaymentTerm { ... }

// handlers

func CreatePurchaseOrder(c echo.Context) error { ... }
func ListPurchaseOrders(c echo.Context) error  { ... }
func GetPurchaseOrderById(c echo.Context) error { ... }
func UpdatePurchaseOrder(c echo.Context) error { ... }
func UpdatePurchaseOrderStatus(c echo.Context) error { ... }
func DeletePurchaseOrder(c echo.Context) error { ... }
```

**Large files (>1000 lines):** the same triad may repeat per feature block —
`structs → helpers → handlers` for specifications, then
`structs → helpers → handlers` for the purchase order itself, then for approval
config. Never interleave: a helper must never appear between two handlers of the same
block. Mark each block with a **one-line** comment naming it (`// Specification`,
`// Purchase Order`, `// Approval Config`) — nothing longer, no drawn separators.

### 5.6.1 `helper.go` — shared helpers of a module

A module usually has several controller files (`dashboard.go`, `expense.go`,
`purchase_order.go`, `specification.go` …), and some of them grow big helper functions
that **more than one of those files needs**. Those shared helpers do not get copied,
and they do not sit in whichever controller happened to need them first — they move
into a single `helper.go` inside the same `controllers` package.

```
modules/
└── Purchase/
    └── controllers/
        ├── purchase_order.go        # handlers + helpers used only here
        ├── specification.go         # handlers + helpers used only here
        └── helper.go                # helpers shared by BOTH files above
```

Because every file in the folder is `package controllers`, a func in `helper.go` is
called directly, with no import and no prefix:

```go
// modules/Purchase/controllers/helper.go
package controllers

import "time"

// Shared by purchase_order.go, specification.go and expense.go
func FormatHHMMSS(d time.Duration) string        { ... }
func ParseDuration(s string) int                 { ... }
func SecondsToDecimalHours(seconds int) float64  { ... }
func CombineDateAndTime(date, t time.Time) time.Time { ... }
func Ptr(s string) *string                       { return &s }
```

```go
// modules/Purchase/controllers/purchase_order.go
package controllers

func CreatePurchaseOrder(c echo.Context) error {
	...
	total := SecondsToDecimalHours(seconds)   // from helper.go, called directly
	...
}
```

**When a helper goes into `helper.go`:**

- two or more controller files in the module use it, **or**
- it is long enough that repeating it anywhere would be duplication, **or**
- it is a pure utility with no domain logic (time formatting, duration parsing,
  pointer helpers, number/string conversion).

**When a helper stays inside its own controller file:**

- only that one file uses it — small one- or two-use helpers are fine where they are;
  do not create a file for them. Keep them in the helper block above the handlers
  (§5.6).

Rules for `helper.go`:

- One file per module's controllers package — named exactly `helper.go`
  (never `utils.go`, `common.go`, `misc.go`).
- Helpers take plain values, never `echo.Context`, and never write a response.
- A helper that touches the DB inside a transaction takes `tx *gorm.DB` as its first
  parameter.
- If `helper.go` itself grows past a few hundred lines, split it by concern —
  `helper.go` + `helper_calculation.go` — not by controller.
- The same rule applies to `models/` and `routers/` if they ever need shared code,
  but in practice they should not.

### 5.7 `config/*.go`

Order: imports → `const` → package-level `var` singletons → template-data structs →
init/loader funcs → send/perform funcs.

```go
package config

import ( ... )

const (
	MailGunDomain = "..."
)

var (
	smtpHost = "smtp.gmail.com"
	smtpPort = "587"
)

type EmailTemplateData struct {
	Name  string
	Email string
	Year  int
}

func GetPasswordEmailTemplateFromFile(name, email, password string) (string, error) { ... }
func SendMailgunEmail(to, subject, htmlBody string) error { ... }
```

A `config` file exposes what the rest of the app needs as package-level variables
(`config.DB`, `config.ApiURL`) and keeps the wiring details private.

### 5.8 Formatting, comments and blank lines

Files must stay compact and must look identical on every machine. Three rules, applied
everywhere.

#### Indentation — tabs, never spaces

- **Indent with tabs.** Never use the space bar to line up code — the same file then
  renders with different widths on different editors and operating systems, and diffs
  fill up with whitespace-only changes.
- This is also what Go itself requires: `gofmt` indents with tabs. If your editor is
  inserting spaces, turn off "insert spaces instead of tabs" for `.go` files.
- Tab width is a personal editor setting (2, 4, 8 — your choice); because the file
  stores a tab, everyone sees their own preferred width and the bytes stay the same.
- Alignment inside a line (struct tags, `var` blocks, comment columns) is done by
  `gofmt` — run it and do not hand-align with spaces afterwards.
- Do not mix: a line indented with a tab followed by spaces is the worst case. Set the
  editor once and forget it.
- `.sql`, `.html` and every other source file in the repo follow the same rule; what
  matters most is that a single file never mixes both.
- **Every Go and SQL example in this document is already written with tabs** — copy
  them as they are and the formatting stays correct.

```
// Bad  →  ····func CreateHoliday(...)      (4 space characters)
// Good →  ⇥func CreateHoliday(...)         (one tab character)
```

Add this to `.editorconfig` at the repo root so nobody has to remember:

```ini
[*.{go,sql}]
indent_style = tab
trim_trailing_whitespace = true
insert_final_newline = true
```

#### Comments — only when they add something

- **Do not comment obvious code.** `// create the holiday` above `config.DB.Create(&holiday)`
  adds nothing. Delete it.
- A comment is written **only** when the reason is not visible in the code: a business
  rule, a non-obvious formula, a workaround, a unit, or a warning.
- Maximum **1–2 lines**. Never a paragraph, never a block of explanation above a
  function.
- No decorative separators of many lines, no `// ---- end of function ----`, no
  commented-out old code (delete it — git has it).
- No auto-generated boilerplate headers (author, date, description) at the top of a file.

```go
// Bad — a paragraph nobody reads, restating the code
/*
 * This function creates a new holiday. It first checks that the employee
 * exists, then binds the request body, then validates the fields, then
 * saves the record to the database and finally returns the response.
 */
func CreateHoliday(c echo.Context) error {
	// get the user id from the path
	employeeID := c.Param("user_id")
	// declare the variables
	var holiday models.Holiday
	...
}
```

```go
// Good — one short comment, only where the reason is not obvious
func CreateHoliday(c echo.Context) error {
	employeeID := c.Param("user_id")
	var holiday models.Holiday
	...
	// Day is derived, never accepted from the client
	holiday.Day = holiday.Date.Weekday().String()
	...
}
```

Short section markers inside a long controller are allowed and useful — one line only:

```go
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
| Between struct declarations | **1** |
| After `package x` | **1** |
| End of file | 1 newline, nothing more |

- Never two or more blank lines in a row, anywhere.
- No blank line right after `{` or right before `}`.
- No trailing spaces at the end of a line.
- Route registrations in a router file are written as consecutive lines; use at most
  one blank line to separate route groups, with a one-line comment naming the group.

```text
// Bad — blank rows scattered through the body, double blank line, padded braces
func ListHoliday(c echo.Context) error {

	employeeID := c.Param("user_id")

	var holiday []models.Holiday


	if result := config.DB.Where("id = ?", employeeID).First(&employee).Error; result != nil {

		return c.JSON(http.StatusBadRequest, echo.Map{"success": false, "error": "Not found"})

	}

}
```

```go
// Good
func ListHoliday(c echo.Context) error {
	employeeID := c.Param("user_id")
	var holiday []models.Holiday
	if result := config.DB.Where("id = ?", employeeID).First(&employee).Error; result != nil {
		return c.JSON(http.StatusBadRequest, echo.Map{"success": false, "error": "Not found"})
	}
	...
}
```

Run `gofmt` before every commit — it fixes indentation and alignment, but it does
**not** remove your extra blank lines or useless comments. That part is on you.

---

## 6. Handler body structure

Every handler follows the same top-to-bottom sequence. This is non-negotiable —
it is what makes any controller in any of our projects readable at a glance.

```
1. read path params                     c.Param("user_id"), c.Param("id")
2. read query params                    page, limit, search, filters
3. declare all vars                     (model structs, input struct, counters)
4. fixed values, conversions, defaults  strconv.Atoi, totalPages = 1, page/limit floors
5. resolve + validate the acting user   fetch employee/staff by user_id
6. fetch the target record              for Update/Delete/Get
7. c.Bind(&input)                       parse the body
8. field-level validation               required, trim, duplicate check, FK exists
9. DB operation                         Create / Save / Update / Delete (tx if multi-table)
10. activity log                        after success, before response
11. return c.JSON(...)                  the standard envelope
```

Steps 1–4 are the **input block**: everything the handler reads and everything with a
fixed or derived value is settled at the top, before a single database call or `if`
that can return. Nothing below the input block introduces a new variable out of thin
air, so a reader knows every value in play by the time the checks start.

Every failure returns immediately with `c.JSON(status, envelope)` — **no `panic`, no
bare `err` returns, no `echo.NewHTTPError` in controllers.**

### 6.1 Create

```go
func CreateHoliday(c echo.Context) error {
	employeeID := c.Param("user_id")
	var holiday models.Holiday
	var employee common.Employee
	if result := config.DB.Where("id = ?", employeeID).First(&employee).Error; result != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Not found, Please check the login",
		})
	}
	if result := c.Bind(&holiday); result != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid input",
		})
	}
	if holiday.Date.IsZero() || strings.TrimSpace(holiday.Holiday) == "" {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Date and Holiday fields are mandatory",
		})
	}
	holiday.Day = holiday.Date.Weekday().String()
	if result := config.DB.Create(&holiday).Error; result != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Failed to create holiday",
		})
	}
	staffID := uint(employee.ID)
	entityID := uint(holiday.ID)
	description := fmt.Sprintf("Added new holiday: %s", holiday.Holiday)
	_ = CreateActivityLog(&staffID, "create", "holiday", &entityID, description, "Success")
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"response": map[string]interface{}{
			"data": holiday,
		},
	})
}
```

Duplicate check before create, when the entity has a unique name:

```go
designation.Name = strings.TrimSpace(designation.Name)
result := config.DB.Where("LOWER(TRIM(name)) = LOWER(?)", designation.Name).First(&designation)
if result.RowsAffected > 0 {
	return c.JSON(http.StatusBadRequest, map[string]interface{}{
		"success": false,
		"error":   "Designation Already Exists",
	})
}
```

FK existence check before create:

```go
if designation.ReportsTo != nil {
	if err := config.DB.First(&parent, *designation.ReportsTo).Error; err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Parent Designation Not Found",
		})
	}
}
```

Default for a tri-state pointer:

```go
if designation.IsActive == nil {
	defaultValue := true
	designation.IsActive = &defaultValue
}
```

### 6.2 List — pagination + search + filter

The list handler always supports `page`, `limit`, `search`, plus entity-specific
filters. `page=0` or `limit=0` means "return everything".

Note the input block at the top: path param, then every query param, then the `var`
declarations, then the conversions and defaults (`userIDInt`, `totalPages = 1`, the
`page`/`limit` floors). Only after all of that does the first check that can return
appear. Never read a query param halfway down the handler.

```go
func ListDesignations(c echo.Context) error {
	userID := c.Param("user_id")
	page, _ := strconv.Atoi(c.QueryParam("page"))
	limit, _ := strconv.Atoi(c.QueryParam("limit"))
	search := c.QueryParam("search")
	isActiveParam := c.QueryParam("is_active")
	var staff models.Staff
	var designations []models.Designation
	var totalRoles int64
	var totalPages int64
	userIDInt, err := strconv.Atoi(userID)
	totalPages = 1
	if page <= 0 {
		page = 0
	}
	if limit <= 0 {
		limit = 0
	}
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Staff not found, please try again",
		})
	}
	if res := config.DB.Where("id = ?", userIDInt).First(&staff); res.Error != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Staff Not Found, Please check the login",
		})
	}
	query := config.DB.Model(&models.Designation{}).Preload("SubRoles").Order("id ASC")
	if search != "" {
		pattern := "%" + search + "%"
		query = query.Where(`(name ILIKE ? OR description ILIKE ?)`, pattern, pattern)
	}
	if isActiveParam != "" {
		query = query.Where("is_active = ?", isActiveParam == "true")
	}
	offset := (page - 1) * limit
	if limit == 0 || page == 0 {
		if result := query.Find(&designations).Error; result != nil {
			return c.JSON(http.StatusBadRequest, map[string]interface{}{
				"success": false,
				"error":   "No designations Found",
			})
		}
	} else {
		_ = query.Count(&totalRoles)
		totalPages = int64(int(totalRoles) / limit)
		if int(totalRoles)%limit != 0 {
			totalPages++
		}
		if result := query.Limit(limit).Offset(offset).Find(&designations).Error; result != nil {
			return c.JSON(http.StatusBadRequest, map[string]interface{}{
				"success": false,
				"error":   "Couldn't list the designations",
			})
		}
	}
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": map[string]interface{}{
			"page":        page,
			"limit":       limit,
			"total_pages": totalPages,
			"data":        designations,
		},
	})
}
```

### 6.3 Update — field-by-field diff with a change log

Update never blind-saves the bound struct. Each field is compared, validated, applied,
and appended to `changes` so the activity log records what actually changed.

```go
func UpdateDesignation(c echo.Context) error {
	userID := c.Param("user_id")
	idParam := c.Param("id")
	var staff models.Staff
	var designation, input models.Designation
	var changes []string
	userIDInt, err := strconv.Atoi(userID)
	id, idErr := strconv.Atoi(idParam)
	// ... err / idErr checks, resolve staff by userIDInt, load designation by id ...
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid input format",
		})
	}
	if strings.TrimSpace(input.Name) != "" && strings.TrimSpace(input.Name) != designation.Name {
		var count int64
		config.DB.Model(&models.Designation{}).
			Where("LOWER(TRIM(name)) = LOWER(?) AND id <> ?", strings.TrimSpace(input.Name), id).
			Count(&count)
		if count > 0 {
			return c.JSON(http.StatusBadRequest, map[string]interface{}{
				"success": false,
				"error":   "Designation already exists",
			})
		}
		oldName := designation.Name
		designation.Name = strings.TrimSpace(input.Name)
		changes = append(changes, fmt.Sprintf("Name changed from '%s' to '%s'", oldName, designation.Name))
	}
	if err := config.DB.Save(&designation).Error; err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Failed to Update Designation",
		})
	}
	description := fmt.Sprintf("Designation updated: %s", strings.Join(changes, "; "))
	desID := uint(designation.ID)
	CreateActivityLog(&staff.ID, "update", "designation", &desID, description)
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": "Designation Updated Successfully",
		"data":    designation,
	})
}
```

### 6.4 Status toggle

A status-only endpoint declares its tiny input struct **inside** the function (it is
used nowhere else):

```go
func UpdateDesignationStatus(c echo.Context) error {
	userID := c.Param("user_id")
	idParam := c.Param("id")
	type Status struct {
		IsActive bool `json:"status"`
	}
	var staff models.Staff
	var designation models.Designation
	var status Status
	userIDInt, err := strconv.Atoi(userID)
	id, idErr := strconv.Atoi(idParam)
	// ... err / idErr checks, resolve staff, load designation, bind status ...
	if result := config.DB.Model(&models.Designation{}).
		Where("id = ?", id).Update("is_active", status.IsActive).Error; result != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Failed to save Status",
		})
	}
	statusStr := "inactivated"
	if status.IsActive {
		statusStr = "activated"
	}
	desID := uint(designation.ID)
	CreateActivityLog(&staff.ID, "Update Active Status", "designation",
		&desID, fmt.Sprintf("Designation '%s' status %s", designation.Name, statusStr))
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": "Status updated Successfully",
	})
}
```

### 6.5 Delete — dependency guards first

Never delete before checking what depends on the record. The error message names the
blocking rows.

```go
func DeleteDesignation(c echo.Context) error {
	userID := c.Param("user_id")
	idParam := c.Param("id")
	var staff models.Staff
	var designation models.Designation
	var childDesignations []models.Designation
	userIDInt, err := strconv.Atoi(userID)
	id, idErr := strconv.Atoi(idParam)
	// ... err / idErr checks, resolve staff by userIDInt, load designation by id ...
	config.DB.Where("reports_to = ?", id).Find(&childDesignations)
	if len(childDesignations) > 0 {
		var names []string
		for _, d := range childDesignations {
			names = append(names, d.Name)
		}
		return c.JSON(http.StatusBadRequest, echo.Map{
			"success": false,
			"error":   fmt.Sprintf("Cannot delete: This designation is 'Reports To' for the following designations: %s", strings.Join(names, ", ")),
		})
	}
	if err := config.DB.Delete(&designation).Error; err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Failed to delete Designation",
		})
	}
	// ... activity log + success response
}
```

### 6.6 Transactions

Multi-table writes run in `config.DB.Transaction(...)`, and every helper that
participates takes `tx *gorm.DB` as its **first** parameter:

```go
func poNumberTaken(tx *gorm.DB, poNumber, excludeID string) (bool, error)
func seedRecurringReceivedInvoice(tx *gorm.DB, po models.PurchaseOrder) (string, error)
func emitPurchaseExpenses(tx *gorm.DB, po models.PurchaseOrder) error
```

```go
err := config.DB.Transaction(func(tx *gorm.DB) error {
	if err := tx.Create(&po).Error; err != nil {
		return err
	}
	if err := emitPurchaseExpenses(tx, po); err != nil {
		return err
	}
	return nil
})
```

Inside a transaction always use `tx`, never `config.DB` — mixing the two silently
writes outside the transaction and breaks the rollback.

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
| Validation failed, bind failed, business rule rejected, DB write failed | `400 Bad Request` | the default for almost everything |
| The addressed record does not exist | `404 Not Found` | `GET/PATCH/DELETE /:id` on a missing row |
| Token missing / invalid / expired | `401 Unauthorized` | raised by middleware, not controllers |
| Caller is known but not allowed to do this | `403 Forbidden` | ownership or access rejection |
| Duplicate record, or state conflict (already approved, already paid) | `409 Conflict` | uniqueness and state-machine violations |
| Body parsed fine but the values are semantically wrong | `422 Unprocessable Entity` | optional, when 400 is too vague |
| Any success, including create and delete | `200 OK` | we do not use 201/204 |

```go
// Bad
if err := config.DB.Create(&po).Error; err != nil {
	return c.JSON(http.StatusInternalServerError, map[string]interface{}{
		"success": false,
		"error":   err.Error(),
	})
}
```

```go
// Good
if err := config.DB.Create(&po).Error; err != nil {
	log.Println("create purchase order:", err)
	return c.JSON(http.StatusBadRequest, map[string]interface{}{
		"success": false,
		"error":   "Failed to create the purchase order, please try again",
	})
}
```

If a query genuinely cannot be classified (a raw SQL scan blew up), still return `400`
with a clean message and log the detail — the client cannot act on a 500 either way.

### 6.8 Reading input — query params, JSON body and form-data

There are exactly three ways a request carries data. Use the one that matches the
content type, and never mix two of them in the same endpoint.

#### 1. Path parameters — identity only

```go
userID := c.Param("user_id")
poID := c.Param("id")
```

Path params carry **who** and **which record**, nothing else. They are always
validated before use (`strconv.Atoi`, then a DB lookup).

#### 2. Query parameters — list controls and filters (`GET` only)

Query params are used for pagination, search, filtering and sorting. Every one of them
is optional and every one has a defined default.

```go
page, _ := strconv.Atoi(c.QueryParam("page"))
limit, _ := strconv.Atoi(c.QueryParam("limit"))
search := c.QueryParam("search")
status := c.QueryParam("status")
fromDate := c.QueryParam("from_date")
```

```
GET /api/v1/users/12/purchase-order?page=2&limit=20&search=cable&status=approved
```

Rules:
- Names are `snake_case` and identical across every module: `page`, `limit`, `search`,
  `from_date`, `to_date`, `status`, `is_active`, `sort`, `order`.
- Ignore an unrecognised or empty param — never fail the request because of it.
- Never send a body with `GET`; never accept a filter through the body.

#### 3. Request body

**a) Plain JSON — the default for `POST` / `PATCH`.**
Content-Type `application/json`, bound into a struct with `c.Bind`:

```go
type PurchaseOrderInput struct {
	VendorID int                      `json:"vendor_id"`
	Items    []PurchaseOrderItemInput `json:"items"`
}

var input PurchaseOrderInput
if err := c.Bind(&input); err != nil {
	return c.JSON(http.StatusBadRequest, map[string]interface{}{
		"success": false,
		"error":   "Invalid input",
	})
}
```

```json
{
  "vendor_id": 8,
  "items": [ { "description": "Cable", "quantity": 10, "unit_price": 45.5 } ]
}
```

**b) Multipart form-data — only when files are uploaded.**
The JSON payload is sent as one text field named `data`, and the binaries come in
named file fields. Never spread the record's fields across dozens of form keys.

```
Content-Type: multipart/form-data

data    = {"vendor_id":8,"title":"Annual contract","items":[...]}   ← one JSON string
files   = contract.pdf
files   = annexure.pdf
images  = site_photo.jpg
```

```go
func CreatePurchaseOrder(c echo.Context) error {
	userID := c.Param("user_id")
	var input PurchaseOrderInput
	var employee common.Employee
	if err := config.DB.Where("id = ?", userID).First(&employee).Error; err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Not found, Please check the login",
		})
	}
	if err := json.Unmarshal([]byte(c.FormValue("data")), &input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid input",
		})
	}
	form, err := c.MultipartForm()
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid file upload",
		})
	}
	files := form.File["files"]
	images := form.File["images"]
	...
}
```

Rules for form-data:
- The JSON part is **always** the field named `data` — same name in every endpoint.
- Documents go in `files`, pictures go in `images`; repeat the key for multiple
  uploads. Do not invent `file1`, `file2`, `attachment_a`.
- Validate every upload before saving: extension, MIME type and size. Reject with
  `400` and a message naming the limit.
- **Never use `file.Filename` as-is.** Always pass it through
  `config.SanitizeFileName(...)` before it becomes part of a storage key or a path —
  a browser filename can carry spaces, `/`, `#`, `?` and `..` (§11.2).
- Store the saved paths/URLs on the record; the response returns the URLs, never the
  bytes.
- An endpoint that has no upload must not be multipart — send plain JSON.

Whatever the input format, the **response format never changes** — it is always the
envelope in §7.

### 6.9 Fast queries — pagination, filters and joins

List endpoints are where a backend gets slow. The rules below are mandatory for every
`List` handler.

**Always paginate at the database.** Never load everything and slice it in Go:

```go
// Bad — pulls the whole table into memory
config.DB.Find(&orders)
paged := orders[offset : offset+limit]
```

```go
// Good — the database does the work
query.Limit(limit).Offset(offset).Find(&orders)
```

**Count with the same filters, on the same query, before applying limit/offset** — the
`total_pages` in the response must match what the filters actually return:

```go
query := config.DB.Model(&models.PurchaseOrder{})
if search != "" {
	pattern := "%" + search + "%"
	query = query.Where("(po_number ILIKE ? OR title ILIKE ?)", pattern, pattern)
}
if status != "" {
	query = query.Where("status = ?", status)
}
var total int64
query.Count(&total)
query.Limit(limit).Offset(offset).Find(&orders)
```

**Build filters conditionally, never as one giant `WHERE`.** Each `if` adds a clause
only when the param was sent, so the database can still use its indexes.

**Search:**
- `ILIKE` with `%term%` for case-insensitive matching on a few named columns only —
  never on every column of the table.
- Trim the term and skip the clause when it is empty.
- Search on indexed columns; a wildcard on both sides cannot use a normal index, so
  keep the searched column list short and add a trigram/`GIN` index if a table gets big.

**Joins and preloads — the main cause of slow lists:**

| Do not | Do instead |
|---|---|
| `Preload` five relations on a list endpoint | preload only what the list actually displays; load the rest in the detail endpoint |
| Nested preloads (`Preload("A.B.C")`) on a list | fetch the child rows in one extra query keyed by the parent IDs |
| Query inside a `for` loop (the N+1 problem) | one `WHERE parent_id IN (?)` query, then map the results in Go |
| `Joins` on several big tables just to show two columns | `Select` only the needed columns, or a small raw query returning a flat struct |
| `SELECT *` on a wide table | `Select("id, po_number, status, total")` |

```go
// Bad — N+1: one query per order
for _, o := range orders {
	config.DB.Where("purchase_order_id = ?", o.ID).Find(&o.Items)
}
```

```go
// Good — two queries in total
var items []models.PurchaseOrderItem
config.DB.Where("purchase_order_id IN ?", orderIDs).Find(&items)
itemsByOrder := map[string][]models.PurchaseOrderItem{}
for _, it := range items {
	itemsByOrder[it.PurchaseOrderID] = append(itemsByOrder[it.PurchaseOrderID], it)
}
```

More rules:
- **Filter in SQL, never in Go.** No `for` loop that skips rows after `Find` — that
  row should not have been fetched.
- **Sort in SQL** with an explicit `Order("id ASC")`; without it Postgres may return
  rows in a different order on every page and records will repeat or disappear.
- **Aggregate in SQL** (`COUNT`, `SUM`, `AVG`) — never sum a slice in Go that the
  database could have summed.
- **Index every column used in `WHERE`, `JOIN` or `ORDER BY`** — add the index in the
  migration that creates the table.
- Cap `limit` at a sane maximum (e.g. 100) so one caller cannot ask for the whole table.
- A dashboard or report that needs many aggregates uses **one raw query returning a
  flat result struct**, not several ORM round-trips.

---

## 7. Response envelope

Every endpoint returns a JSON object with a boolean `success`. Nothing is ever
returned bare (no top-level arrays, no plain strings).

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

**List with pagination:**
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
- Never return a bare array, a bare string, an empty body, or a raw Go error.
- An empty list is a success: `"data": []` with `200`, never `404`.
- Never return `500` (§6.7).
- Response maps are written as `map[string]interface{}{...}`; `echo.Map{...}` is
  acceptable and equivalent — do not mix both inside one file.
- Field names in JSON are `snake_case`.
- Never return password hashes, tokens, or internal columns; if a model holds one, set
  it to empty before responding.

---

## 8. Model conventions

```go
type Designation struct {
	ID          uint           `json:"id" gorm:"primaryKey"`
	Name        string         `json:"name" gorm:"unique"`
	Description string         `json:"description"`
	IsActive    *bool          `json:"status"`
	ReportsTo   *uint          `json:"reports_to" gorm:"null"`
	SubRoles    []*Designation `json:"children" gorm:"foreignKey:ReportsTo"`
}
```

Rules:

- **Tag order is always `json` then `gorm`.** Fields are aligned in a column.
- **No methods on models.** No `Validate()`, no `BeforeSave` business rules, no DB calls.
- **Pointers for nullable / tri-state.** `*bool` when "unset" differs from `false`,
  `*uint` / `*int` for nullable FKs, `*time.Time` for optional dates.
- **Relations:**
  ```go
  Vendor      Vendor        `json:"vendor" gorm:"foreignKey:VendorID"`         // belongs-to
  Items       []Item        `json:"items" gorm:"foreignKey:PurchaseOrderID"`   // has-many
  Employees   []models.Employee `json:"employees" gorm:"many2many:lead_employees;joinForeignKey:LeadID;JoinReferences:EmployeeID"`
  EmployeeIDs []int         `json:"reports_to" gorm:"-"`                       // input-only, not a column
  ```
  `gorm:"-"` marks request-only fields (lists of IDs the client sends) that the
  handler expands into real relations.
- **ID strategy:**
  - integer surrogate key → `ID uint \`json:"id" gorm:"primaryKey"\`` backed by `SERIAL`.
  - human-readable business key → string ID with a DB-side default:
    ```go
	ID string `json:"id" gorm:"default:('LEAD-' || EXTRACT(YEAR FROM CURRENT_DATE)::text || '-' || LPAD(nextval('lead_seq')::text, 3, '0'))"`
    ```
    Use this style for identifiers the user reads and quotes, such as `PO-2026-001`.
- **Cross-package models:** import the shared package with an alias and reference it:
  ```go
  import common "myproject/common/models"
  ...
  Employees []common.Employee `json:"employees"`
  ```
- Struct order inside the file: parent entity first, then child entities, then
  join/lookup structs.

---

## 9. Routing conventions

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

### 9.2 Verb table

| Action | Method + path suffix | Handler name |
|---|---|---|
| Create | `POST` `""` | `CreateX` |
| List | `GET` `""` | `ListXs` / `ListAllXs` |
| Filtered list | `GET` `"/filter"` | `XFilterList` |
| Get one | `GET` `"/:id"` | `GetXById` |
| Update | `PATCH` `"/:id/update"` | `UpdateX` |
| Toggle active | `PATCH` `"/:id/is_active"` | `UpdateXStatus` |
| Change status | `PATCH` `"/:id/status"` | `UpdateXStatus` |
| Delete | `DELETE` `"/:id/delete"` | `DeleteX` |
| Custom action | `POST` `"/:id/<verb>"` | `XVerb` (e.g. `PurchaseOrderApproval`) |

`PUT` is not used. Deletes are explicit (`/delete`) so they can't be hit accidentally.

### 9.3 Middleware placement

Middleware is **optional at the start and appended last when it exists.**

Before auth is set up — while the endpoints are being built and tested — the route is
just path + handler:

```go
e.POST(purchasePath, controllers.CreatePurchaseOrder)
e.GET(purchasePath, controllers.ListPurchaseOrders)
e.GET(purchasePath+"/:id", controllers.GetPurchaseOrderById)
```

Once auth exists, the middleware becomes the **last argument** of the same line:

```go
e.POST(purchasePath, controllers.CreatePurchaseOrder, auth.AdminMiddleware("..."))
e.GET(purchasePath, controllers.ListPurchaseOrders, auth.AdminMiddleware("..."))
e.GET(purchasePath+"/:id", controllers.GetPurchaseOrderById, auth.AdminMiddleware("..."))
```

Nothing else moves — same path variables, same handler names, same order. Adding auth
to a module is a one-argument change per line plus the `auth` import.

Middleware functions live in `auth/auth.go`. Because they may not be in place yet, a
handler never assumes the request was already checked: it reads `:user_id` and
validates it itself (§6).

### 9.4 Wiring levels

```
main.go
 └── routers.InitRoutes(e)                    root: CORS + aggregators
      ├── commonRouters.CommonRoutes(e)       common: calls each common XRoutes(e)
      └── <module>.<Module>Routes(e)          module: calls each module XRoutes(e)
           └── XRoutes(e)                     entity: the actual e.POST/GET/... lines
```

Adding a new entity touches exactly one aggregator line.

---

## 10. Migrations

Migrations are plain SQL, applied by `rubenv/sql-migrate` from `config.InitDB()`.
GORM `AutoMigrate` is **not** used — the SQL files are the schema source of truth.

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

### 10.2 File templates

Every migration file has exactly two markers: `-- +migrate Up` and `-- +migrate Down`.
Nothing else — no `BEGIN`/`COMMIT` (the tool wraps each file in its own transaction),
no `\c`, no psql meta-commands.

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
| Column names | singular, `snake_case`, matching the model's `json` tag |
| Index name | `idx_<table>_<column>` |
| Constraint name | `chk_<table>_<column>` / `uq_<table>_<columns>` |

Every `Up` must have a matching `Down` that reverses it, dropping children first.

**Index every column used in a `WHERE`, `JOIN` or `ORDER BY`** — every foreign key,
every status column, every column the list endpoint filters or sorts on. Add them in
the migration that creates the table, not months later when the list is already slow
(§6.9).

### 10.4 Rules

- **Never edit a migration that has already been applied** anywhere. Write a new
  `alter_` file instead.
- Never renumber existing files.
- The Go model and the SQL must agree; if you add a column, add the struct field in
  the same commit.

### 10.5 How they run

`config.InitDB()` opens GORM, takes the raw `*sql.DB`, and executes the folder:

```go
migrations := &migrate.FileMigrationSource{Dir: migrationsDir}
n, err := migrate.Exec(sqlDB, "postgres", migrations, migrate.Up)
if err != nil {
	log.Fatalf("❌ Migration failed: %s", err.Error())
}
fmt.Printf("✅ Applied %d migrations\n", n)
```

For local runs `migrationsDir` must resolve to the repo folder (`"./migrations"`),
not an absolute container path. Keep it env-driven so nobody has to edit code:

```go
migrationsDir := os.Getenv("MIGRATIONS_DIR")
if migrationsDir == "" {
	migrationsDir = "./migrations"
}
```

---

## 11. `config/` package

One file per external concern. Everything the app needs from the outside world is
initialised here and exposed as a package-level variable.

| File | Required? | Responsibility |
|---|---|---|
| `database.go` | **always** | `InitDB()`, exported `DB *gorm.DB` (and a second handle if a second database exists), migration execution |
| `email.go` | only if the project sends email | SMTP sender, template parsing, one `SendXEmail` per email type |
| `regex.go` | only if there is shared validation | validation regex constants |
| `storage.go` | only if the project uploads files | object-storage upload/delete (S3-compatible bucket) |
| `storage_b2.go` | only if that bucket API is used | object-storage upload/delete (Backblaze B2 style API) |
| `<vendor>_client.go` | only per integration actually used | one file per other third-party API client |
| `ws_notification.go` | only if the project uses websockets | websocket notification config |

**Only `database.go` is mandatory.** Everything else in this section is optional — add
the file when the project actually needs that capability, and leave it out otherwise.
A project with no uploads has no `storage.go`; a project that never sends mail has no
`email.go`; a project using one bucket provider does not carry the other one's file.
Do not copy files "just in case" — an unused config file still needs env variables,
still gets read during review, and still rots.

What is fixed is the **shape**: when the project does need one of these, it is written
as the version below rather than a new invention each time. Copy it and change only
the environment values (keys, URLs, bucket, sender address). The same applies to
capabilities not listed here — a payment gateway, an SMS sender, a PDF service each
get their own `config/<concern>.go` following the same pattern.

**Credentials are read from `.env`, never written in the code.** Hardcoded keys end up
in git history and cannot be rotated. Every constant below comes from `os.Getenv`, and
`.env` only carries the variables the project actually uses.

### 11.1 `config/database.go` — required

```go
package config

import (
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	migrate "github.com/rubenv/sql-migrate"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var (
	DB     *gorm.DB
	ApiURL string
)

func InitDB() {
	if err := godotenv.Load(".env"); err != nil {
		fmt.Println("Error loading .env:", err)
	}
	dbHost := os.Getenv("DB_HOST")
	dbPort := os.Getenv("DB_PORT")
	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbName := os.Getenv("DB_NAME")
	sslMode := os.Getenv("SSL_MODE")
	ApiURL = os.Getenv("FRONTEND_URL")
	if dbHost == "" || dbPort == "" || dbUser == "" || dbPassword == "" || dbName == "" || sslMode == "" {
		log.Fatal("Missing required environment variables for database connection")
	}
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		dbHost, dbPort, dbUser, dbPassword, dbName, sslMode)
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("❌ Unable to connect to the database: %s", err.Error())
	}
	fmt.Println("✅ Successfully connected to the database")
	DB = db
	RunMigrations()
}

func RunMigrations() {
	sqlDB, err := DB.DB()
	if err != nil {
		log.Fatalf("❌ Failed to get raw database connection: %s", err.Error())
	}
	dir := os.Getenv("MIGRATIONS_DIR")
	if dir == "" {
		dir = "./migrations"
	}
	migrations := &migrate.FileMigrationSource{Dir: dir}
	n, err := migrate.Exec(sqlDB, "postgres", migrations, migrate.Up)
	if err != nil {
		log.Fatalf("❌ Migration failed: %s", err.Error())
	}
	fmt.Printf("✅ Applied %d migrations\n", n)
}
```

Keep: fail fast with `log.Fatal` on missing config, print ✅/❌ status lines, expose
the handle as `config.DB`. Controllers never open their own connection.

A project with a second database repeats the block in the same file as
`InitSecondDB()` with its own `SECOND_DB_*` variables, its own exported handle and its
own migrations folder.

### 11.2 `config/storage.go` — optional, S3-compatible object storage

Upload and delete against an S3-compatible bucket, signed with AWS Signature V4. Only
the four env values change between projects.

```go
package config

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"
)

var (
	storageRegion    = os.Getenv("STORAGE_REGION")
	storageBucket    = os.Getenv("STORAGE_BUCKET")
	storageAccessKey = os.Getenv("STORAGE_ACCESS_KEY")
	storageSecretKey = os.Getenv("STORAGE_SECRET_KEY")
	storageEndpoint  = os.Getenv("STORAGE_ENDPOINT") // e.g. <region>.example-objects.com
)

// SanitizeFileName strips characters that break object keys and URLs.
func SanitizeFileName(name string) string {
	name = strings.NewReplacer(" ", "_", "\n", "_", "\t", "_", "\r", "_").Replace(name)
	name = regexp.MustCompile(`[<>:"/\\|?*#&%$@!+=\[\]{}(),]`).ReplaceAllString(name, "_")
	name = regexp.MustCompile(`_+`).ReplaceAllString(name, "_")
	return strings.Trim(name, "._")
}

func hmacSHA256(key []byte, data string) []byte {
	h := hmac.New(sha256.New, key)
	h.Write([]byte(data))
	return h.Sum(nil)
}

func storageHost() string {
	return fmt.Sprintf("%s.%s", storageBucket, storageEndpoint)
}

// signV4 returns the Authorization header value for one request.
func signV4(method, canonicalURI, payloadHash, amzDate, dateStamp, canonicalHeaders, signedHeaders string) string {
	canonicalRequest := fmt.Sprintf("%s\n%s\n%s\n%s\n%s\n%s",
		method, canonicalURI, "", canonicalHeaders, signedHeaders, payloadHash)
	credentialScope := fmt.Sprintf("%s/%s/s3/aws4_request", dateStamp, storageRegion)
	stringToSign := fmt.Sprintf("AWS4-HMAC-SHA256\n%s\n%s\n%x",
		amzDate, credentialScope, sha256.Sum256([]byte(canonicalRequest)))
	kDate := hmacSHA256([]byte("AWS4"+storageSecretKey), dateStamp)
	kRegion := hmacSHA256(kDate, storageRegion)
	kService := hmacSHA256(kRegion, "s3")
	kSigning := hmacSHA256(kService, "aws4_request")
	signature := hex.EncodeToString(hmacSHA256(kSigning, stringToSign))
	return fmt.Sprintf("AWS4-HMAC-SHA256 Credential=%s/%s, SignedHeaders=%s, Signature=%s",
		storageAccessKey, credentialScope, signedHeaders, signature)
}

// UploadFile stores the file at path (e.g. "purchase-order/PO-2026-001/quote.pdf")
// and returns its public URL.
func UploadFile(file *multipart.FileHeader, path string) (string, error) {
	if path == "" {
		path = SanitizeFileName(file.Filename)
	}
	path = strings.TrimPrefix(path, "/")
	src, err := file.Open()
	if err != nil {
		return "", err
	}
	defer src.Close()
	buffer := bytes.NewBuffer(nil)
	if _, err := io.Copy(buffer, src); err != nil {
		return "", err
	}
	host := storageHost()
	contentType := "application/octet-stream"
	t := time.Now().UTC()
	amzDate := t.Format("20060102T150405Z")
	dateStamp := t.Format("20060102")
	canonicalURI := "/" + path
	payloadHash := fmt.Sprintf("%x", sha256.Sum256(buffer.Bytes()))
	canonicalHeaders := fmt.Sprintf("content-type:%s\nhost:%s\nx-amz-content-sha256:%s\nx-amz-date:%s\n",
		contentType, host, payloadHash, amzDate)
	signedHeaders := "content-type;host;x-amz-content-sha256;x-amz-date"
	authorization := signV4("PUT", canonicalURI, payloadHash, amzDate, dateStamp, canonicalHeaders, signedHeaders)
	req, err := http.NewRequest("PUT", "https://"+host+canonicalURI, bytes.NewReader(buffer.Bytes()))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", contentType)
	req.Header.Set("Host", host)
	req.Header.Set("X-Amz-Content-Sha256", payloadHash)
	req.Header.Set("X-Amz-Date", amzDate)
	req.Header.Set("Authorization", authorization)
	req.Header.Set("Content-Length", strconv.Itoa(buffer.Len()))
	req.Header.Set("x-amz-acl", "public-read")
	resp, err := (&http.Client{}).Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("upload failed (%d): %s", resp.StatusCode, string(body))
	}
	return fmt.Sprintf("https://%s/%s", host, path), nil
}

func RemoveFile(fileURL string) error {
	u, err := url.Parse(fileURL)
	if err != nil {
		return err
	}
	path := strings.TrimPrefix(u.Path, "/")
	host := storageHost()
	t := time.Now().UTC()
	amzDate := t.Format("20060102T150405Z")
	dateStamp := t.Format("20060102")
	canonicalURI := "/" + path
	payloadHash := fmt.Sprintf("%x", sha256.Sum256([]byte("")))
	canonicalHeaders := fmt.Sprintf("host:%s\nx-amz-content-sha256:%s\nx-amz-date:%s\n",
		host, payloadHash, amzDate)
	signedHeaders := "host;x-amz-content-sha256;x-amz-date"
	authorization := signV4("DELETE", canonicalURI, payloadHash, amzDate, dateStamp, canonicalHeaders, signedHeaders)
	req, err := http.NewRequest("DELETE", "https://"+host+canonicalURI, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Host", host)
	req.Header.Set("X-Amz-Content-Sha256", payloadHash)
	req.Header.Set("X-Amz-Date", amzDate)
	req.Header.Set("Authorization", authorization)
	resp, err := (&http.Client{}).Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusNoContent && resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("delete failed (%d): %s", resp.StatusCode, string(body))
	}
	return nil
}

// BytesToFileHeader wraps generated bytes (a PDF, a QR image) as an upload so they
// can go through UploadFile without touching disk.
func BytesToFileHeader(data []byte, filename string) (*multipart.FileHeader, error) {
	var buf bytes.Buffer
	w := multipart.NewWriter(&buf)
	fw, err := w.CreateFormFile("file", filename)
	if err != nil {
		return nil, err
	}
	if _, err := fw.Write(data); err != nil {
		return nil, err
	}
	w.Close()
	form, err := multipart.NewReader(&buf, w.Boundary()).ReadForm(int64(len(data)) * 2)
	if err != nil {
		return nil, err
	}
	files := form.File["file"]
	if len(files) == 0 {
		return nil, fmt.Errorf("no file part found")
	}
	return files[0], nil
}
```

Calling it from a controller:

```go
url, err := config.UploadFile(fileHeader, fmt.Sprintf("purchase-order/%s/%s", po.ID, config.SanitizeFileName(fileHeader.Filename)))
if err != nil {
	return c.JSON(http.StatusBadRequest, map[string]interface{}{
		"success": false,
		"error":   "Failed to upload the file, please try again",
	})
}
po.QuoteURL = url
```

Rules: the object key always starts with the entity and its id
(`invoice/INV-2026-014/scan.pdf`) so the bucket stays browsable; the database stores
the returned URL, never the bytes; deleting a record deletes its objects.

#### `SanitizeFileName` — always run it on a user-supplied name

A filename that came from a browser can contain spaces, slashes, quotes, `#`, `?`,
`&`, newlines and non-ASCII characters. Used raw, it silently breaks things: `/`
creates unintended folders in the bucket, `#` and `?` truncate the URL when the file
is downloaded, spaces produce links that break in emails, and `..` can escape the
intended prefix. `SanitizeFileName` replaces every unsafe character with `_`, collapses
repeated `_`, and trims leading/trailing `.` and `_`.

```go
// config/storage.go
func SanitizeFileName(name string) string {
	name = strings.NewReplacer(" ", "_", "\n", "_", "\t", "_", "\r", "_").Replace(name)
	name = regexp.MustCompile(`[<>:"/\\|?*#&%$@!+=\[\]{}(),]`).ReplaceAllString(name, "_")
	name = regexp.MustCompile(`_+`).ReplaceAllString(name, "_")
	return strings.Trim(name, "._")
}
```

| Incoming filename | After `SanitizeFileName` |
|---|---|
| `Quote #12 (final).pdf` | `Quote_12_final.pdf` |
| `../../etc/passwd` | `etc_passwd` |
| `site photo 2026.jpg` | `site_photo_2026.jpg` |
| `report&summary%.xlsx` | `report_summary.xlsx` |

**Where it must be called:**

- On **every** `file.Filename` before it becomes part of an object key — this is the
  only rule that matters, and `UploadFile` already applies it when `path` is empty.
- When you build the key yourself, sanitise the filename part but **not** the prefix
  you control (`purchase-order/PO-2026-001/`), since the prefix legitimately contains
  slashes.
- On a generated name too, whenever any part of it comes from user data:
  `SanitizeFileName(vendor.Name + "_agreement.pdf")`.
- On any name written to the local disk or put into a `Content-Disposition` header.

```go
// Uploading several files from one multipart request (§6.8)
for _, fh := range form.File["files"] {
	key := fmt.Sprintf("purchase-order/%s/%s", po.ID, config.SanitizeFileName(fh.Filename))
	url, err := config.UploadFile(fh, key)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Failed to upload " + fh.Filename,
		})
	}
	attachments = append(attachments, models.PurchaseOrderFile{PurchaseOrderID: po.ID, URL: url})
}
```

Keep the original filename in the database if the user needs to see it — sanitise the
**key**, and store `fh.Filename` in a `file_name` column for display.

Do not write a second copy of this function anywhere. It lives in `config/storage.go`
and every module calls `config.SanitizeFileName(...)`.

### 11.3 `config/storage_b2.go` — optional, Backblaze-B2-style storage

Some projects use a bucket API that authorises first, then asks for an upload URL.
Same two exported functions, different transport.

```go
package config

import (
	"bytes"
	"crypto/sha1"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"strconv"
	"strings"
)

var (
	b2AuthURL    = os.Getenv("B2_AUTH_URL") // https://api.backblazeb2.com/b2api/v2/b2_authorize_account
	b2KeyID      = os.Getenv("B2_KEY_ID")
	b2AppKey     = os.Getenv("B2_APP_KEY")
	b2BucketID   = os.Getenv("B2_BUCKET_ID")
	b2BucketName = os.Getenv("B2_BUCKET_NAME")
)

type b2Auth struct {
	AuthorizationToken string `json:"authorizationToken"`
	APIURL             string `json:"apiUrl"`
	DownloadURL        string `json:"downloadUrl"`
}

type b2UploadURL struct {
	UploadURL          string `json:"uploadUrl"`
	AuthorizationToken string `json:"authorizationToken"`
}

func b2Authorize() (b2Auth, error) {
	var auth b2Auth
	req, err := http.NewRequest("GET", b2AuthURL, nil)
	if err != nil {
		return auth, err
	}
	req.SetBasicAuth(b2KeyID, b2AppKey)
	resp, err := (&http.Client{}).Do(req)
	if err != nil {
		return auth, err
	}
	defer resp.Body.Close()
	err = json.NewDecoder(resp.Body).Decode(&auth)
	return auth, err
}

func UploadFileB2(file *multipart.FileHeader, path string) (string, error) {
	auth, err := b2Authorize()
	if err != nil {
		return "", err
	}
	body := fmt.Sprintf(`{"bucketId":"%s"}`, b2BucketID)
	req, err := http.NewRequest("POST", auth.APIURL+"/b2api/v2/b2_get_upload_url", bytes.NewBufferString(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", auth.AuthorizationToken)
	req.Header.Set("Content-Type", "application/json")
	resp, err := (&http.Client{}).Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	var upload b2UploadURL
	if err := json.NewDecoder(resp.Body).Decode(&upload); err != nil {
		return "", err
	}
	src, err := file.Open()
	if err != nil {
		return "", err
	}
	defer src.Close()
	buffer := bytes.NewBuffer(nil)
	if _, err := io.Copy(buffer, src); err != nil {
		return "", err
	}
	sum := sha1.Sum(buffer.Bytes())
	path = strings.TrimPrefix(path, "/")
	req, err = http.NewRequest("POST", upload.UploadURL, buffer)
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", upload.AuthorizationToken)
	req.Header.Set("X-Bz-File-Name", path)
	req.Header.Set("Content-Type", "application/octet-stream")
	req.Header.Set("X-Bz-Content-Sha1", fmt.Sprintf("%x", sum))
	req.Header.Set("Content-Length", strconv.Itoa(buffer.Len()))
	resp, err = (&http.Client{}).Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("upload failed (%d): %s", resp.StatusCode, string(body))
	}
	return fmt.Sprintf("%s/file/%s/%s", auth.DownloadURL, b2BucketName, path), nil
}
```

`RemoveFileB2` follows the same three steps — authorise, look up the file version with
`b2_list_file_versions`, then `b2_delete_file_version`.

### 11.4 `config/email.go` — optional

One private `Email` struct that renders a template, then one exported
`SendXEmail(...)` per email type. Adding an email means adding a `case`, not a new
transport.

```go
package config

import (
	"bytes"
	"fmt"
	"html/template"
	"log"
	"net/smtp"
	"os"

	common "myproject/common/models"
)

var (
	smtpHost     = os.Getenv("SMTP_HOST")
	smtpPort     = os.Getenv("SMTP_PORT")
	smtpUser     = os.Getenv("SMTP_USER")
	smtpPassword = os.Getenv("SMTP_PASSWORD")
	sender       = os.Getenv("MAIL_SENDER") // noreply@example.com
	from         = os.Getenv("MAIL_FROM")   // Example App <noreply@example.com>
)

type Email struct {
	data    map[string]string
	subject string
	body    string
	tmpl    string
}

func (e *Email) parse() error {
	tmpl, err := template.ParseFiles(e.tmpl)
	if err != nil {
		return err
	}
	b := new(bytes.Buffer)
	if err := tmpl.Execute(b, e.data); err != nil {
		return err
	}
	e.body = b.String()
	return nil
}

func (e *Email) send(to string) error {
	msg := fmt.Sprintf(
		"From: %s\r\nTo: %s\r\nSubject: %s\r\nMIME-version: 1.0;\r\nContent-Type: text/html; charset=\"UTF-8\";\r\n\r\n%s",
		from, to, e.subject, e.body,
	)
	addr := fmt.Sprintf("%s:%s", smtpHost, smtpPort)
	auth := smtp.PlainAuth("", smtpUser, smtpPassword, smtpHost)
	if err := smtp.SendMail(addr, auth, sender, []string{to}, []byte(msg)); err != nil {
		log.Printf("failed to send %q to %s: %v", e.subject, to, err)
		return err
	}
	log.Printf("email %q sent to %s", e.subject, to)
	return nil
}

func SendEmployeeEmail(employee *common.Employee, emailType string) error {
	e := &Email{data: map[string]string{
		"Username": employee.Name,
		"Link":     fmt.Sprintf("%s/reset-password?token=%s", ApiURL, employee.Token),
	}}
	switch emailType {
	case "forgot_password":
		e.tmpl = "templates/forgot_password.html"
		e.subject = "Reset Your Password"
	case "user_created":
		e.tmpl = "templates/new_user_created.html"
		e.subject = "Welcome! Please Set Your Password"
	default:
		return fmt.Errorf("invalid email type")
	}
	if err := e.parse(); err != nil {
		return err
	}
	return e.send(employee.Email)
}
```

Rules: templates are referenced by path, never inlined as strings in Go; the sending
function returns `error` and the controller ignores it with `_ =` only when the email
is not critical to the request; never block a response on a slow mail server for
bulk sends — call it from the scheduler instead.

### 11.5 `config/regex.go` — optional

Plain constants, one per rule, compiled where used. A short comment is allowed when
the pattern is not obvious.

```go
package config

const (
	EmailRegex = `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
	// Accepts international and local forms: optional '+', then 7-20 digits,
	// spaces, dots, hyphens or brackets.
	PhoneRegex    = `^\+?[0-9][0-9\s().-]{6,19}$`
	GSTRegex      = `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`
	PasswordRegex = `^.{8,}$`
)
```

```go
if !regexp.MustCompile(config.EmailRegex).MatchString(input.Email) {
	return c.JSON(http.StatusBadRequest, map[string]interface{}{
		"success": false,
		"error":   "Please enter a valid email address",
	})
}
```

### 11.6 `.env`

Only the database block is always present. Keep the block for a capability **only if
the project has that `config` file** — an empty `SMTP_*` block in a project that never
sends mail is noise.

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

# only with config/storage.go
STORAGE_REGION=
STORAGE_BUCKET=
STORAGE_ENDPOINT=
STORAGE_ACCESS_KEY=
STORAGE_SECRET_KEY=

# only with config/email.go
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
MAIL_SENDER=
MAIL_FROM=
```

`.env` is git-ignored and a `.env.example` with empty values is committed in its place.
Any new variable is read in `config/`, never with `os.Getenv` scattered through
controllers (the one accepted exception is `main.go` wiring, e.g.
`controllers.FrontendUrl = os.Getenv("FRONTEND_URL")`).

---

## 12. `auth/` package

`auth/auth.go` holds key loading, claim structs, token extraction and the middleware
constructors. Structural rules only (permission design lives in its own document):

- Package-level key material: `var PrivateKey *ecdsa.PrivateKey`, `var PublicKey string`,
  loaded from `main.go` at startup via `auth.LoadPrivateKey(...)` / `auth.LoadPublicKey(...)`.
- Claim structs are declared next to the extractor that uses them:
  ```go
  type CustomClaims struct {
  	UserID   int    `json:"user_id"`
  	RoleID   int    `json:"role_id"`
  	UserType string `json:"user_type"`
  	jwt.RegisteredClaims
  }
  ```
- File order: imports → key vars → shared types → `LoadXKey` funcs → middleware
  constructors → claim structs + `ExtractX` helpers (unexported parsing helpers such
  as `cleanPublicKey` / `parseECDSAPublicKey` sit immediately above the extractors
  that use them).
- Two middleware signatures exist:
  - `func XMiddleware(next echo.HandlerFunc) echo.HandlerFunc` — plain gate.
  - `func XMiddleware(arg string) echo.MiddlewareFunc` — parameterised gate.
- Middleware returns `401` with `{"error": "..."}` and never continues on failure.
- Controllers never parse tokens themselves; they trust `:user_id` after middleware.

---

## 13. `scheduler/` package

```go
package scheduler

import (
	"fmt"
	"time"

	"github.com/robfig/cron/v3"

	"myproject/modules/Finance/controllers"
)

func StartCronJobs() {
	PaymentVerificationCron()
	InvoiceCronJobs()
	EmailCronJobs()
}

func PaymentVerificationCron() {
	c := cron.New()
	_, err := c.AddFunc("*/5 * * * *", func() {
		controllers.OneTimePaymentVerificationCron()
	})
	if err != nil {
		fmt.Println("Error adding cron job:", err)
		return
	}
	c.Start()
}

func InvoiceCronJobs() {
	ist := time.FixedZone("IST", 5*60*60+30*60)
	c := cron.New(cron.WithLocation(ist))
	c.AddFunc("1 0 * * *", func() {
		fmt.Println("Running daily invoice job")
		controllers.CreateUpcomingInvoices()
	})
	c.Start()
}

func EmailCronJobs() {
	c := cron.New(cron.WithSeconds()) // 6-field spec: sec min hour dom mon dow
	c.AddFunc("0 0 1 * * *", func() {
		controllers.FetchAndProcessEmails()
	})
	c.Start()
}
```

Rules:

- `StartCronJobs()` is the only exported entry point called from `main.go`; it does
  nothing but call one `XCronJobs()` per domain.
- Each domain function builds **its own** `cron.New()` and calls `c.Start()`.
- **No business logic in the scheduler.** The closure only calls exported controller
  functions; the logic lives in `controllers/`.
- Use `cron.WithLocation(...)` when the schedule is business-time sensitive, and
  `cron.WithSeconds()` when the spec has 6 fields.
- Log a one-line start message inside the job so local runs are traceable.

---

## 14. `templates/` and email

- Flat folder, `snake_case.html`, one file per email: `po_approval.html`,
  `po_status.html`, `new_user_created.html`, `forgot_password.html`.
- No sub-folders, no partials.
- Parsed with `html/template` from `config/email.go`, path relative to the working
  directory: `template.ParseFiles("templates/po_approval.html")`.
- The values a template needs are passed as a `map[string]string` built in the
  `SendXEmail` function (§11.4). Placeholders in the HTML use the same keys:
  ```html
  <p>Hello {{.Username}},</p>
  <p>Purchase order <b>{{.PO_ID}}</b> for {{.Vendor}} is awaiting your approval.</p>
  <a href="{{.Link}}">Open the purchase order</a>
  ```
- Rendering (`parse`) and sending (`send`) are separate methods, so a template can be
  rendered and checked without sending anything.
- Controllers call `config.SendXEmail(...)` only; they never call
  `template.ParseFiles` or `smtp.SendMail` directly.
- Every placeholder the template uses must be set in the data map — a missing key
  renders as empty text with no error, which is how blank emails go out.
- Keep the HTML simple: inline styles, tables for layout, no external CSS or JS —
  mail clients strip them.

The full `config/email.go` boilerplate is in §11.4.

---

## 15. `main.go`

Entry point only — wiring, no logic, no route declarations.

```go
package main

import (
	"fmt"
	"log"
	"os"

	"github.com/labstack/echo/v4"

	"myproject/auth"
	"myproject/common/controllers"
	"myproject/config"
	"myproject/routers"
	"myproject/scheduler"
)

func main() {
	config.InitDB()
	scheduler.StartCronJobs()
	if err := auth.LoadPrivateKey("./private_ec.pem"); err != nil {
		log.Fatalf("❌ Error loading private key: %v", err)
	}
	if err := auth.LoadPublicKey("./public_ec.pem"); err != nil {
		log.Fatalf("❌ Error loading public key: %v", err)
	}
	e := echo.New()
	controllers.FrontendUrl = os.Getenv("FRONTEND_URL")
	routers.InitRoutes(e)
	fmt.Println("Server is running on port 8080")
	e.Logger.Fatal(e.Start(":8080"))
}
```

Fixed order: `InitDB` → `StartCronJobs` → key loading → `echo.New()` → global wiring
→ `InitRoutes` → `Start`. Keep it under ~40 lines.

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
   -- +migrate Down
   DROP TABLE IF EXISTS vendor_contracts;
   ```

2. **Model** — `modules/Purchase/models/vendor_contract.go`
   ```go
   package models

   import "time"

   type VendorContract struct {
   	ID        uint       `json:"id" gorm:"primaryKey"`
   	VendorID  int        `json:"vendor_id"`
   	Title     string     `json:"title"`
   	StartDate *time.Time `json:"start_date"`
   	EndDate   *time.Time `json:"end_date"`
   	IsActive  *bool      `json:"is_active"`
   	CreatedAt time.Time  `json:"created_at"`
   }
   ```

3. **Controller** — `modules/Purchase/controllers/vendor_contract.go`
   Order: imports → input structs → helpers → `CreateVendorContract`,
   `ListVendorContracts`, `GetVendorContractById`, `UpdateVendorContract`,
   `UpdateVendorContractStatus`, `DeleteVendorContract`. Each handler follows §6.

4. **Router** — `modules/Purchase/routers/vendor_contract.go`
   ```go
   var vendorContractPath = "/api/v1/users/:user_id/vendor-contract"

   func VendorContractRoutes(e *echo.Echo) *echo.Echo {
   	e.POST(vendorContractPath, controllers.CreateVendorContract)
   	e.GET(vendorContractPath, controllers.ListVendorContracts)
   	e.GET(vendorContractPath+"/:id", controllers.GetVendorContractById)
   	e.PATCH(vendorContractPath+"/:id/update", controllers.UpdateVendorContract)
   	e.PATCH(vendorContractPath+"/:id/is_active", controllers.UpdateVendorContractStatus)
   	e.DELETE(vendorContractPath+"/:id/delete", controllers.DeleteVendorContract)
   	return e
   }
   ```
   Once the auth layer exists, append `auth.AdminMiddleware("...")` as the last
   argument of each line (§5.3, §9.3) — nothing else in the file changes.

5. **Module aggregator** — add one line to `modules/Purchase/routers/routers.go`
   ```go
   func PurchaseRoutes(e *echo.Echo) {
   	PurchaseOrderRoutes(e)
   	VendorContractRoutes(e)   // ← new
   }
   ```
   (If the module is new, also add `purchase.PurchaseRoutes(e)` to `routers/routes.go`.)

6. **Optional pieces**
   - recurring job → new `XCronJobs()` in `scheduler/scheduler.go` calling an exported
     controller func.
   - email → `templates/vendor_contract_expiry.html` + render/send pair in `config/email.go`.

7. **Run and verify**
   ```bash
   cd <project>/backend
   go build ./...
   go run .
   ```
   Confirm the migration count printed at startup increased, then hit each new route.

---

## 17. Anti-patterns — do not do these

| Anti-pattern | Do instead |
|---|---|
| Business logic or DB calls in `models/` | models are struct-only; logic in `controllers/` |
| DB queries in `routers/` | routers only map paths → handlers |
| Repeating the full route literal on every line | one `var xPath` + suffixes |
| Declaring routes inside `routes.go` / `routers.go` | aggregators only call `XRoutes(e)` |
| `os.Getenv` scattered across controllers | read env in `config/`, expose a variable |
| API keys, SMTP passwords or bucket secrets written in the code | read them from `.env` (§11) — committed keys cannot be rotated |
| Rewriting the storage/email/database boilerplate per project | copy §11 and change only the env values |
| Copying `storage.go` / `email.go` / `ws_notification.go` into a project that does not use them | only `database.go` is mandatory — add a config file when the capability is actually needed (§11) |
| `.env` blocks for capabilities the project does not have | keep only the variables the existing config files read |
| Storing uploaded bytes in the database | upload to the bucket, store the returned URL (§11.2) |
| Using `file.Filename` directly in a storage key or path | `config.SanitizeFileName(file.Filename)` (§11.2) |
| A second copy of `SanitizeFileName` in a module | one copy in `config/storage.go`, called everywhere |
| A migration without a working `Down`, or without indexes on its FKs | follow the templates in §10.2 |
| Opening a new DB connection in a controller | always use `config.DB` |
| Editing an already-applied migration | add a new `alter_` migration |
| `AutoMigrate` alongside SQL migrations | SQL files are the only schema source |
| Returning bare arrays / strings / `echo.NewHTTPError` from a handler | the `success` envelope from §7 |
| Mixing `{"data": ...}` and `{"response": {"data": ...}}` in one module | pick one per module and keep it |
| Helper functions interleaved between handlers | helpers above the handler block, or in `helper.go` |
| Reading a query param, or declaring a var, in the middle of a handler | all inputs, vars and defaults in the input block at the top (§6) |
| Copying the same big helper into two controller files of a module | move it once into the module's `helper.go` (§5.6.1) |
| Indenting with the space bar | indent with tabs — `gofmt` + `.editorconfig` (§5.8) |
| Paragraph comments, or comments restating the code | 1–2 line comments, only where the reason is not obvious (§5.8) |
| Blank rows inside a function, or two blank lines in a row | no blank line inside a function, exactly one between functions (§5.8) |
| Commented-out old code left in the file | delete it — git keeps the history |
| Creating `helper.go` for a helper only one file uses | keep it in that file's helper block |
| `utils.go` / `misc.go` / `common.go` inside a controllers package | `helper.go` |
| Deleting a record without checking dependents | dependency guards first (§6.5) |
| Blind `config.DB.Save(&input)` on update | field-by-field diff with `changes` (§6.3) |
| Leaking driver/SQL errors to the client | fixed human-readable messages |
| Returning `500 Internal Server Error` | classify it — `400`, `404`, `403`, `409` (§6.7) |
| Filters or search sent in the request body | query params on `GET` (§6.8) |
| Multipart form-data on an endpoint with no upload | plain JSON body |
| Spreading record fields across many form keys | one JSON string in `data`, binaries in `files` / `images` (§6.8) |
| `Find` everything then slice/filter/sum in Go | `Where` + `Limit`/`Offset` + `COUNT`/`SUM` in SQL (§6.9) |
| A DB query inside a `for` loop (N+1) | one `WHERE id IN (?)` query, then map in Go (§6.9) |
| Preloading every relation on a list endpoint | preload only what the list shows; full detail in `GET /:id` |
| Listing without `Order(...)` | always sort explicitly, or pages repeat rows |
| Multi-table writes without a transaction | `config.DB.Transaction(func(tx *gorm.DB) error {...})` |
| Business logic inside a cron closure | closure calls an exported controller func |
| One giant controller covering several entities | one file per entity |
