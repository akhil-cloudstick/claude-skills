---
name: mobile-app
description: "Mobile app standard — convert a mobile-layout web design into a real Expo React Native app for iOS and Android. Works from a single self-contained index.html prototype or from a React web app laid out at phone width: strips the simulated device chrome, ports the CSS :root tokens 1:1 into a theme file, maps every screen to an Expo Router route, and rebuilds the UI with the same module structure as a Cloudhouse frontend. Covers the folder layout, router shells, web-to-native element mapping, navigation, state, the demo-or-real data decision, app identity and permissions. Use for ANY Expo work — converting a design, adding a screen or module to an existing app, or auditing one against the standard. Pairs with /cloudhouse:frontend. Invoked as /cloudhouse:mobile-app."
---

# Mobile App Skill — convert, build and audit to one fixed standard

You are working under a fixed house standard. **Part B of this file is the standard.**
It is not advice and not a starting point: it is the specification. Do not substitute your own
conventions, do not "improve" the layout, and do not follow a scaffolder's conventions where they
contradict Part B.

The app targets **iOS and Android together**. Not one and then the other: every screen is built so
that both platforms render it correctly, and a platform difference is handled where it occurs rather
than deferred.

One thing matters more than everything else in this file, so it is stated before the standard:

> **The design is a reference, not a source tree.** Nothing in the prototype is copied forward.
> The screens, the design tokens, the navigation and the data shapes are read out of it; the markup,
> the CSS and the simulated phone around it are not.

Read Part B in full before writing or changing a single file.

---

## 0. First — identify what you are converting from

Before asking the user anything:

1. **Find the design and identify its shape.** Three exist:
   - **A single `index.html` prototype** — hand-written HTML, CSS and vanilla JS, no build step.
     Screens are usually sibling elements toggled by a small navigation function rather than a
     router. This is the common case.
   - **A React web app laid out at phone width** — a real project whose layout is constrained to a
     phone-sized column. The component tree is worth reading; the width constraint is not.
   - **An existing Expo app** — then this is Mode B, C or D, and there is nothing to convert.
2. **Count the screens and name them.** In a single-file prototype they are the elements the
   navigation function shows and hides; in a React app they are the routed views. You need the list
   before the interview, because it is what the screen map (§3) is built from.
3. **Find the design tokens.** The `:root` custom property block, a theme file, or a Tailwind config.
   This becomes the token file (§4 of Part B) and it is read before any component is written.
4. **Find the hardcoded data.** Prototype fixtures — the arrays of records the screens render. These
   define the entity shapes, and in a demo build they are the data (§9 of Part B).
5. **Find the navigation model.** How the prototype pushes, replaces and goes back. It is the
   specification for the router (§8 of Part B), and reading it is faster and more accurate than
   inferring it from the screens.

State what you found in one line — the input shape, the screen count, whether a token block exists —
then continue.

---

## 1. Pick the mode

Read what the user typed after `/mobile-app` and choose one:

| The user asks for | Mode |
|---|---|
| "convert this design to a mobile app", "make this an Expo app", "build the app from this UI" | **A — Convert** |
| "add a screen / a module / a permission" to an app that exists | **B — Extend** |
| "update / check / review this mobile app" | **C — Audit** |
| anything else touching the mobile app (a bug fix, a tweak) | **D — Edit** |

If it is genuinely unclear, ask once, then proceed.

---

## 2. The interview — asked once

Ask these together, before writing anything. **Then stop asking and finish the job.** Do not return
with another question between every file.

1. **Where does the app go?** Offer `mobile/` beside the design as the default — it keeps the
   prototype next to the app, so any screen can be diffed against the thing it was ported from — but
   ask, and accept whatever folder the user names.

   **Never convert the design folder in place.** The prototype is the approved visual reference and
   the only record of what the app is supposed to look like. Once it is gone, "does this match?" has
   no answer.

