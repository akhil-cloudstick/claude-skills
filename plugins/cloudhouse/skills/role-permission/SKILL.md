---
name: role-permission
description: "Role and permission standard, backend and frontend together — permissions and role_permissions tables, seeding and grant defaults, token claims, permission middleware, error shapes, the permissions API, and on the frontend the permission store, can() helper, route guard, gate component and sidebar filtering so a blocked page is hidden rather than shown empty. Use for ANY authorization work — adding a permission, gating a route or endpoint, building the role-permission admin screen, wiring auth middleware, or auditing an existing RBAC setup. Language and framework neutral; pairs with /cloudhouse:backend and /cloudhouse:go-backend. Invoked as /cloudhouse:role-permission."
---

# Role & Permission Skill — one contract across backend and frontend

You are working under a fixed house standard. **Part B of this file is the standard.**
It is not advice and not a starting point: it is the specification.

Authorization is the one feature that is only correct when **both halves agree**. The backend
decides; the frontend obeys. A permission switched off by an admin must produce two effects at
once:

- the API refuses the call, and
- the page never appears in the navigation.

A visible menu item that leads to an empty list is a **bug**, not a denial. That failure is the
single thing this standard exists to prevent, and it is why the backend rules and the frontend
rules live in one file — so they cannot drift apart.

Read Part B in full before writing or changing a single line of code or SQL.

---

## 0. First — identify BOTH stacks

Authorization work always touches two codebases. Before writing anything:

1. **Backend** — read the manifest (`package.json`, `go.mod`, `composer.json`,
   `pyproject.toml`, `pom.xml`, `Gemfile`) and identify the language, framework and ORM.
2. **Frontend** — identify the framework (React, Vue, Angular, Svelte, …), the router and the
   state container.
3. If either is unclear, or you can only see one of the two repositories, **ask once**, then
   proceed.

From that point every example, file name and snippet you produce is in **those stacks' idioms
only**. Never show the user code from a language the project does not use.

**The examples in this document are pseudocode on purpose.** They fix the shape, the order and
the sequence — not the syntax. Translate them. The parts that are **not** pseudocode — the SQL
in §3, the JSON in §7, the URLs, and the permission-name derivation in §2 — are literal and
identical in every stack, because they are the wire contract between the two halves.

This skill composes with the structure standards: file layout, handler body order and the
response envelope come from **`/cloudhouse:backend`** (any language) or
**`/cloudhouse:go-backend`** (Go + Echo). This skill only adds the authorization layer.

---

## 1. Pick the mode

Read what the user typed after `/role-permission` and choose one:

| The user asks for | Mode |
|---|---|
| set up roles/permissions, add a permission, gate an endpoint or a page, build the role-permission admin screen | **A — Build** |
| "check / review / audit our permissions", "is this properly secured" | **B — Audit** |
| anything else touching auth or permission code (a bug fix, a tweak) | **C — Edit** |

If it is genuinely unclear, ask once, then proceed.

---

## 2. Mode A — Build

Adding or gating a capability is **never a one-sided change.** Work in this order, because each
step depends on the one before it:

1. **Migration** — insert the permission row, then back-fill a `role_permissions` row for every
   existing role (§3.3).
2. **Backend route** — add the permission argument to the route registration (§6.4).
3. **Frontend nav metadata** — attach `module` + `permissionKey` to the menu item (§12).
4. **Frontend route guard** — wrap the route so a direct URL is refused (§11).
5. **In-page gates** — hide the buttons the user cannot use (§10).

Then state, in one line each: the permission name you used, the routes you gated, and the nav
entries you filtered.

**A permission that exists on only one side is an incomplete change.** If you gated an endpoint
but did not filter the menu, the user still sees the page and gets a 403 — the exact failure
this standard prohibits. If you filtered the menu but did not gate the endpoint, you have
built a decoration, not a control.

Run the self-check in section 5 before reporting done.

---

## 3. Mode B — Audit an existing setup

Do **not** change anything until the user approves.

1. Read enough to judge, on both sides: the permission migrations, the middleware file, a
   sample of route files across modules, the permission controller, the frontend permission
   store, the route guard, and the sidebar/nav config.
2. Run the **two-directional sweep** — this is what catches the real problems:

   **(a) Route → catalogue.** Collect every permission string passed to middleware in the
   router files. Every one must exist in the permission catalogue. A route gated with a
   permission name that is not seeded is **permanently 403** for everyone.

   **(b) Catalogue → route.** Collect every permission in the catalogue. Every one should gate
   at least one route, or be referenced by the frontend. A permission that is seeded, shown as
   a toggle in the admin UI, and enforced nowhere is a **lie to the administrator** — they
   switch it off and nothing happens.

   **(c) Backend → frontend.** Every gated route's permission must have a corresponding nav
   filter or route guard on the frontend, or the user gets a visible-but-broken page.

   **(d) Frontend → backend.** Every permission the frontend checks must be enforced by a
   route, or it is security theatre.

3. Produce this table, most severe first:

   | # | File | Rule broken (§) | What is wrong | Fix |
   |---|---|---|---|---|

   Check at least: table shape and constraints (§1), permission naming (§2), migration
   back-fill (§3), role lifecycle (§4), token claims and key handling (§5), middleware sequence
   and error shapes (§6), the permissions API (§7), handler-side rules (§8), the frontend store
   (§9), check helper (§10), route guarding (§11), nav filtering (§12), 403 handling (§13).

4. Report the **unauthorized-route ratio**: how many gated routes use the auth-only sentinel
   (§6.5) versus a real permission. A quarter of the API being "any valid token" is worth
   knowing about.

5. Group the findings into: **(a) mechanical** — naming, missing indexes, error-shape
   inconsistency; **(b) structural** — missing back-fill migrations, permissions enforced on
   one side only, missing nav filtering; **(c) security** — unwired middleware, hardcoded
   secrets, permissions in the token, fail-open checks, missing route guards.

6. Then ask the user, with the counts filled in:

   > Found N violations: X mechanical, Y structural, Z security.
   > 1. Fix everything
   > 2. Fix security + structural only, leave naming and cosmetics
   > 3. Fix a specific list I give you
   > 4. Leave it as is — report only
   >
   > Which one?

7. Apply only what was chosen. Fix **security findings first**, one at a time, and confirm the
   app still authenticates after each. Never batch a middleware change with a schema change.

8. Re-run the sweep and report what is now compliant and what the user chose to leave.

---

## 4. Mode C — Edit

Small change, same rules. Before editing, check whether the file already follows Part B. If it
does not, fix the part you are touching to be compliant, mention the rest in one line, and do
not silently spread the old pattern.

