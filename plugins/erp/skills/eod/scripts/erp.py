#!/usr/bin/env python3
"""Cloudhouse ERP end-of-day CLI.

Dependency-free wrapper around the ERP API used by the /erp:eod skill.
Every command prints a single JSON object: {"ok": true, ...} or {"ok": false, "error": "..."}.
"""

import argparse
import getpass
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".cloudhouse-eod.json")

# The ERP API, as the Project-Management-System frontend defines it
# (src/services/EventServices.ts). Only login asks for credentials; the URL is fixed.
PRODUCTION_URL = "https://api.cloudhousetechnologies.com"
DEVELOPMENT_URL = "http://localhost:8085"
TOKEN_MAX_AGE = 71 * 3600  # server issues 72h tokens; refresh a little early

VALID_STATUSES = [
    "Todo",
    "In Progress",
    "Backend",
    "Front-end",
    "Testing",
    "Review",
    "Completed",
]


# --------------------------------------------------------------------------- output


def emit(payload, code=0):
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    sys.exit(code)


def fail(message, **extra):
    payload = {"ok": False, "error": message}
    payload.update(extra)
    emit(payload, 1)


# --------------------------------------------------------------------------- config


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        fail("Could not read %s: %s" % (CONFIG_PATH, exc))


def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2)
        try:
            os.chmod(CONFIG_PATH, 0o600)
        except OSError:
            pass  # some Windows filesystems do not support it
    except OSError as exc:
        fail("Could not write %s: %s" % (CONFIG_PATH, exc))


def require_config():
    config = load_config()
    if not config.get("base_url") or not config.get("token"):
        fail("Not logged in. Run: py erp.py login")
    return config


# --------------------------------------------------------------------------- http


def request(method, url, token=None, body=None, content_type=None, timeout=60):
    """Perform one HTTP call. Returns (status, parsed_body_or_text)."""
    req = urllib.request.Request(url, data=body, method=method)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if content_type:
        req.add_header("Content-Type", content_type)
    req.add_header("Accept", "application/json")

    context = ssl.create_default_context() if url.lower().startswith("https") else None
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.getcode()
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status = exc.code
    except urllib.error.URLError as exc:
        fail("Cannot reach %s: %s" % (url, exc.reason))
    except OSError as exc:
        fail("Network error calling %s: %s" % (url, exc))

    try:
        return status, json.loads(raw) if raw else {}
    except ValueError:
        return status, {"raw": raw}