2. **Demo data, or the real API?** Exactly two options, and the answer applies to the whole app:

   - **Demo** — every module carries its fixtures, ported from the prototype. No HTTP client, no
     services, no network call anywhere. The app runs correctly on first install with nothing behind
     it, which is what makes it demonstrable.
   - **Real API** — every module carries a service, and the data layer is `/cloudhouse:frontend` §6,
     §7 and §9 as written. No demo fixtures anywhere in the tree. This needs the development and
     production base URLs.

   Say in one line that this is not a switch to be flipped later: changing it means writing the
   other half across every module, so it is worth answering deliberately. **Never build both.**

3. **App identity** — the display name, the slug, the deep-link scheme, and the bundle identifier
   used for iOS and Android.

4. **Device capabilities.** Read these off the screens rather than asking cold — a map screen needs
   location, a photo field needs the camera and the library, an attachment field needs documents —
   then confirm the list in one line. Each one becomes a permission declaration *and* a usage
   description (§10 of Part B), and a missing usage description is a store rejection rather than a
   bug you can find by testing.

---

## 3. Mode A — Convert a design into an Expo app

### 3.1 Produce the screen map first

Before writing code, write the map and get it approved. It is the one artifact that makes a
conversion reviewable, and it takes a minute:

| Design screen | Route | Page file | Module |
|---|---|---|---|
| `view-leads` | `src/app/(tabs)/leads.<ext>` | `modules/leads/pages/LeadsPage.<ext>` | `leads` |
| `view-lead-detail` | `src/app/lead/[id]/index.<ext>` | `modules/leads/pages/LeadDetailPage.<ext>` | `leads` |

Include every screen found in §0.2, and name the modules while you are there — a module is a product
area, not a screen (`/cloudhouse:frontend §2.1`). Overlays, sheets and modals are **not** screens;
they are components inside the screen that opens them, and listing them as routes produces a router
full of things that are not pages.

Say in one line which screens become tabs, which become pushed screens, and which are modals.

### 3.2 Then build, in this order

Each step is what the next one consumes:

**tokens → primitives → router skeleton → module types → data layer (demo *or* services) → stores →
components → pages → router shells → app identity and permissions.**

Tokens first is not arbitrary. Every component below them reads from the token file, and a component
written against colour literals has to be rewritten rather than adjusted.

Build one module at a time, all the way through, and confirm it typechecks before starting the next.
Never scaffold ten modules and then try to make them compile together.

---

## 4. Mode B — Extend an existing Expo app

The structure is settled. Change only what was asked for, and match what is already there.

- **Adding a screen.** Module page first, then the router shell — never the other way round, because
  a screen written in the router folder is a screen that has to be moved later (§3 of Part B). If it
  belongs to an existing module, it goes in that module; if it is a new product area, it is a new
  module with the full set of folders.
- **Adding a module.** The same order as a conversion: types → data → store → components → pages →
  route. Register its slice in the root store.
- **Adding a device capability.** The permission declaration, the usage description and the runtime
  request are three separate things and all three are required. Declaring it without requesting it
  fails at runtime; requesting it without declaring it fails at review.
- **Changing a visual detail.** Check the design first. If the app and the design disagree, say which
  one is wrong in one line before changing either (§5.1).

---

## 5. Mode C — Audit an existing Expo app

Do **not** change anything until the user approves.

### 5.1 The sweeps

Run all of them. Each names the failure it catches — report findings in those terms, not as a style
preference.

**(a) Device chrome carried over.** Search for a fixed device width, a bezel, a notch element, a
hand-drawn status bar or a home-indicator bar. All of it is prototype scaffolding. On a real phone it
draws a picture of a phone inside the phone (§5 of Part B).

**(b) Style literals in components.** A colour, a radius or a spacing value written inline instead of
read from the token file. Each one is a value that will not move when the design does.

**(c) Real screens in the router folder.** A route file containing markup, state or data fetching. It
cannot be reused, it cannot be tested apart from its route, and it breaks the module boundary (§3).