**Never weaken a check to make something work.** If a call is failing with 403, the fix is a
correct grant or a correct permission name — not removing the middleware argument, not
commenting out the guard, and not adding a role-name special case.

---

## 5. Self-check — run before saying you are done

Every backend item has a frontend twin. Both must be true.

**Data**
- [ ] `permissions`, `roles`, `role_permissions` match §1, including `UNIQUE (role_id, permission_id)` and the indexes
- [ ] Permission name follows `can <verb> <noun>`, module name is Title Case (§2)
- [ ] The migration inserted the permission **and** back-filled a row for every existing role (§3.3)
- [ ] Migration is idempotent — re-running it changes nothing (§3)

**Backend**
- [ ] The signing key is read from the environment and startup **aborts** if it is missing (§5)
- [ ] Token claims carry `user_id`, `role_id`, `user_type` — and **no permission list** (§5)
- [ ] Every new endpoint has a permission argument, or a stated reason it is auth-only (§6)
- [ ] The permission string in the route matches the catalogue row exactly, character for character (§2)
- [ ] Middleware errors use the standard envelope and the §6.3 status codes; expired is distinct from invalid
- [ ] Permission updates run in one transaction (§7.3)
- [ ] Controllers do not re-query the acting user that middleware already validated (§8)

**Frontend**
- [ ] The permission map is fetched on login **and** on every app mount (§9)
- [ ] Lookups are `permissions[module][key] === true` — O(1), never a scan over a name string (§9)
- [ ] The route is guarded, and the guard **waits for loaded** before deciding (§11)
- [ ] The nav item carries `module` + `permissionKey` and is **filtered out of the array**, not disabled (§12)
- [ ] An empty nav group renders nothing at all (§12)
- [ ] Buttons for actions the user cannot perform are gated (§10)
- [ ] A 403 produces a visible denial, not a console log (§13)

**Both**
- [ ] Every permission you touched is enforced on the backend AND reflected in the frontend
- [ ] Log in as a restricted role and confirm the page is **absent from the menu**, the direct URL is refused, and the API returns 403

---

## 6. Non-negotiables

1. **The backend is the enforcement; the frontend is the experience.** A hidden button is not
   a control. Every gated capability has a route-level check.
2. **Never render a page the user cannot use.** Filter it out of the nav and guard the route.
   An empty list is a bug, not a denial.
3. **One permission name, three places, spelled identically** — catalogue row, route middleware
   argument, frontend key.
4. **Every role has a row for every permission.** A missing row means the permission vanishes
   from the admin toggle screen and can never be granted.
5. **`is_system` roles are never editable or deletable.**
6. **Permission checks are data, never code.** No `IF role.name == "Manager"` anywhere, ever.
7. **A permission change is one transaction.**
8. **The token carries identity, not permissions.** A revoked permission must take effect
   without the user logging in again.
9. **Fail closed** on the backend and on route guards. The one documented exception is
   visibility permissions (§7.4).
10. **No secrets in code.** The signing key comes from the environment, and startup aborts if
    it is missing.

If the user explicitly asks for something that breaks a rule, say which rule in one sentence,
then do what they asked.

## 7. Staying on the standard for the whole session

This standard applies to every later message in the conversation, not only the one that invoked
`/role-permission`. Before each new endpoint, page or migration, re-check section 5. If the
conversation has been long, re-read the relevant section of Part B rather than working from
memory.

---
---

# PART B — THE STANDARD

Everything below this line is the specification. Follow it exactly.

# Role & Permission Standard (any language, any framework)

This document defines how authorization is modelled, enforced and reflected in the UI. It
covers the database tables, the permission vocabulary, the migrations, the token, the
middleware, the permissions API, and the frontend store, guard, gate and navigation filter.

Read §1–§3 before your first migration; §6 and §12 are the two you will come back to.

### How to read the examples

```
MIDDLEWARE Name(arg):          a request-time gate
HANDLER Name(request):         an HTTP handler
FUNC name(args) -> type:       a plain function
COMPONENT Name(props):         a UI component
STORE.x                        application state
DB.first(Model, cond)          fetch one row, or nothing
RETURN 403 { ... }             status code + response envelope
# comment
```

SQL, JSON and URLs are **literal** — copy them exactly.

---

## 1. The model

Three tables. This is the whole model — there is no separate `modules`, `menus` or `features`
table, and no per-action boolean columns.

```sql
CREATE TABLE roles (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	description TEXT,
	is_active BOOLEAN NOT NULL DEFAULT TRUE,
	is_system BOOLEAN NOT NULL DEFAULT FALSE,
	access_control TEXT,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE permissions (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) UNIQUE NOT NULL,
	description TEXT,
	module_name TEXT NOT NULL,
	is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE role_permissions (
	id SERIAL PRIMARY KEY,
	role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
	permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
	permission BOOLEAN NOT NULL DEFAULT TRUE,
	UNIQUE (role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX idx_permissions_module_name ON permissions(module_name);
```

Column notes:

| Column | Why it exists |
|---|---|
| `roles.is_system` | Marks a role that must never be edited or deleted (the seeded Admin). **This is a column, not a name check.** Comparing `name = 'Admin'` in code breaks the moment somebody renames the role, and it cannot be extended to a second protected role without editing code. |
| `roles.access_control` | Which dashboard/surface the role belongs to, when a product has more than one (`admin`, `staff`). Optional — omit it in a single-surface product. |
| `permissions.name` | The permission itself, and the contract (§2). Unique. |
| `permissions.module_name` | The display grouping in the admin screen, and the first half of the frontend key (§2.2). |
| `role_permissions.permission` | The grant. Defaults to `TRUE` (§4.1). |
| `UNIQUE (role_id, permission_id)` | **Required.** Without it, a concurrent double-toggle inserts two rows for the same pair and the effective grant becomes whichever row the query happens to read first. |

`role_permissions` is a pure join row: no timestamps, no logic, no soft delete. Revoking is
setting `permission = false`, never deleting the row — a deleted row disappears from the admin
screen (§4.2).

Models/entities for these three tables are **declarations only**, per the structure standard —
no methods, no hooks, no queries.

---

## 2. Naming permissions

The permission name is the contract. It appears in three places and must be **character-for-
character identical** in all three.

### 2.1 The form

```
can <verb> <noun>
```

Lowercase, spaces, no punctuation, singular noun.

| Verb | When |
|---|---|
| `view` | reading — list, detail, export, report |
| `change` | any mutation — create, update, delete, reorder, assign |
| `approve` / `reject` | a real approval authority, separate from ordinary editing |
| `audit` | a review step distinct from approval |
| `delete` | **only** when destruction is a separately-granted authority beyond `change` |

