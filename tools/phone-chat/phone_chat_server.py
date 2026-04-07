#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOST = os.environ.get("PHONE_CHAT_HOST", "127.0.0.1")
PORT = int(os.environ.get("PHONE_CHAT_PORT", "8787"))
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://127.0.0.1:11434")


def roleplay_rank(model_name: str) -> tuple[int, str]:
    name = model_name.lower()
    score = 0

    if "abliterated" in name or "uncensored" in name:
        score -= 120
    if "magnum-v4-22b" in name:
        score -= 118
    if "midnight-miqu" in name:
        score -= 114
    if "magnum" in name:
        score -= 100
    if "mistral-small3.1" in name:
        score -= 96
    if "mistral-small3.1" in name or "mistral-small3.2" in name:
        score -= 92
    if "eva" in name:
        score -= 85
    if "dolphin3" in name:
        score -= 78
    if "wizardlm" in name:
        score -= 74
    if "hermes" in name:
        score -= 70
    if "qwen3" in name:
        score -= 55
    if "qwen2.5" in name or "qwen-2.5" in name:
        score -= 45

    if ":32b" in name or "32b" in name:
        score -= 18
    if ":30b" in name or "30b" in name:
        score -= 16
    if ":14b" in name or "14b" in name:
        score -= 12
    if ":12b" in name or "12b" in name:
        score -= 10
    if ":8b" in name or "8b" in name:
        score -= 6

    if "embed" in name:
        score += 500

    return (score, name)