**(d) Demo and real data both present.** Fixtures alongside services, a component importing a fixture
directly, or a runtime flag choosing between them. One or the other, decided once (§9).

**(e) A hostname outside the HTTP client.** `/cloudhouse:frontend §6` — one base URL, one file.

**(f) Web idioms that silently do nothing.** `className`, `position: fixed`, hover styles, `cursor`,
percentage height chains, `z-index` with no elevation. None of these error; they are simply ignored,
so the layout is subtly wrong and nothing in the build says so.

**(g) Unsafe layout.** Content under the notch or the home indicator, no safe-area handling, or a
form screen with no keyboard avoidance — on a small device the keyboard covers the field being typed
into and the user cannot see what they are entering.

**(h) Touch targets below 44pt.** Ported from a design drawn for a mouse pointer. It is technically
tappable and practically not.

**(i) An unbounded list rendered by mapping inside a scroll view.** Every row is created at once; the
screen takes seconds to open and the memory does not come back.

**(j) Manifest gaps.** A capability used in code with no permission declaration, or a permission with
no usage description.

**(k) Comments.** Multi-line explanatory blocks, usually inherited from a scaffolder (§12).

**(l) Fidelity drift.** The screen no longer matches the design. Diff against the prototype, which is
why it was kept.

### 5.2 Report and ask

1. Write the findings in one table, most severe first:

   | # | File | Rule broken (§) | What is wrong | Fix |
   |---|---|---|---|---|

2. Group them into: **(a) mechanical** — naming, import order, comments, style literals;
   **(b) structural** — moving screens out of the router folder, extracting a module, splitting a
   page; **(c) behavioural** — device chrome, unsafe layout, mixed data sources, a hostname in a
   component, a missing permission, a list that will not scale.

3. Then ask the user, with the counts filled in:

   > Found N violations: X mechanical, Y structural, Z behavioural.
   > 1. Fix everything (structural moves included)
   > 2. Fix behavioural + mechanical only, leave the module structure as it is
   > 3. Fix a specific list I give you
   > 4. Leave it as is — report only
   >
   > Which one?

4. Apply only what was chosen. Behavioural fixes first — they are the ones costing something today.
   Structural moves go **one module at a time**, and the app must typecheck and still run after each.

5. Re-run the self-check (§7) and report what is now compliant and what the user chose to leave.

---

## 6. Mode D — Edit

Small change, same rules. Before editing a file, check whether it already follows Part B. If it does
not, fix the part you are touching to be compliant, mention the rest in one line, and do not silently
spread the old pattern.

In particular: if you need a colour and the token file does not have it, **add it to the token
file** — do not write the hex inline because the component next to it does. That one shortcut is
what makes the next design change a search-and-replace across the whole app instead of an edit to
one file.

---

## 7. Self-check — run before saying you are done

- [ ] The design is untouched and still sits beside the app (§2)
- [ ] Every screen in the map has a route, and every route resolves to a module page (§3.1, §3)
- [ ] **No route file contains markup, state or data fetching** (§3)
- [ ] **No device frame, notch, fake status bar or fixed device width in the app** (§5)
- [ ] Every colour, radius and spacing value comes from the token file (§4)
- [ ] Tokens match the design's values one for one (§4)
- [ ] Every string is inside a text element (§6)
- [ ] Unbounded lists use a virtualised list, not a mapped scroll view (§6)
- [ ] Safe-area insets handled; forms avoid the keyboard (§7)
- [ ] Touch targets are at least 44pt (§6)
- [ ] **The app has demo data or services, never both** (§9)
- [ ] If real: the base URL appears in exactly one file, and the dev/prod flag is correct (§9)
- [ ] Every capability used in code is declared **and** carries a usage description (§10)
- [ ] Icons, splash and images are local assets, not remote URLs (§10)
- [ ] Typecheck is clean, and the build script runs it (§11)
- [ ] No comment longer than one line, and none that restates the code (§12)
- [ ] **The app runs on both iOS and Android**, and every screen was checked on both
- [ ] Each screen was diffed against the design before being called done (§13)