**Default to the `view` / `change` pair, one per module.** Do not create
`can create X` / `can edit X` / `can delete X` / `can list X` — four toggles per module produces
an admin screen nobody reads, and in practice they are always switched together. Split further
only when a real business rule says one person may edit and a different person may approve.

```
can view invoice          can change invoice          can approve invoice
can view purchase order   can change purchase order
can view expense          can change expense          can delete expense
can view role and permission                          can change role and permission
```

`module_name` is Title Case with spaces and ends in `Management`:

```
Invoice Management    Expense Management    Purchase Order Management
Role Management       Project Management    Visibility Management
```

Every permission belongs to exactly one module. The module is what the admin screen groups by,
so a module with one permission is fine; a permission with no module is not.

### 2.2 The derivation to the frontend key

The frontend never sends the English sentence. Both halves of the name are transformed the same
way: **replace every space with an underscore.** Nothing else — no lowercasing beyond what is
already there, no stripping of `can`.

| `module_name` | `permissions.name` | Frontend lookup |
|---|---|---|
| `Invoice Management` | `can view invoice` | `permissions["Invoice_Management"]["can_view_invoice"]` |
| `Expense Management` | `can change expense` | `permissions["Expense_Management"]["can_change_expense"]` |
| `Purchase Order Management` | `can view purchase order` | `permissions["Purchase_Order_Management"]["can_view_purchase_order"]` |
| `Role Management` | `can change role and permission` | `permissions["Role_Management"]["can_change_role_and_permission"]` |

The transformation happens **once, on the backend**, in the bootstrap endpoint (§7.1). The
frontend receives the keys already derived and never does string manipulation on a permission
name.

### 2.3 Renaming is a breaking change

Because the name is simultaneously the database row, the middleware argument and the source of
the frontend key, **renaming a permission breaks all three silently**. Nothing fails at compile
time; routes simply start returning 403 and menu items simply disappear.

Do not rename in place. If a permission genuinely must be renamed:

1. Insert the new permission and back-fill grants **copied from the old one**, so nobody's
   access changes.
2. Gate the routes with the new name; leave the old permission in place.
3. Update the frontend keys.
4. Ship, verify, and only then remove the old permission in a later migration.

This is also why the description column exists: **reword the description freely, never the
name.** The description is what the admin screen shows underneath the toggle, so it can carry
the human explanation while the name stays frozen.

---

## 3. Migrations

Permission changes are schema changes: plain numbered SQL files, per the structure standard
(`NNNN_<verb>_<subject>.sql`, Up/Down, no `BEGIN`/`COMMIT`, never edited once applied).

### 3.1 Creating the RBAC schema

One migration containing the three tables from §1 with their constraints and indexes. Its
`Down` drops `role_permissions`, then `permissions`, then `roles` — children first.

### 3.2 Seeding the catalogue and the system role

```sql
-- +migrate Up

INSERT INTO permissions (name, description, module_name) VALUES
	('can view invoice',   'View invoices, invoice detail and invoice exports', 'Invoice Management'),
	('can change invoice', 'Create, update and delete invoices',                'Invoice Management'),
	('can view expense',   'View the expense list and expense detail',          'Expense Management'),
	('can change expense', 'Create, update and delete expenses',                'Expense Management')
ON CONFLICT (name) DO NOTHING;

INSERT INTO roles (name, description, is_active, is_system)
VALUES ('Admin', 'Full access. Cannot be edited or deleted.', TRUE, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id, permission)
SELECT r.id, p.id, TRUE
FROM roles r CROSS JOIN permissions p
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- +migrate Down

DELETE FROM role_permissions;
DELETE FROM roles WHERE name = 'Admin';
DELETE FROM permissions;
```

The `ON CONFLICT … DO NOTHING` clauses are what make the file idempotent — and they only work
because of the `UNIQUE` constraints in §1.

### 3.3 Adding a permission later — the template you will use most

Two statements, always both. Adding the catalogue row without the back-fill is the single most
common mistake: the permission exists, no role has a row for it, so it **does not appear in the
admin screen at all** and can never be granted.

```sql
-- +migrate Up

INSERT INTO permissions (name, description, module_name)
VALUES ('can view asset', 'View the asset registry and asset detail', 'Asset Management')
ON CONFLICT (name) DO NOTHING;

-- Back-fill every existing role. New permissions are granted by default; the
-- administrator switches them off per role in the admin screen.
INSERT INTO role_permissions (role_id, permission_id, permission)
SELECT r.id, p.id, TRUE
FROM roles r CROSS JOIN permissions p
WHERE p.name = 'can view asset'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- +migrate Down

DELETE FROM role_permissions
WHERE permission_id IN (SELECT id FROM permissions WHERE name = 'can view asset');

DELETE FROM permissions WHERE name = 'can view asset';
```

**The grant default is `TRUE` for every existing role** — the same rule as a newly created role
(§4.1). The administrator curates by switching things off, not by hunting for what to switch
on.

Be aware of what this means and say so when you ship one: **a new permission grants the
capability to every existing role until somebody revokes it.** If the capability is genuinely
sensitive (money movement, deletion, data export), say so in one line when you present the
migration so the administrator knows to review the roles immediately after deploying. Do not
silently change the default — that is the standard, and a per-migration exception would make
two projects behave differently.

Log the back-fill. Role and permission changes made through the UI are activity-logged (§7.3);
a migration that grants a capability to every role should leave the same trail, so a later
review can answer "when did this role get that".

### 3.4 Rules

- One permission per migration, or one coherent module's worth. Never mix a permission
  addition with an unrelated schema change.
- Never edit an applied migration to change a grant. Write a new one.
- Never renumber.
- The permission name in the migration, in the route, and in the frontend are the same string.
  Copy-paste it; do not retype it.

---

## 4. Roles — lifecycle and grant defaults

### 4.1 Creating a role grants everything

When a role is created, the handler writes a `role_permissions` row for **every** permission in
the catalogue, with `permission = TRUE`. The administrator then switches off what that role
should not have, in the admin screen.

```
HANDLER createRole(request):
	# ... input block, validation, duplicate-name check per the structure standard ...
	DB.transaction(tx => {
		tx.create(role)
		permissions = tx.list(Permission)
		rows = []
		FOR p IN permissions:
			rows.append({ role_id: role.id, permission_id: p.id, permission: true })
		tx.bulkCreate(rows)
	})
	createActivityLog(actor.id, "create", "role", role.id,
		"Role '" + role.name + "' created with all " + count(permissions) + " permissions granted")
	RETURN 200 { "success": true, "message": "Role created successfully", "data": role }
```

Both writes are in **one transaction**. A role that exists with no permission rows is invisible
in the admin screen and cannot be repaired through the UI.

