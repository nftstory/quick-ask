# Quick Ask Agent Notes

## App Store Connect JWT

Shared App Store Connect JWT config for Codex lives at:
- `/Users/nicholas/.codex/shared/appstoreconnect/.env`

Repo-safe example and documentation live at:
- `/Users/nicholas/.codex/shared/appstoreconnect/.env.example`
- `/Users/nicholas/.codex/shared/appstoreconnect/README.md`

When a repo needs ASC/TestFlight upload values, load that shared `.env` instead of re-discovering credentials or using interactive Keychain flows.

## Remote Test Offload (Mac Mini over Tailscale SSH)

Use this when local test runs are disruptive.

Prerequisites:
- SSH alias `mac-mini-1` is configured and reachable.
- Remote user/path used by default: `harold@mac-mini-1:/Users/harold/Development/tools/quick-ask-smoke`
- Remote Python bootstrap (one-time):
  - `ssh mac-mini-1 'python3 -m pip install --user --upgrade pip pytest'`

Targeted backend test offload workflow:
1. `ssh mac-mini-1 'mkdir -p /Users/harold/Development/tools/quick-ask-smoke/tests'`
2. `scp quick_ask_backend.py mac-mini-1:/Users/harold/Development/tools/quick-ask-smoke/quick_ask_backend.py`
3. `scp quick_ask_shared.py mac-mini-1:/Users/harold/Development/tools/quick-ask-smoke/quick_ask_shared.py`
4. `scp tests/test_codex_app_server_backend.py mac-mini-1:/Users/harold/Development/tools/quick-ask-smoke/tests/test_codex_app_server_backend.py`
5. `ssh mac-mini-1 'cd /Users/harold/Development/tools/quick-ask-smoke && python3 tests/test_codex_app_server_backend.py'`

Preferred targeted backend run:
- `ssh mac-mini-1 'cd /Users/harold/Development/tools/quick-ask-smoke && python3 -m pytest -q tests/test_codex_app_server_backend.py tests/test_backend_env.py tests/test_quick_ask_backend_images.py'`

Guidance:
- Prefer targeted tests for changed functionality.
- Avoid full local UI suites unless explicitly requested.

## Full Suite on Mac Mini

Use this when asked to run all tests remotely instead of the local machine.

Sync workspace to Mac Mini clone:
1. `ssh mac-mini-1 'mkdir -p /Users/harold/Development/tools/quick-ask-smoke'`
2. `rsync -az --delete --exclude '.git' --exclude '.venv' --exclude '__pycache__' --exclude '.pytest_cache' '/Users/nicholas/Development/tools/quick-ask/' 'mac-mini-1:/Users/harold/Development/tools/quick-ask-smoke/'`

Run full test suite remotely:
- `ssh mac-mini-1 'python3 -m pip install --user -q pytest >/dev/null 2>&1 || true; cd /Users/harold/Development/tools/quick-ask-smoke && python3 -m pytest -q'`

Optional: save output to a remote artifact:
- `ssh mac-mini-1 'cd /Users/harold/Development/tools/quick-ask-smoke && python3 -m pytest -q | tee /tmp/quick-ask-pytest.txt'`