---

## 8. Non-negotiables

1. **The design survives.** It is never converted in place, never edited to match the app.
2. **The design is read, not copied.** No markup, no CSS and no device frame comes forward.
3. **`src/app/` holds shells.** Every real screen lives in a module.
4. **One token file.** No style literal in any component.
5. **Demo or real, never both.** Decided once, applied everywhere.
6. **One base URL, one file** — `/cloudhouse:frontend §6`.
7. **A module owns its pages, components, services, store and types** —
   `/cloudhouse:frontend §2`.
8. **Both platforms, every screen.** A screen checked on one platform is not done.
9. **Every capability is declared with a usage description.**
10. **Write Expo code against the pinned SDK's documentation**, never from memory.

If the user explicitly asks for something that breaks a rule, say which rule in one sentence, then do
what they asked.

## 9. Staying on the standard for the whole session

This standard applies to every later message in the conversation, not only the one that invoked
`/mobile-app`. Before each new file you write or edit, re-check section 7. If the conversation has
been long, re-read the relevant section of Part B rather than working from memory.

---
---

# PART B — THE STANDARD

Everything below this line is the specification. Follow it exactly.

# Mobile Application Structure & Conversion Standard (Expo, iOS and Android)

This document defines how a mobile-layout web design becomes a real mobile application — what is
read out of the design and what is discarded, how the project is organised, how every screen and
element maps from the web to the native equivalent, how the app navigates, where its data comes from,
and what it declares about itself to the two app stores.

It is the single source of truth. When something is not covered here, copy the closest pattern in
this document rather than inventing a new one, and then add the new pattern here.

Read §2–§6 before your first file. §4 and §9 are the two you will come back to.

### How to read the examples

```
SCREEN Name:                  a screen the user navigates to
COMPONENT Name(props):        a UI component
SERVICE name:                 a module's API service
STORE name:                   a store slice
FUNC name(args) -> type:      a plain function
TOKEN group.key = value       a design token
ROUTE path -> Page            a router entry
RENDER: ...                   the UI the component produces
```

Folder trees, file names and token names are **literal**. Everything else is a shape to translate
into the project's version of React Native.

---

## 1. Stack baseline

The renderer conventions are an ordinary Cloudhouse frontend and follow `/cloudhouse:frontend` in
full — that skill wins on the module layout, file naming, in-file ordering, the HTTP client,
services, stores, and page and component anatomy, and this document does not restate them. What this
document adds is fixed:

- **Expo and React Native**, with the SDK version pinned in the manifest. Say which one in one line
  before writing code.
- **TypeScript, strict.** The build typechecks before it bundles. A type error that reaches a phone
  cannot be hot-fixed the way a website can — it needs a new build and, for a store release, a new
  review.
- **Expo Router**, file-based. The router folder holds shells (§3).
- **A path alias to the source root**, configured in the TypeScript config and honoured by the
  bundler, and identical between them.
- **One state container**, with typed hooks, per `/cloudhouse:frontend §9`.
- **Stylesheet objects plus a token file.** No utility-class library, no styled-components.
- **House-built UI primitives** in `common/components/ui/`. **No third-party React Native UI kit.**
  A kit ships its own visual language, and every screen then becomes an argument between the kit's
  idea of a button and the approved design's. Building the ten primitives the design actually uses
  is faster than overriding a hundred you did not choose.

> **Expo changes fast. Read the versioned documentation for the SDK the project is pinned to before
> writing any code** — `https://docs.expo.dev/versions/v<SDK>/`. Navigation, the asset pipeline, the
> config format and half the module APIs have all changed shape across recent majors. An answer from
> memory is an answer about a different SDK, and it will typecheck.

Whatever a scaffolder produces is **rearranged to match §2 and stripped of its comments (§12)**
before it is committed. The scaffolder is a typing shortcut, not the layout authority.

---

## 2. Folder structure