The activity-log line names the count, so a review can see that a permissive default was
applied rather than a deliberate grant.

### 4.2 Revoking is `false`, never a deleted row

The admin screen renders one toggle per row in `role_permissions`. Delete the row and the
toggle disappears — the administrator can no longer grant it back, and the permission looks
like it does not exist for that role. **Set `permission = false`.**

The corollary: if a role is somehow missing a row (an older role created before a permission
was added, a failed migration), the update endpoint **creates the row on demand** rather than
failing (§7.3).

### 4.3 System roles

A role with `is_system = TRUE`:

- cannot be renamed, deactivated or deleted — `403 {"success": false, "error": "System roles cannot be modified"}`;
- cannot have its permissions changed — same response from the permission update endpoint;
- is seeded by migration, never created through the UI.

Exactly one system role is seeded by default (`Admin`). A product may seed a second where a
real second superuser tier exists. **Do not implement this as a name comparison.** The whole
point of the column is that `IF role.name == "Admin"` is a code check pretending to be data.

### 4.4 Deleting a role

Guard first, per the structure standard's delete rules: if any user still holds the role,
refuse and **name the blockers**.

```
	users = DB.list(User, role_id = id, limit 5)
	IF count(users) > 0:
		RETURN 400 { "success": false,
			"error": "Cannot delete: this role is assigned to " + total + " user(s): " + join(names, ", ") }
```

`role_permissions` rows go with the role via `ON DELETE CASCADE`.

---

## 5. The token

### 5.1 Claims

```
CLAIMS:
	user_id    int
	role_id    int
	user_type  string     # which surface: "admin" | "staff" — only when the product has more than one
	+ standard registered claims (issuer, subject, expiry)
```

**Never embed the permission list in the token.** It is the most tempting optimisation here and
it is wrong for one decisive reason: the token is immutable until it expires. An administrator
revoking a permission would have no effect until the user logs in again — which can be days.
Carrying `role_id` and resolving the grant per request means a revocation takes effect on the
next call.

It also keeps the token small enough to stay out of header-size limits as the catalogue grows.

### 5.2 The signing key

- Read from the environment, in the config layer, exactly once.
- **Startup aborts** if it is missing or empty. A missing key does not fall back to a default
  and does not sign with an empty string — that produces tokens anybody can forge, and nothing
  in the logs would say so.
- Never a literal in the source.

```
FUNC initAuth():
	signingKey = env("JWT_SECRET")
	IF signingKey IS EMPTY:
		exit("❌ JWT_SECRET is not set")
```

### 5.3 Parsing

- **Assert the algorithm family** before trusting the token. A parser that accepts whatever the
  token's header claims will accept a token signed with `none`, or an RSA-verified token signed
  with the public key as an HMAC secret.
- Distinguish **expired** from **invalid** (§6.3) — they need different words to the user.

### 5.4 Where the token travels

The `Authorization` header, always.

**One exception: websocket upgrade routes may accept `?token=`**, because browsers cannot set
custom headers on a websocket handshake. That fallback is confined to those routes and is not
available on ordinary API routes.

Accepting a query-string token everywhere puts a valid credential into web-server access logs,
browser history, and the `Referer` header of every outbound link — permanently, in plaintext,
on systems whose retention nobody controls.

### 5.5 Revocation

The standard is short-lived tokens plus a server-side check on the paths that matter. At
minimum, the middleware must reject a token whose user is now inactive — a deactivated employee
holding a valid token otherwise keeps full access until it expires.

---

## 6. The middleware

### 6.1 Two shapes

```
MIDDLEWARE requirePermission(permissionName)   # parameterised gate — the normal case
MIDDLEWARE requireAuth                          # plain gate — authentication only
```

Where the framework uses guard classes, decorators or attributes rather than functions, the two
shapes are the same: one that gates on a named permission, one that only proves identity.

### 6.2 The sequence

Fixed order. Each step returns immediately on failure.

```
MIDDLEWARE requirePermission(permissionName):
	RETURN handler(request):
		# 1. extract the token
		raw = request.header("Authorization")
		IF raw IS EMPTY AND route.isWebsocket:
			raw = request.query("token")
		IF raw IS EMPTY:
			RETURN 401 { "success": false, "error": "Missing token" }
		# 2. parse and classify the failure
		claims, err = parseToken(raw)
		IF err IS EXPIRED:
			RETURN 401 { "success": false, "error": "Session expired, please log in again" }
		IF err:
			RETURN 401 { "success": false, "error": "Invalid token" }
		# 3. the acting user in the path must be the token's user
		IF request.hasPath("user_id") AND toInt(request.path("user_id")) != claims.user_id:
			RETURN 401 { "success": false, "error": "Invalid user" }
		# 4. the surface must match, where the product has more than one
		IF surface != "" AND claims.user_type != surface:
			RETURN 403 { "success": false, "error": "Access denied" }
		# 5. auth-only routes stop here
		IF permissionName == AUTH_ONLY:
			RETURN next(request)
		# 6. resolve the grant — ONE query, cached for this request
		granted = resolveGrant(request, claims.role_id, permissionName)
		IF granted IS NOT_FOUND:
			RETURN 403 { "success": false, "error": "Permission not found" }
		IF granted IS false:
			RETURN 403 { "success": false, "error": "Access denied" }
		RETURN next(request)
```

**Step 6 is one join, not two lookups.**

```
FUNC resolveGrant(request, roleId, permissionName) -> bool | NOT_FOUND:
	cache = request.context("permissionCache")   # per-request, created on first use
	IF cache.has(permissionName):
		RETURN cache.get(permissionName)
	row = DB.first(
		SELECT rp.permission
		FROM role_permissions rp
		JOIN permissions p ON p.id = rp.permission_id
		WHERE rp.role_id = ? AND p.name = ?, roleId, permissionName)
	result = row IS NULL ? NOT_FOUND : row.permission
	cache.set(permissionName, result)
	RETURN result
```

Two separate queries — look up the permission by name, then look up the join row — costs two
database round-trips on **every gated request**, which is most of the API. One join costs one.
The per-request cache matters because a single request can pass through more than one gate.

`NOT_FOUND` (no row at all) and `false` (row exists, revoked) are different states and are
worth distinguishing in the response: the first almost always means a typo in the route's
permission string or a missing back-fill migration, and saying so turns a mystery into a
one-line fix.

### 6.3 Error responses

Every middleware response uses the **same envelope as the rest of the API** (`/cloudhouse:backend`
§7). A middleware that returns a different shape from the controllers means the frontend needs
two error parsers, and one of them will be forgotten.

