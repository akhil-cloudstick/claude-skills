---
description: Sign out of the Cloudhouse ERP on this machine, so the next /erp:eod asks for login again
---

Run the ERP logout and report the result.

1. Find the plugin's script directory (this command lives in the same plugin as the `eod`
   skill, so the script is at `../skills/eod/scripts/erp.py` relative to this command file).
2. Show who is about to be signed out:

   ```
   py "<plugin>/skills/eod/scripts/erp.py" whoami
   ```

3. Then clear the stored credentials:

   ```
   py "<plugin>/skills/eod/scripts/erp.py" logout
   ```

4. Confirm in one line which account was removed and from where, for example:

   > Signed out `akhil@cloudstick.io` on this machine. `~/.cloudhouse-eod.json` deleted — the
   > next `/erp:eod` will ask for email and password again.

Notes:
- This only affects **this machine**. Other machines keep their own session.
- Nothing on the ERP server changes; only the locally stored email, password and token go.
- If nothing was stored, say so plainly instead of reporting a signout that did not happen.