The modular layout of `/cloudhouse:frontend §3.2`, unchanged, plus the router folder and two mobile
additions. Only the deltas are shown here — read that section for the rest:

```
<app>/
├── app.json                              identity, permissions, plugins, icons (§10)
├── <dependency manifest>
├── <typescript config>                   the path alias lives here
├── .env.example                          committed, empty values
│
├── assets/
│   └── images/                           icon, splash, logo — real files (§10)
│
└── src/
	├── app/                              ROUTER SHELLS ONLY — 1–3 lines each (§3)
	│   ├── _layout.<ext>                 providers and the root navigator
	│   ├── index.<ext>
	│   ├── (tabs)/
	│   │   ├── _layout.<ext>             the tab bar
	│   │   └── <tab>.<ext>
	│   └── <feature>/[id]/index.<ext>
	│
	├── common/
	│   ├── components/
	│   │   ├── ui/                       house-built primitives, generic
	│   │   └── layout/                   headers, tab bar, screen container
	│   ├── config/appConfig.<ext>        app-wide constants
	│   ├── services/httpClient.<ext>     REAL-API BUILDS ONLY — the only file with a base URL
	│   ├── theme/
	│   │   ├── tokens.<ext>              ported 1:1 from the design (§4)
	│   │   └── shadows.<ext>             elevation is platform-split (§4)
	│   ├── hooks/  types/  utils/
	│
	├── modules/<feature>/
	│   ├── pages/  components/  services/  store/  types/
	│   └── demo/                         DEMO BUILDS ONLY (§9)
	│
	└── store/                            the store instance and typed hooks
```

Rules, in addition to `/cloudhouse:frontend §3.3`:

- **`src/app/` mirrors the URL, and nothing else.** Its shape is dictated by the router, so it is the
  one folder whose layout is not ours to choose — which is exactly why no real code lives there.
- **`theme/` is one folder with two files.** Not a theme per screen, not tokens beside components.
- **`demo/` and `services/` never coexist** in the same app (§9).

---

## 3. `src/app/` holds shells, not screens

This is `/cloudhouse:frontend §3.4` applied to Expo Router, and it matters more here because the
router folder's structure is imposed from outside.

A route file is one line:

```
export { default } from "@/modules/leads/pages/LeadsPage"
```

- **No markup, no state, no data fetching, no styles** in a route file.
- The real screen is `modules/<feature>/pages/<Feature>Page`, named and shaped per
  `/cloudhouse:frontend §4` and §10.
- **`_layout` files are the exception.** They hold navigation configuration — the navigator, its
  screen options, the tab bar, the providers at the root — and nothing else. A `_layout` that fetches
  data has taken a page's job.
- A screen written directly into the router folder cannot be reused from anywhere, cannot be reached
  except through its route, and puts one product area's code outside the module that owns it.

---

## 4. Design tokens, ported 1:1

The design's custom properties — its `:root` block, theme file or config — become one token file.

```
TOKEN colors.brand    = "#153E9E"        # the design's --brand, unchanged
TOKEN radius.card     = 16
TOKEN spacing.screenX = 20
TOKEN sizes.control   = 38
```

Groups: `colors`, `radius`, `spacing`, `sizes`, `fontSize`, `fontWeight`. Shadows live in their own
file because elevation is platform-split.

- **Ported 1:1 — same values, same names.** What the design calls `--brand` is `colors.brand`. A
  renamed or "tidied" token makes the two impossible to diff, which defeats keeping the design.
- **No colour, radius, spacing or font-size literal in any component.** If a value is not in the
  token file, it is not in the design, and the fix is to add it to the token file — not to write it
  inline (§ Mode D).
- **Convert units honestly.** React Native has no `rem`, no `em`, no `vh` and no `%` for most
  properties: everything is a unitless density-independent number. A design in `px` converts
  directly; anything relative has to be resolved to a number at conversion time, once, rather than
  guessed at per component.