| Case | Status | Body |
|---|---|---|
| No token at all | `401` | `{"success": false, "error": "Missing token"}` |
| Token expired | `401` | `{"success": false, "error": "Session expired, please log in again"}` |
| Malformed / bad signature / wrong algorithm | `401` | `{"success": false, "error": "Invalid token"}` |
| Path `:user_id` is not the token's user | `401` | `{"success": false, "error": "Invalid user"}` |
| Wrong surface for this route | `403` | `{"success": false, "error": "Access denied"}` |
| Permission name not in the catalogue | `403` | `{"success": false, "error": "Permission not found"}` |
| Role has the row, `permission = false` | `403` | `{"success": false, "error": "Access denied"}` |
| User is no longer active | `401` | `{"success": false, "error": "Account is inactive"}` |

**Expired must be distinguishable from invalid.** Collapsing both into "Invalid token" leaves
the client unable to tell "your session ran out, log in again" from "something is wrong with
your credentials" — so it either logs everyone out on any auth error, or nobody.

Never leak *why* a permission was denied beyond these strings — no permission names, no role
names, no row ids in the response. Log the detail server-side.

### 6.4 Wiring it to routes

The permission argument goes on the route registration, as the last argument, per the routing
rules in the structure standard:

```
	app.GET(invoicePath, listInvoices, requirePermission("can view invoice"))
	app.POST(invoicePath, createInvoice, requirePermission("can change invoice"))
	app.GET(invoicePath + "/:id", getInvoiceById, requirePermission("can view invoice"))
	app.PATCH(invoicePath + "/:id/update", updateInvoice, requirePermission("can change invoice"))
	app.PATCH(invoicePath + "/:id/approve", approveInvoice, requirePermission("can approve invoice"))
	app.DELETE(invoicePath + "/:id/delete", deleteInvoice, requirePermission("can change invoice"))
```

Rules:

- **Every route gets one.** A route with no gate is a decision, and it must be a deliberate one.
- `view` gates reads; `change` gates every mutation; a distinct authority gets its own name.
- The string is the catalogue row, exactly. Not `"can view invoices"`, not `"Can view invoice"`.
- Where the framework attaches guards by decorator or attribute, the permission name goes there
  instead — the rule is that it sits **on the route declaration**, never inside the handler.

### 6.5 The auth-only sentinel

Some routes need a valid token but no specific permission — the bootstrap endpoint itself, the
current-user profile, shared lookup lists. Mark them explicitly:

```
	app.GET(profilePath, getProfile, requireAuth)
```

Do not reach for this because you have not decided yet. Every auth-only route is a route any
authenticated user can call, and they accumulate: it is easy to end up with a quarter of the
API behind authentication with no authorization at all, which looks secured and is not.

**Audit mode counts them and reports the ratio.** If auth-only is more than a small minority of
gated routes, that is a finding.

---

## 7. The permissions API

Three endpoints. The shapes below are **literal** — both halves of the contract depend on them,
and a frontend written against one product should work against another.

### 7.1 Bootstrap — what the signed-in user may do

```
GET /api/v1/users/:user_id/permissions/by-employee
```

Returns the derived map (§2.2), flat and boolean, for the caller's own role:

```json
{
  "success": true,
  "data": {
    "Invoice_Management": { "can_view_invoice": true, "can_change_invoice": false },
    "Expense_Management": { "can_view_expense": false, "can_change_expense": false },
    "Visibility_Management": { "can_view_analytic_dashboard": true }
  }
}
```

This is the only permissions call the ordinary app makes. It is gated `requireAuth`, **never**
with a permission — a permission on the bootstrap endpoint is a deadlock: the user cannot load
their permissions because they lack the permission to load their permissions.

Booleans, not objects. The frontend does one lookup per check, millions of times; it must be a
constant-time index, not a scan.

### 7.2 The admin matrix — what a given role may do

```
GET /api/v1/users/:user_id/permissions?role_id=<id>&search=<term>
```

Gated `requirePermission("can view role and permission")`. Grouped by module, ordered stably:

```json
{
  "success": true,
  "role": { "id": 7, "name": "Project Manager", "is_active": true, "is_system": false },
  "data": {
    "Invoice Management": [
      {
        "id": 812,
        "role_id": 7,
        "permission_id": 20,
        "permission": true,
        "permissions": {
          "id": 20,
          "name": "can view invoice",
          "description": "View invoices, invoice detail and invoice exports",
          "module_name": "Invoice Management"
        }
      }
    ]
  }
}
```

Note the difference from §7.1: here the **display** names are used (`Invoice Management`,
`can view invoice`), because this payload drives a screen a human reads. The derived
underscore keys are only for programmatic lookup.

Order permissions within a module by `permissions.id` so the toggles do not jump around
between loads.

### 7.3 Updating grants

```
PATCH /api/v1/users/:user_id/permissions/:role_id
PATCH /api/v1/users/:user_id/permissions/:role_id/set-all?permission=true|false
```

Both gated `requirePermission("can change role and permission")`.

The body of the first is a **bare JSON array** — one entry per toggled permission, so the same
endpoint serves a single switch and a bulk save:

```json
[ { "permission_id": 20, "permission": false }, { "permission_id": 21, "permission": false } ]
```

```
HANDLER updateRolePermissions(request):
	userId = request.path("user_id")
	roleId = toInt(request.path("role_id"))
	DECLARE role, updates
	IF roleId IS INVALID:
		RETURN 400 { "success": false, "error": "Invalid role" }
	role = DB.first(Role, id = roleId)
	IF NOT role:
		RETURN 404 { "success": false, "error": "Role not found" }
	IF role.is_system:
		RETURN 403 { "success": false, "error": "System roles cannot be modified" }
	updates = parse(request.body())
	IF updates IS EMPTY:
		RETURN 400 { "success": false, "error": "Provide an array of {permission_id, permission}" }
	DB.transaction(tx => {
		FOR u IN updates:
			IF NOT tx.exists(Permission, id = u.permission_id):
				FAIL "Permission not found"
			# create on demand — a role predating this permission has no row yet (§4.2)
			tx.upsert(RolePermission,
				WHERE role_id = roleId AND permission_id = u.permission_id,
				SET permission = u.permission)
	})
	IF FAILED:
		RETURN 400 { "success": false, "error": "Failed to update permissions" }
	createActivityLog(actor.id, "update", "role_permission", roleId,
		"Permissions updated for role '" + role.name + "': " + describe(updates))
	RETURN 200 { "success": true, "message": "Permissions updated successfully" }
```

**One transaction for the whole array.** Applying the updates one at a time outside a
transaction means a failure halfway leaves the role in a state the administrator never chose —
half the toggles they flipped applied, half not, with a success-looking screen.