def sorted_models(models: list[str]) -> list[str]:
    return sorted(models, key=roleplay_rank)


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Local Ollama Chat</title>
  <style>
    :root {
      --bg: #0f1115;
      --panel: #171a21;
      --panel-2: #1e2330;
      --text: #edf2f7;
      --muted: #9aa4b2;
      --accent: #7dd3fc;
      --user: #1f2937;
      --assistant: #0b3b4a;
      --border: #2a3140;
      --danger: #f87171;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #19202b 0%, var(--bg) 45%);
      color: var(--text);
      min-height: 100vh;
    }
    .wrap {
      max-width: 900px;
      margin: 0 auto;
      padding: 18px 14px 24px;
    }
    .header {
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .title {
      font-size: 18px;
      font-weight: 700;
    }
    .sub {
      color: var(--muted);
      font-size: 13px;
      margin-top: 4px;
    }
    .controls {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      background: rgba(23, 26, 33, 0.9);
      border: 1px solid var(--border);
      padding: 10px;
      border-radius: 14px;
      margin-bottom: 12px;
      position: sticky;
      top: 8px;
      backdrop-filter: blur(10px);
    }
    select, textarea, button {
      border-radius: 12px;
      border: 1px solid var(--border);
      background: var(--panel-2);
      color: var(--text);
      font: inherit;
    }
    select {
      padding: 10px 12px;
      min-width: 240px;
    }
    .chat {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 12px;
    }
    .msg {
      padding: 12px 14px;
      border-radius: 16px;
      border: 1px solid var(--border);
      white-space: pre-wrap;
      line-height: 1.45;
      box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }
    .msg.user {
      background: var(--user);
      margin-left: 36px;
    }
    .msg.assistant {
      background: var(--assistant);
      margin-right: 36px;
    }
    .label {
      display: block;
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .composer {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    textarea {
      width: 100%;
      min-height: 130px;
      padding: 14px;
      resize: vertical;
    }
    .actions {
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
    }
    .left-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    button {
      padding: 10px 14px;
      font-weight: 600;
      cursor: pointer;
    }
    button.primary {
      background: linear-gradient(135deg, #0891b2, #2563eb);
      border: none;
    }
    button.secondary {
      background: transparent;
    }
    .status {
      color: var(--muted);
      font-size: 13px;
    }
    .status.error {
      color: var(--danger);
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div>
        <div class="title">Local Ollama Chat</div>
        <div class="sub">Private to your tailnet. Runs on this Mac.</div>
      </div>
    </div>

    <div class="controls">
      <label>
        <span class="sub">Model</span><br>
        <select id="model"></select>
      </label>
      <div class="status" id="status">Loading models…</div>
    </div>

    <div class="chat" id="chat"></div>

    <div class="composer">
      <textarea id="prompt" placeholder="Ask something…"></textarea>
      <div class="actions">
        <div class="left-actions">
          <button class="primary" id="send">Send</button>
          <button class="secondary" id="clear">Clear Chat</button>
        </div>
        <div class="sub">Tip: keep this tab open on your phone.</div>
      </div>
    </div>
  </div>

  <script>
    const chatEl = document.getElementById('chat');
    const modelEl = document.getElementById('model');
    const promptEl = document.getElementById('prompt');
    const statusEl = document.getElementById('status');
    const sendBtn = document.getElementById('send');
    const clearBtn = document.getElementById('clear');

    let messages = [];

    function setStatus(text, isError = false) {
      statusEl.textContent = text;
      statusEl.className = isError ? 'status error' : 'status';
    }

    function render() {
      chatEl.innerHTML = '';
      for (const m of messages) {
        const div = document.createElement('div');
        div.className = `msg ${m.role}`;
        const label = document.createElement('span');
        label.className = 'label';
        label.textContent = m.role;
        const body = document.createElement('div');
        body.textContent = m.content;
        div.appendChild(label);
        div.appendChild(body);
        chatEl.appendChild(div);
      }
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }

    async function loadModels() {
      const res = await fetch('/api/models');
      const data = await res.json();
      modelEl.innerHTML = '';
      for (const model of data.models) {
        const opt = document.createElement('option');
        opt.value = model;
        opt.textContent = model;
        modelEl.appendChild(opt);
      }
      if (data.models.length === 0) {
        setStatus('No local Ollama models found.', true);
      } else {
        setStatus(`Ready with ${data.models.length} local model${data.models.length === 1 ? '' : 's'}.`);
      }
    }

    async function send() {
      const prompt = promptEl.value.trim();
      if (!prompt) return;
      const model = modelEl.value;
      if (!model) {
        setStatus('Pick a model first.', true);
        return;
      }

      messages.push({ role: 'user', content: prompt });
      render();
      promptEl.value = '';
      sendBtn.disabled = true;
      setStatus('Thinking…');

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model, messages })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Request failed');
        messages.push({ role: 'assistant', content: data.message || '(no response)' });
        render();
        setStatus('Ready');
      } catch (err) {
        setStatus(err.message || 'Request failed', true);
      } finally {
        sendBtn.disabled = false;
      }
    }

    sendBtn.addEventListener('click', send);
    clearBtn.addEventListener('click', () => {
      messages = [];
      render();
      setStatus('Chat cleared.');
    });
    promptEl.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') send();
    });

    loadModels().catch((err) => setStatus(err.message || 'Could not load models', true));
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path == "/api/models":
            try:
                data = ollama_get("/api/tags")
                models = sorted_models([m["name"] for m in data.get("models", [])])
                self._send(200, json.dumps({"models": models}).encode("utf-8"))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}).encode("utf-8"))
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        if self.path != "/api/chat":
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            upstream = ollama_post("/api/chat", {
                "model": payload.get("model"),
                "messages": payload.get("messages", []),
                "stream": False,
            })
            message = upstream.get("message", {}).get("content", "")
            self._send(200, json.dumps({"message": message}).encode("utf-8"))
        except Exception as exc:
            self._send(500, json.dumps({"error": str(exc)}).encode("utf-8"))


def ollama_get(path: str) -> dict:
    req = urllib.request.Request(f"{OLLAMA_BASE}{path}")
    with urllib.request.urlopen(req, timeout=120) as res:
        return json.loads(res.read().decode("utf-8"))


def ollama_post(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(detail or exc.reason) from exc


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving on http://{HOST}:{PORT}", flush=True)
    server.serve_forever()