- **Shadows are two implementations of one token.** iOS takes colour, offset, opacity and radius;
  Android takes an elevation number. One shadow helper exposing named levels, used everywhere — never
  a hand-written shadow per component, which is how the same card ends up looking different on two
  screens.
- A design with a dark mode has two colour sets behind one accessor, decided at this step. Retrofit
  is a rewrite of every stylesheet.

---

## 5. Strip the device chrome

A mobile design shown on a desktop draws its own phone around itself: a bezel, a notch, a status bar
reading a fixed time with fake signal and battery icons, a home-indicator bar, and a fixed frame
centred on a backdrop.

**None of it is application UI.** The real device supplies every one of those things.

Ported forward, the result is a picture of a phone drawn inside a phone, inset from the real edges,
with a second status bar under the real one. It is the single most common failure in this conversion
and it is immediately visible to anyone who opens the app.

Delete the frame. Replace it with the real equivalents:

| Prototype | The app |
|---|---|
| bezel, rounded outer frame, fixed `<width>×<height>` | a full-bleed screen, sized by the device |
| notch element | the safe-area inset at the top |
| hand-drawn status bar | the platform status bar, styled per screen |
| home-indicator bar | the safe-area inset at the bottom |
| the desktop backdrop the phone sits on | nothing |

**Safe-area insets are not padding constants.** They differ per device and per orientation, and they
are read from the platform, never hardcoded to the numbers that happened to look right on one phone.

---

## 6. Web → native element mapping

The table that does most of the conversion work. The third column is the reason it matters, and it is
the part people skip.

| Web | Native | Why it matters |
|---|---|---|
| `div` | a view | **no cascade.** Styles do not inherit; every element carries its own |
| `span`, `p`, `h1`–`h6` | a text element | **every string must be inside one**, or it throws at runtime |
| `img` | an image element | needs explicit dimensions; there is no intrinsic sizing to fall back on |
| `button`, `a`, clickable `div` | a pressable | **44pt minimum target**, and the press feedback is yours to provide |
| `input`, `textarea` | a text input | choose the keyboard type, the return key and the autocomplete per field |
| `select` | a sheet or a picker | there is no native `select`; a dropdown has to be built |
| a scrolling container | a scroll view | fixed, bounded content only |
| a long or unbounded list | a virtualised list | a mapped scroll view builds **every** row up front |
| a fixed bottom tab bar | the tab navigator, custom bar | §8 |
| an overlay or dialog | a modal, or a sheet primitive | overlays are components, not routes (§3.1 of Part A) |
| inline `svg` | the SVG library | **one icon component with a name union** — not a file per glyph |
| `:hover` | nothing | there is no hover; the affordance must be visible without it |
| CSS transition or keyframes | the animation library | declare it; there is no implicit transition |

On the icon rule specifically: a prototype's icons are usually dozens of inline SVG paths. They
become one component taking a name from a union type, so every icon is one call, the set is
discoverable through the type, and a missing icon is a compile error rather than a blank space.

---

## 7. What has no equivalent

The failures a literal port produces, none of which error:

- **No cascade and no inheritance.** A font set on a container does not reach its children.
- **No percentage height chain.** `height: 100%` through five ancestors becomes `flex: 1`.
- **No fixed positioning.** An element pinned to the viewport is an absolutely positioned child of
  the screen container instead.
- **No hover, no focus ring, no cursor.** A control whose only affordance is hover is invisible on a
  phone and must be given a real one.
- **Stacking needs elevation on Android.** A raised element ordered only by `z-index` renders behind
  its neighbours there while looking correct on iOS.
- **The keyboard covers the screen.** A form has to move out of its way; nothing does this by
  default, and a field at the bottom of a screen is unusable without it.
- **Text does not wrap around anything**, and it truncates rather than reflowing — long values need
  an explicit line limit and an explicit behaviour.
- **Platform differences are normal, not bugs.** Shadows, fonts, the back gesture and safe areas all
  differ. Handle the difference where it occurs; do not try to make one platform impersonate the
  other.