The `upsert` relies on `UNIQUE (role_id, permission_id)` (§1). Without the constraint, two
administrators toggling at once each insert a row and the grant becomes ambiguous.

`set-all` is one statement over the role, in one transaction, and is subject to the same
`is_system` guard.

### 7.4 Two polarities

Almost every permission is **positive**: `true` means "may". The check is `=== true`, so a
missing or not-yet-loaded value denies. Fail closed.

A small number are **visibility** permissions — they hide something rather than granting it
(`can view fund details`, `can view analytic dashboard`). These are checked as `=== false`, so
they hide only on an explicit revocation. Fail open, deliberately: a not-yet-loaded map would
otherwise blank out figures for a fraction of a second on every page load, which reads as a
broken UI.

Keep them in their own module (`Visibility Management`) so the polarity is visible in the admin
screen and in the code, and **do not mix the two conventions inside one module.**

---

## 8. Handler-side rules

**Controllers trust the middleware.** The gate has already proved the token is valid, the
`:user_id` is the token's user, and the role holds the permission. Re-querying the user at the
top of every handler just to check it exists is a wasted round-trip on every request — and it
tends to spread until it is in fifty handlers.

Fetch the acting user only when you actually need its **data** (a company id, a name for the
activity log), not to re-authorise.

**Never re-check the permission in the handler.** Two checks for one rule means two places to
update, and they will disagree.

### 8.1 The exception — row-scoping permissions

Some permissions filter rows rather than gating a route: "this role sees only the projects it
is assigned to". A gate cannot express that — the route is allowed, the result set is narrowed
— so it belongs in the handler, in the query.

```
HANDLER listProjects(request):
	# ... input block per the structure standard ...
	assignedOnly = true                     # fail closed: if we cannot resolve it, restrict
	grant = DB.first(
		SELECT rp.permission FROM role_permissions rp
		JOIN permissions p ON p.id = rp.permission_id
		WHERE rp.role_id = ? AND p.name = ?, employee.role_id, "view assigned projects only")
	IF grant IS NOT NULL:
		assignedOnly = grant.permission
	query = DB.query(Project)
	IF assignedOnly:
		query = query.where("id IN (SELECT project_id FROM project_assignees WHERE employee_id = ?)", employee.id)
	# ... pagination, filters, envelope ...
```

Two rules for these:

- **Fail closed.** If the role or the grant cannot be resolved, restrict. A lookup failure that
  silently clears the restriction lists every row to someone who should see a handful.
- **Resolve with one join**, the same way the middleware does — not a different query shape for
  the same logical question.

---

## 9. Frontend — the permission store

### 9.1 Shape

```
permissions : Map<moduleKey, Map<permissionKey, bool>>
loaded      : bool
loading     : bool
failed      : bool
```

Exactly the payload of §7.1, stored as received. **O(1) lookup by two keys.**

Do not store an array of permission row objects and search it by name at call time. A linear
scan comparing an English sentence, run on every render of every gated element, is both slow
and fragile — a single character of drift in the sentence silently denies.

### 9.2 When it is fetched

Two triggers, both required:

1. **On login**, after the token is stored.
2. **On every application mount** — including a hard refresh and a new tab.

The second is what people forget. Fetching only at login means a user who refreshes the page
runs on whatever was cached at login, potentially days old, and an administrator's change never
reaches them until they log out and back in.

### 9.3 Where it is cached

Mirror the map into **session storage** so a refresh rehydrates instantly instead of flashing a
loading state, and set `loaded` from the presence of that mirror.

- **Session** storage, not local storage: it dies with the tab, which bounds how stale a cached
  grant can get.
- **Cleared on logout**, explicitly. A permission map left behind after logout is served to the
  next person who signs in on that machine, until the fetch completes.
- **Never** in a persisted store that survives across sessions.

### 9.4 Failure

On failure set `loaded = true` **and** `failed = true`, with an empty map.

Setting `loaded` on failure is deliberate: guards block on `loaded` (§11), so leaving it false
hangs the whole application on a spinner forever. An empty map plus fail-closed checks means
the user sees a minimal, safe UI.

But `failed` must then be **read and shown** — a visible "we could not load your permissions,
retry" banner. A `failed` flag that nothing renders produces a user staring at an app that has
silently lost every menu item, with no explanation and no way back.

### 9.5 Staleness — say it out loud

Permissions refresh on the next application mount. An administrator's change is **not**
instant for a user who is already signed in and stays on the page; it lands on their next
refresh or navigation that remounts the app.

This is an accepted trade-off, not an oversight. If a product needs immediate revocation, push
it over the existing notification channel and refetch — do not shorten the token, and do not
poll on a timer.

---

## 10. Frontend — the check helper

One function, used everywhere:

```
FUNC can(module, key) -> bool:
	RETURN STORE.permissions?[module]?[key] == true

FUNC permissionsLoaded() -> bool:
	RETURN STORE.loaded
```

`== true` matters: a missing module, a missing key, and an undefined value must all deny.
`IF permissions[module][key]` would throw on a missing module; `!= false` would grant on a
missing key.

Visibility permissions (§7.4) get their own named helpers so the inverted polarity is explicit
at the call site and cannot be copied by accident:

```
FUNC hideFundDetails() -> bool:
	RETURN STORE.permissions?["Visibility_Management"]?["can_view_fund_details"] == false
```

### 10.1 The gate component

For buttons, toolbars and sections inside a page the user *is* allowed to open:

```
COMPONENT PermissionGate(module, key, fallback = nothing, children):
	RETURN can(module, key) ? children : fallback
```

Use it for every affordance that leads to a call the user cannot make:

```
	PermissionGate("Expense_Management", "can_change_expense"):
		Button("Add Expense", onClick: openCreate)
		Button("Categories", onClick: openCategories)

	PermissionGate("Invoice_Management", "can_approve_invoice"):
		Button("Approve", onClick: approve)
```

**This is cosmetic only.** It removes a button; it does not protect anything. The route gate
(§6) is the control. Never let a gate component be the only thing standing between a user and
an action.

---

## 11. Frontend — route guarding

The nav filter (§12) stops a user *finding* a page. The route guard stops them *reaching* it —
by typed URL, bookmark, or a link someone pasted them.

```
COMPONENT PermissionRoute(module, key, anyOf = none):
	IF NOT permissionsLoaded():
		RETURN Spinner()                       # decide nothing until we know
	granted = anyOf
		? anyOf.some(c => can(c.module, c.key))
		: can(module, key)
	RETURN granted ? childRoutes() : NoPermissionPage()
```

Three requirements:

1. **Wait for `loaded` before deciding.** A guard that evaluates an empty map mid-fetch denies
   everyone for a moment — the user sees "no permission" flash and then the page appears, or
   worse, gets bounced to a fallback route before the map arrives.