def html_to_text(value):
    """ERP descriptions come from a rich-text editor, so they arrive as HTML."""
    if not value:
        return ""
    text = value
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|pre|h[1-6]|tr)>", "\n", text)
    text = re.sub(r"(?i)<li[^>]*>", "\n- ", text)
    text = re.sub(r"(?i)</li>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace(" ", " ").replace("•", "-")
    lines = [line.rstrip() for line in text.splitlines()]
    out, blank = [], False
    for line in lines:
        if line.strip():
            out.append(line.strip())
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def json_body(payload):
    return json.dumps(payload).encode("utf-8"), "application/json"


def multipart_body(fields, files=None):
    """Build a multipart/form-data body. fields: dict of str->str. files: list of paths."""
    boundary = "----cloudhouse-eod-" + uuid.uuid4().hex
    out = bytearray()
    for name, value in fields.items():
        out += ("--%s\r\n" % boundary).encode()
        out += ('Content-Disposition: form-data; name="%s"\r\n\r\n' % name).encode()
        out += value.encode("utf-8") + b"\r\n"
    for path in files or []:
        filename = os.path.basename(path)
        try:
            with open(path, "rb") as handle:
                content = handle.read()
        except OSError as exc:
            fail("Cannot read attachment %s: %s" % (path, exc))
        out += ("--%s\r\n" % boundary).encode()
        out += (
            'Content-Disposition: form-data; name="files"; filename="%s"\r\n' % filename
        ).encode()
        out += b"Content-Type: application/octet-stream\r\n\r\n"
        out += content + b"\r\n"
    out += ("--%s--\r\n" % boundary).encode()
    return bytes(out), "multipart/form-data; boundary=" + boundary


# --------------------------------------------------------------------------- auth


def do_login(base_url, email, password):
    body, ctype = json_body({"email": email, "password": password})
    status, data = request(
        "POST", base_url.rstrip("/") + "/api/v1/login", body=body, content_type=ctype
    )
    if status != 200:
        fail("Login failed (HTTP %s)" % status, response=data)
    response = data.get("response") or {}
    if not response.get("token"):
        fail("Login response had no token", response=data)
    return response


def store_session(config, response, email=None, password=None, base_url=None):
    if base_url:
        config["base_url"] = base_url.rstrip("/")
    if email is not None:
        config["email"] = email
    if password is not None:
        config["password"] = password
    config["user_id"] = response.get("id")
    config["full_name"] = response.get("full_name")
    config["role"] = response.get("role")
    config["access"] = response.get("access")
    config["user_type"] = response.get("userType")
    config["token"] = response.get("token")
    config["token_saved_at"] = int(time.time())
    save_config(config)
    return config


def refresh_if_stale(config):
    """Re-login when the stored token is close to its 72h expiry."""
    age = int(time.time()) - int(config.get("token_saved_at") or 0)
    if age < TOKEN_MAX_AGE:
        return config
    if not config.get("password"):
        fail("Token expired and no saved password. Run: py erp.py login --update")
    response = do_login(config["base_url"], config["email"], config["password"])
    return store_session(config, response)


def authed(method, path, config, body=None, content_type=None):
    """Call an authenticated endpoint, retrying once after a fresh login on 401."""
    url = config["base_url"].rstrip("/") + path
    status, data = request(
        method, url, token=config.get("token"), body=body, content_type=content_type
    )
    if status == 401 and config.get("password"):
        response = do_login(config["base_url"], config["email"], config["password"])
        config = store_session(config, response)
        status, data = request(
            method, url, token=config["token"], body=body, content_type=content_type
        )
    return status, data, url


def prefix(config, kind):
    """Path prefix for the logged-in role.

    kind 'agent'   -> the agent/tasks tree
    kind 'subtask' -> subtask reads and writes
    """
    user_id = config.get("user_id")
    if config.get("user_type") == "staff":
        return "/api/v1/staff/%s" % user_id
    if kind == "agent":
        return "/api/v1/user/%s" % user_id
    return "/api/v1/employee/%s" % user_id


# --------------------------------------------------------------------------- commands


def cmd_login(args):
    config = load_config()
    fresh = args.update or not config.get("token")

    if fresh:
        if args.url:
            base_url = args.url
        elif args.dev:
            base_url = DEVELOPMENT_URL
        else:
            base_url = PRODUCTION_URL
        print("ERP: %s" % base_url)
        if config.get("email") and args.update:
            print("Signed in as %s - enter a different email to switch account."
                  % config["email"])
        default_email = config.get("email") or ""
        if args.email:
            email = args.email.strip()
            print("Email: %s" % email)
        else:
            prompt_email = "Email%s: " % (" [%s]" % default_email if default_email else "")
            email = input(prompt_email).strip() or default_email
        if not email:
            fail("Email is required")
        if sys.stdin.isatty():
            password = getpass.getpass("Password: ")
        else:
            # piped input (scripted runs): read the password from the next line
            password = sys.stdin.readline().rstrip("\n")
        if not password:
            fail("Password is required")
        response = do_login(base_url, email, password)
        config = store_session(
            config, response, email=email, password=password, base_url=base_url
        )
    else:
        config = refresh_if_stale(config)

    if args.as_staff:
        body, ctype = json_body({"staff_id": int(args.as_staff)})
        path = "/api/v1/user/%s/staff/login" % config.get("user_id")
        status, data, url = authed("POST", path, config, body=body, content_type=ctype)
        if status != 200:
            fail("Impersonation failed (HTTP %s)" % status, url=url, response=data)
        config = store_session(config, data.get("response") or {})

    emit(
        {
            "ok": True,
            "base_url": config.get("base_url"),
            "user_id": config.get("user_id"),
            "full_name": config.get("full_name"),
            "email": config.get("email"),
            "role": config.get("role"),
            "user_type": config.get("user_type"),
            "config_path": CONFIG_PATH,
        }
    )


def cmd_logout(_args):
    """Forget this machine's stored account, so the next login starts clean."""
    config = load_config()
    if not config:
        emit({"ok": True, "message": "No stored session", "config_path": CONFIG_PATH})
    email = config.get("email")
    try:
        os.remove(CONFIG_PATH)
    except OSError as exc:
        fail("Could not remove %s: %s" % (CONFIG_PATH, exc))
    emit(
        {
            "ok": True,
            "message": "Signed out %s on this machine" % (email or "the stored account"),
            "next": "py erp.py login",
        }
    )


def cmd_whoami(_args):
    config = load_config()
    if not config.get("token"):
        emit({"ok": False, "error": "Not logged in", "config_path": CONFIG_PATH}, 1)
    age = int(time.time()) - int(config.get("token_saved_at") or 0)
    emit(
        {
            "ok": True,
            "base_url": config.get("base_url"),
            "user_id": config.get("user_id"),
            "full_name": config.get("full_name"),
            "email": config.get("email"),
            "role": config.get("role"),
            "user_type": config.get("user_type"),
            "token_age_hours": round(age / 3600.0, 1),
            "token_fresh": age < TOKEN_MAX_AGE,
            "can_auto_refresh": bool(config.get("password")),
        }
    )


def cmd_tasks(_args):
    config = refresh_if_stale(require_config())
    status, data, url = authed("GET", prefix(config, "agent") + "/agent/tasks", config)
    if status != 200:
        fail("Could not list tasks (HTTP %s)" % status, url=url, response=data)
    emit({"ok": True, "url": url, "data": data.get("data", [])})


def cmd_subtask(args):
    """Fetch one subtask's detail: description, current status/progress and any checklist."""
    config = refresh_if_stale(require_config())
    path = "%s/task/%s/subtask/%s" % (prefix(config, "subtask"), args.task, args.subtask)
    status, data, url = authed("GET", path, config)
    if status != 200:
        fail("Could not read subtask (HTTP %s)" % status, url=url, response=data)

    body = (data.get("response") or {}).get("data") or {}

    # Department workflow stages (backend / frontend / testing / review) are deliberately
    # not reported: one person does all of them here, so they say nothing about progress.
    checklist = [
        {
            "id": item.get("id"),
            "title": ((item.get("sop") or {}).get("title")),
            "done": bool(item.get("is_completed")),
            "note": item.get("note") or "",
        }
        for item in (body.get("sops") or [])
    ]

    emit(
        {
            "ok": True,
            "url": url,
            "id": body.get("id"),
            "name": body.get("name"),
            "description": html_to_text(body.get("description")),
            "description_html": body.get("description") or "",
            "status": body.get("status"),
            "progress": body.get("progress"),
            "priority": body.get("priority"),
            "start_date": body.get("start_date"),
            "end_date": body.get("end_date"),
            "assigned_hours": body.get("assigned_hours"),
            "tracked_hours": body.get("tracked_hours"),
            "checklist": checklist,
            "checklist_done": sum(1 for c in checklist if c["done"]),
            "checklist_total": len(checklist),
            "task_details": (data.get("response") or {}).get("task_details"),
        }
    )


def cmd_update(args):
    config = refresh_if_stale(require_config())

    title = args.title.strip()
    if not title:
        fail("Title is required")

    if args.description_file:
        try:
            with open(args.description_file, "r", encoding="utf-8") as handle:
                description = handle.read().strip()
        except OSError as exc:
            fail("Cannot read description file: %s" % exc)
    else:
        description = (args.description or "").strip()
    if not description:
        fail("Description is empty - pass --description-file or --description")

    payload = {"title": title, "description": description}
    body, ctype = multipart_body({"data": json.dumps(payload)}, args.file)
    path = "%s/subtask/%s/updates/add" % (prefix(config, "subtask"), args.subtask)
    status, data, url = authed("POST", path, config, body=body, content_type=ctype)
    if status not in (200, 201):
        fail("Update not posted (HTTP %s)" % status, url=url, response=data)
    emit({"ok": True, "url": url, "http_status": status, "response": data})


def cmd_updates_list(args):
    config = refresh_if_stale(require_config())
    query = urllib.parse.urlencode({"page": args.page, "limit": args.limit})
    path = "%s/subtask/%s/updates/list?%s" % (
        prefix(config, "subtask"),
        args.subtask,
        query,
    )
    status, data, url = authed("GET", path, config)
    if status != 200:
        fail("Could not list updates (HTTP %s)" % status, url=url, response=data)
    emit({"ok": True, "url": url, "response": data})


def cmd_status(args):
    config = refresh_if_stale(require_config())
    value = args.status.strip()
    if value not in VALID_STATUSES:
        fail(
            "Invalid status %r - an empty or unknown status would blank the subtask"
            % args.status,
            allowed=VALID_STATUSES,
        )
    body, ctype = json_body({"status": value})
    path = "%s/task/%s/subtask/%s/status" % (
        prefix(config, "subtask"),
        args.task,
        args.subtask,
    )
    status, data, url = authed("PATCH", path, config, body=body, content_type=ctype)
    if status != 200:
        fail("Status not changed (HTTP %s)" % status, url=url, response=data)
    emit({"ok": True, "url": url, "status": value, "response": data})


def cmd_progress(args):
    config = refresh_if_stale(require_config())
    try:
        value = float(args.progress)
    except (TypeError, ValueError):
        fail("Progress must be a number between 0 and 100")
    if value < 0 or value > 100:
        fail("Progress must be between 0 and 100, got %s" % args.progress)
    body, ctype = json_body({"progress": value})
    path = "%s/task/%s/subtask/%s/progress" % (
        prefix(config, "subtask"),
        args.task,
        args.subtask,
    )
    status, data, url = authed("PATCH", path, config, body=body, content_type=ctype)
    if status != 200:
        fail("Progress not updated (HTTP %s)" % status, url=url, response=data)
    emit({"ok": True, "url": url, "progress": value, "response": data})


# --------------------------------------------------------------------------- cli


def build_parser():
    parser = argparse.ArgumentParser(
        prog="erp.py", description="Cloudhouse ERP end-of-day CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_login = sub.add_parser("login", help="sign in and store the session")
    p_login.add_argument(
        "--update", action="store_true", help="sign in again, or as a different user"
    )
    p_login.add_argument(
        "--as-staff", metavar="STAFF_ID", help="admin: continue as this staff account"
    )
    p_login.add_argument(
        "--dev", action="store_true", help="use the local backend (%s)" % DEVELOPMENT_URL
    )
    p_login.add_argument("--url", help="a different ERP base URL, without /api/v1")
    p_login.add_argument(
        "--email", help="skip the email prompt and ask only for the password"
    )
    p_login.set_defaults(func=cmd_login)

    p_whoami = sub.add_parser("whoami", help="show the stored session")
    p_whoami.set_defaults(func=cmd_whoami)

    p_logout = sub.add_parser("logout", help="forget the stored account on this machine")
    p_logout.set_defaults(func=cmd_logout)

    p_tasks = sub.add_parser("tasks", help="list my projects, tasks and subtasks")
    p_tasks.set_defaults(func=cmd_tasks)

    p_subtask = sub.add_parser(
        "subtask", help="read one subtask: description, current status/progress, checklist"
    )
    p_subtask.add_argument("--subtask", required=True)
    p_subtask.add_argument("--task", required=True)
    p_subtask.set_defaults(func=cmd_subtask)

    p_update = sub.add_parser("update", help="post a work update on a subtask")
    p_update.add_argument("--subtask", required=True)
    p_update.add_argument("--title", required=True)
    p_update.add_argument("--description")
    p_update.add_argument("--description-file")
    p_update.add_argument("--file", action="append", help="attachment path (repeatable)")
    p_update.set_defaults(func=cmd_update)

    p_list = sub.add_parser("updates", help="list existing updates on a subtask")
    p_list.add_argument("--subtask", required=True)
    p_list.add_argument("--page", default="1")
    p_list.add_argument("--limit", default="10")
    p_list.set_defaults(func=cmd_updates_list)

    p_status = sub.add_parser("status", help="change a subtask status")
    p_status.add_argument("--subtask", required=True)
    p_status.add_argument("--task", required=True)
    p_status.add_argument("--status", required=True, choices=VALID_STATUSES)
    p_status.set_defaults(func=cmd_status)

    p_progress = sub.add_parser("progress", help="change a subtask progress percentage")
    p_progress.add_argument("--subtask", required=True)
    p_progress.add_argument("--task", required=True)
    p_progress.add_argument("--progress", required=True)
    p_progress.set_defaults(func=cmd_progress)

    return parser


def main():
    # ERP data holds arrows, dashes and other characters the Windows console
    # codepage cannot encode; without this, printing a real task list crashes.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