---

## 8. Navigation

The router mirrors the design's navigation model, which was read in §0.5 and is a specification
rather than a hint.

- **The bottom bar becomes a tab navigator**, with a custom bar component when the design's bar is
  not the platform default — which it usually is not.
- **Anything that pushes becomes a stack screen.** A detail view takes a dynamic segment; the record
  is loaded from the segment, not passed as an object, so the route is shareable and survives a
  reload.
- **Anything that replaces without a back step replaces**, and is not pushed. Getting this backwards
  produces a back stack that grows forever and a back gesture that walks the user through screens
  they already dismissed.
- **Overlays, sheets and modals are components**, owned by the screen that opens them. They are not
  routes. A router full of sheets is a router that cannot tell you what the app's screens are.
- The navigator's configuration lives in `_layout` files (§3), never scattered through screens.

---

## 9. Data — demo or real, never both

The decision from the interview (§2 of Part A), applied everywhere without exception.

### 9.1 A demo build

- Fixtures live in `modules/<feature>/demo/demo-<entity>`, ported from the design's hardcoded data.
- Stores seed from the fixtures. Components read the store, exactly as they would with a real API,
  so the structure does not change when one is added later.
- **There is no HTTP client, no `services/` folder and no network call anywhere in the app.**

### 9.2 A real-API build

- `/cloudhouse:frontend` §6, §7 and §9 as written: one HTTP client holding the only base URL and the
  development/production switch as its first statement; one service per entity owning every path for
  it; slices that call services and never the client.
- Two deltas from the web version, and only two:
  - **The transport is `fetch` with an explicit timeout.** There is no browser XHR client here, and
    without a timeout a request against an unreachable host on a mobile network hangs until the OS
    gives up, which can be minutes.
  - **The token lives in secure device storage**, not in web storage. It is an asynchronous read, so
    the client's header construction is asynchronous too.
- **There are no demo fixtures anywhere in the tree.**

### 9.3 Why not both

A build that carries both grows a runtime flag choosing between them, and from then on every screen
has two behaviours, only one of which is ever tested. Worse, a component that reaches a fixture
directly renders plausible data in production, forever, and no build, typecheck or test ever fails.

If demo data is genuinely wanted inside a real build — a seeded account, a screenshot mode — it is a
separate, deliberate request, and it is built as one named thing rather than as a flag threaded
through every module.

---

## 10. App identity, permissions and assets

The app manifest carries the display name, the slug, the scheme, the bundle identifier, the
orientation, the icons, the splash screen and the plugins.

- **Every capability used in code is declared, and every declaration carries a usage description.**
  Android needs the permission strings; iOS needs a purpose string per capability, written in plain
  language that says what the app does with it. A missing or lazy purpose string is a store
  rejection — a failure that arrives days later, from a reviewer, not from a build.
- **Request at the point of use, not at launch.** A permission prompt on first open, before the user
  has seen why, is the most common reason a permission is denied permanently.
- **Handle the denial.** Every capability needs a path for the user who said no, and for the user who
  said no and cannot be asked again.
- **Assets are local files.** A design that loads its logo from a URL does not survive into the app:
  the icon, the splash and the brand images are real files in `assets/`, in the sizes the platforms
  require.
- **The identity values are decided once** (§2 of Part A). The bundle identifier in particular cannot
  be changed after the first store submission without shipping a different app.

---

## 11. Commands

`start` · `android` · `ios` · `typecheck` · `lint` · `build`.

- **`typecheck` must be clean before any build**, and the build script runs it first. A phone build
  that ships a type error costs a new build and, on a store track, a new review.
- `android` and `ios` are both expected to work from day one. An app that has only ever been started
  on one platform has never been tested on the other, whatever the code suggests.

---

## 12. Formatting and comments

`/cloudhouse:frontend §5` in full — the import order, the module-level order, the order inside a
component, tabs, and the naming rules. In particular:

- **Comments: 0–1 lines, and mostly none.** The default is to write no comment. Write one only where
  the reason is genuinely not visible in the code — a business rule, a workaround, a unit, a warning.
  **One line is the hard maximum.** Never two, never a paragraph, never a block above a function. If
  a comment needs more than one line, the code needs a better name instead.
- **Cross-reference the design where a value must stay in sync.** A token or a status list ported
  from the prototype gets a one-line comment naming what it mirrors. This is the one comment habit
  that is required, because it is what makes the next diff possible.
- Generated Expo scaffolding arrives full of explanatory blocks. They are stripped before the commit,
  not inherited.
- A stylesheet belongs at the bottom of the file it styles, after the component, in one object.

---

## 13. Converting a design — end to end

1. **Read the design** — screens, tokens, data, navigation (§0 of Part A).
2. **Settle the interview** — location, demo or real, identity, capabilities (§2 of Part A).
3. **Write the screen map** and get it approved (§3.1 of Part A).
4. **Create the project** in the agreed folder, pinned to a named SDK (§1).
5. **Port the tokens** — 1:1, before any component (§4).
6. **Build the primitives** the design actually uses, and the icon component (§1, §6).
7. **Lay out the router skeleton** — layouts and empty shells, so navigation is walkable early (§3).
8. **Per module, in order**: types → data (fixtures *or* service) → store → components → pages →
   route shell. Typecheck before starting the next module (§2, §9).
9. **Strip anything that came from the device frame** (§5).
10. **Fill in the manifest** — identity, capabilities, usage descriptions, icons, splash (§10).
11. **Run on both platforms**, every screen (§11).
12. **Diff each screen against the design**, and fix the app rather than the design (§5.1 of Part A).
13. **Run the self-check** (§7 of Part A) and report what was built, module by module.

---

## 14. Anti-patterns — do not do these

| Anti-pattern | Do instead |
|---|---|
| Converting the design folder in place | build beside it; the design survives (§2 of Part A) |
| Editing the design so it matches the app | fix the app; the design is the reference (§5.1 of Part A) |
| The bezel, notch or fake status bar ported forward | delete the frame; use safe-area insets (§5) |
| A fixed device width in the app | full bleed, sized by the device (§5) |
| Safe-area insets hardcoded to one phone's numbers | read them from the platform (§5) |
| A colour or radius literal in a component | add it to the token file and read it (§4) |
| Tokens renamed or "tidied" during the port | 1:1 with the design, or it cannot be diffed (§4) |
| A real screen implemented in the router folder | a module page, re-exported by a one-line route (§3) |
| A `_layout` that fetches data | layouts hold navigation configuration only (§3) |
| Every overlay and sheet registered as a route | they are components of the screen that opens them (§8) |
| A string rendered outside a text element | wrap it, or it throws at runtime (§6) |
| An unbounded list mapped inside a scroll view | a virtualised list (§6) |
| A file per SVG icon | one icon component with a name union (§6) |
| `className`, `position: fixed` or hover styles | they are silently ignored; use the native equivalent (§7) |
| A percentage height chain | `flex: 1` (§7) |
| A raised element ordered by `z-index` alone | add elevation, or Android renders it behind (§7) |
| A form screen that ignores the keyboard | move the content out of its way (§7) |
| A touch target under 44pt | size it for a fingertip (§6) |
| Demo fixtures and services in the same app | one or the other, decided once (§9) |
| A component importing a fixture directly | it reads the store (§9) |
| A hostname outside the HTTP client | one base URL, one file (§9, `/cloudhouse:frontend §6`) |
| A capability requested with no usage description | declare it and say why, or the store rejects it (§10) |
| A permission prompt on first launch | ask at the point of use (§10) |
| A remote URL for the logo or icons | local asset files (§10) |
| A third-party UI kit fighting the approved design | build the primitives the design uses (§1) |
| Testing on one platform and shipping both | every screen, on both (§11) |
| Writing Expo code from memory | read the pinned SDK's documentation first (§1) |