2. **Decide during render, not in a post-render effect.** An effect-based redirect renders the
   protected page once first — its data fetches fire, its content paints, and only then does
   the redirect happen. That is a visible leak of the page you were protecting.
3. **Render a real denial**, not a silent redirect to the dashboard. A user bounced with no
   explanation files a bug; a user shown "You do not have access to this page" asks their
   administrator.

`anyOf` covers pages reachable through several permissions — a settings index that should open
if the user can see *any* of its sections.

Routes declare the requirement **as a wrapper around the route group**, so a section's pages
inherit one declaration:

```
	Route(guard: PermissionRoute("Expense_Management", "can_view_expense")):
		Route("/expenses",          ExpensesPage)
		Route("/expenses/:id",      ExpenseDetailPage)

	Route(guard: PermissionRoute("Purchase_Order_Management", "can_view_purchase_order")):
		Route("/purchase-orders",           PurchaseOrdersPage)
		Route("/purchase-orders/create",    PurchaseOrderCreatePage)
		Route("/purchase-orders/:id/detail", PurchaseOrderDetailPage)
```

Gate the **mutation** routes separately even when viewing is open:

```
	Route(guard: PermissionRoute("Project_Management", "can_change_project")):
		Route("/projects/new", ProjectCreatePage)
```

Where a page genuinely has no permission behind it, say so in a one-line comment on the route
so the next reader knows it is a decision rather than an omission.

---

## 12. Frontend — navigation filtering

**This is the section that prevents the failure this whole standard is about.** Everything else
can be right and the product still feels broken if the menu shows a page the user cannot open.

### 12.1 The menu is data with permission metadata

Never a hand-written list of links. A list of objects, each carrying what it needs to be
filtered:

```
navMain = [
	{ title: "Dashboard",  url: "/",          module: null,                        key: null,                        authOnly: false },
	{ title: "Projects",   url: "/projects",  module: "Project_Management",        key: null,                        authOnly: true  },
	{ title: "Customers",  url: "/customers", module: "Customer_Management",       key: null,                        authOnly: true  },
	{ title: "Activity",   url: "/activity",  module: "Activity_Log",              key: "can_view_activity_log",     authOnly: false },
]

navDocuments = [
	{ title: "Invoices",        url: "/invoices",        module: "Invoice_Management",        key: "can_view_invoice" },
	{ title: "Expenses",        url: "/expenses",        module: "Expense_Management",        key: "can_view_expense" },
	{ title: "Purchase Orders", url: "/purchase-orders", module: "Purchase_Order_Management", key: "can_view_purchase_order" },
	{ title: "Assets",          url: "/asset-registry",  module: "Asset_Management",          key: "can_view_asset" },
]
```

Field meanings:

| Field | Meaning |
|---|---|
| `module: null` | always visible — no permission governs it |
| `module` set, `key` set | visible only when that exact permission is `true` |
| `module` set, `key: null` | visible when **any** permission in that module is `true` — for a section whose backend routes are auth-only but which still belongs to a module |
| `authOnly: true` | the backend gates this section with the auth-only sentinel (§6.5), so any authenticated user of this surface may see it |

### 12.2 The filter

```
FUNC filteredNav():
	canSee = (module, key, authOnly) => {
		IF module == null: RETURN true
		IF authOnly AND isAuthenticated(): RETURN true
		modulePerms = STORE.permissions?[module]
		IF NOT modulePerms: RETURN false
		IF key != null: RETURN modulePerms[key] == true
		RETURN modulePerms.values().any(v => v == true)
	}
	RETURN {
		main:      navMain.filter(i => canSee(i.module, i.key, i.authOnly)),
		documents: navDocuments.filter(i => canSee(i.module, i.key, false)),
	}
```

Then render the filtered arrays.

### 12.3 Remove, do not disable

An item the user cannot use is **removed from the array**. Not rendered greyed out, not
rendered with a tooltip, not rendered at all.

A disabled menu item still tells the user the feature exists and still invites a click. A
removed one produces a navigation that honestly reflects what that person's job is.

### 12.4 An empty group renders nothing

If every item in a group is filtered out, the **group heading disappears too**:

```
COMPONENT NavGroup(title, items):
	IF count(items) == 0:
		RETURN nothing
	RETURN Section(title, items.map(renderItem))
```

Otherwise a user with none of Invoices, Expenses, Purchase Orders or Assets sees a bare
"Documents" heading with a void under it — which looks like a rendering failure.

### 12.5 Before and after

```
# Wrong — the failure this standard exists to prevent.
# Every user of this type sees every item; the backend then returns 403 or an
# empty list, and the user believes the product is broken or the data is missing.
menuItems = userType == "staff"
	? [ Dashboard, Training, Faculty, Officers, Expenses, Reports, Settings ]
	: [ MyTrainings, Exams ]
```

```
# Right — the menu is derived from the same grants the API enforces.
# A staff member without "can view expense" has no Expenses item at all.
menuItems = filteredNav().main
```

### 12.6 The one deliberate exception

A **settings index** — a page whose whole content is a list of links to sub-sections — may
render inaccessible rows disabled, with a lock icon, instead of removing them.

The reason is narrow and specific: if a user has access to one of eight settings sections,
filtering the other seven leaves a page with a single row that looks broken. Showing the full
list with locks communicates "this exists, you do not have it", which on an admin-facing
settings screen is the more useful message.

This applies to a settings index and nothing else. **The main navigation always filters.** Do
not use this as licence to disable-instead-of-remove elsewhere.

---

## 13. Frontend — denials, and what happens after

### 13.1 The interceptor

One place handles auth failures for every call:

| Response | Action |
|---|---|
| `401` "Session expired…" | clear stored credentials and the permission map, send the user to login with a message saying the session expired |
| `401` other | clear credentials, send to login |
| `403` on the bootstrap call (§7.1) | **do not redirect** — surface the retry state (§9.4) |
| `403` on any other call | show a denial the user can see |
| network error | a distinct "server unreachable" state, never conflated with a denial |

The bootstrap exclusion is not optional. Without it, a 403 while loading permissions triggers a
redirect, which remounts the app, which retries the bootstrap, which 403s — an infinite loop
that presents as a frozen browser tab.

### 13.2 A 403 must be visible

Logging a denial to the developer console is not handling it. From the user's side, the button
did nothing.

Every 403 produces something the user can see — a toast, an inline message, or a denial page —
saying they do not have access and who to ask.

### 13.3 When a 403 is itself a bug

If a user reaches a page through the menu and then gets a 403 from it, **the nav filter and the
route gate disagree** — the frontend thinks they may, the backend knows they may not. That is a
defect in this standard's terms, not a permissions problem to be solved by granting more.

Fix the mismatch: either the nav item is missing its permission metadata, or the route is gated
with a different permission than the one the page's data calls need.

---

## 14. Adding one permission, end to end

Example: **expenses**, currently open to everyone, must become permission-controlled.

1. **Migration** — `migrations/0104_insert_expense_permissions.sql`
   ```sql
   -- +migrate Up

   INSERT INTO permissions (name, description, module_name) VALUES
   	('can view expense',   'View the expense list and expense detail', 'Expense Management'),
   	('can change expense', 'Create, update and delete expenses',       'Expense Management')
   ON CONFLICT (name) DO NOTHING;

   INSERT INTO role_permissions (role_id, permission_id, permission)
   SELECT r.id, p.id, TRUE
   FROM roles r CROSS JOIN permissions p
   WHERE p.module_name = 'Expense Management'
   ON CONFLICT (role_id, permission_id) DO NOTHING;

   -- +migrate Down

   DELETE FROM role_permissions
   WHERE permission_id IN (SELECT id FROM permissions WHERE module_name = 'Expense Management');
   DELETE FROM permissions WHERE module_name = 'Expense Management';
   ```

2. **Backend routes** — `routers/expense.<ext>`
   ```
   	app.GET(expensePath, listExpenses, requirePermission("can view expense"))
   	app.GET(expensePath + "/:id", getExpenseById, requirePermission("can view expense"))
   	app.POST(expensePath, createExpense, requirePermission("can change expense"))
   	app.PATCH(expensePath + "/:id/update", updateExpense, requirePermission("can change expense"))
   	app.DELETE(expensePath + "/:id/delete", deleteExpense, requirePermission("can change expense"))
   ```

3. **Frontend nav** — add the metadata to the menu entry
   ```
   	{ title: "Expenses", url: "/expenses", module: "Expense_Management", key: "can_view_expense" }
   ```

4. **Frontend route guard**
   ```
   	Route(guard: PermissionRoute("Expense_Management", "can_view_expense")):
   		Route("/expenses", ExpensesPage)
   ```

5. **In-page gates** — the create and delete affordances
   ```
   	PermissionGate("Expense_Management", "can_change_expense"):
   		Button("Add Expense", onClick: openCreate)
   ```

6. **Verify, as a restricted role** — this is the step that catches everything:
   - switch `can view expense` off for a test role in the admin screen;
   - sign in as a user with that role;
   - the **Expenses item is absent from the menu**;
   - typing `/expenses` directly shows the no-permission page, not an empty list;
   - calling the API directly returns `403 {"success": false, "error": "Access denied"}`;
   - switch it back on, reload, and confirm all three reverse.

7. **Say what you changed** — the permission names, the routes gated, the nav entry filtered,
   and that existing roles were granted by default.

---

## 15. Anti-patterns — do not do these

| Anti-pattern | Do instead |
|---|---|
| Middleware written but attached to no route | every route carries a gate or the auth-only sentinel (§6.4) |
| Middleware querying a column that does not exist on the join table | the join column matches the migration exactly; verify with a real request, not by reading (§1) |
| A signing key hardcoded in the source | environment only, and abort at startup if unset (§5.2) |
| Falling back to a default or empty signing key | exit — an empty key means anyone can forge a token (§5.2) |
| Accepting whatever algorithm the token header claims | assert the algorithm family on parse (§5.3) |
| Embedding the permission list in the token | carry `role_id`; resolve per request so revocation works (§5.1) |
| Accepting `?token=` on every route | header only, query string on websocket upgrades alone (§5.4) |
| Expired and malformed both returning "Invalid token" | distinct messages — the client must tell them apart (§6.3) |
| Middleware returning a different response shape than controllers | one envelope across the whole API (§6.3) |
| Two queries per gate (name lookup, then join row) | one join, cached per request (§6.2) |
| `IF role.name == "Admin"` anywhere | `is_system` / grant rows — checks are data (§4.3) |
| A permission granted by a code branch instead of a row | every grant is a `role_permissions` row |
| Adding a permission without back-filling existing roles | both statements, always — otherwise it never appears in the admin screen (§3.3) |
| Revoking by deleting the `role_permissions` row | set `permission = false` (§4.2) |
| Creating a role without seeding its permission rows | one transaction, a row per permission (§4.1) |
| No `UNIQUE (role_id, permission_id)` | the constraint is required; the upsert depends on it (§1) |
| Applying a permission array one row at a time, uncommitted | one transaction for the whole array (§7.3) |
| A permission on the bootstrap endpoint | auth-only, or the user can never load their permissions (§7.1) |
| A permission seeded and shown as a toggle but enforced nowhere | enforce it or remove it — an inert toggle misleads the administrator (§3 audit) |
| A route gated with a permission that is not in the catalogue | permanently 403; the audit sweep catches this (Mode B) |
| Controllers re-checking the permission the gate already proved | trust the gate; one rule, one place (§8) |
| Re-querying the acting user at the top of every handler | fetch it only when you need its data (§8) |
| A row-scoping lookup that grants everything when it fails | fail closed — restrict on any resolution failure (§8.1) |
| Storing permissions as an array and scanning it by name | a two-level map, O(1) lookup (§9.1) |
| Fetching permissions only at login | on login **and** on every app mount (§9.2) |
| Permissions in storage that survives logout | session-scoped, cleared explicitly on logout (§9.3) |
| Leaving `loaded` false when the fetch fails | set `loaded` and `failed`; guards would hang forever (§9.4) |
| A `failed` flag nothing renders | show a retry the user can see (§9.4) |
| A route guard that decides before permissions load | wait for `loaded` (§11) |
| A guard that redirects from a post-render effect | decide during render, or the protected page paints first (§11) |
| Denial as a silent redirect to the dashboard | a real "no access" page (§11) |
| A menu item shown for a page the user cannot open | filter it out of the array (§12.3) |
| A menu item rendered disabled instead of removed | remove it — settings index is the only exception (§12.6) |
| An empty nav group still rendering its heading | render nothing (§12.4) |
| A sidebar built from a static list keyed on user type | metadata + filter, derived from the same grants the API enforces (§12.5) |
| `403` handled by logging to the console | a visible denial (§13.2) |
| A `403` redirect with no exclusion for the bootstrap call | exclude it, or you get an infinite reload loop (§13.1) |
| Reaching a page from the menu and getting a 403 | the two sides disagree — fix the mismatch, do not grant more (§13.3) |
| Removing a gate to make a failing call work | fix the grant or the permission name (Mode C) |
| A permission gated on the backend with no frontend counterpart | both sides, always — one side is an incomplete change (§2 of Part A) |
