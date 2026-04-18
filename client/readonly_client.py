"""
Read-only client -- can send text messages; file commands are forbidden.

Usage:
    python run_readonly.py
    python client/readonly_client.py    (from project root)

Type any text and press Enter to send.
Type /quit or press Ctrl-C to exit.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.base_client import BaseClient
import base64
import json


_HELP_READONLY = """
- Read-only Commands -----------------------------------------------+
|  /list                  List files in server directory            |
|  /read   <filename>     Print file content                        |
|  /download <filename>   Download file from server                 |
|  /search <keyword>      Search files by keyword                   |
|  /info   <filename>     File metadata (size, created, modified)   |
|  /help                  Show this help                            |
|  /quit                  Disconnect and exit                       |
|  <any text>             Send as a plain message                   |
+-------------------------------------------------------------------+
"""


class ReadOnlyClient(BaseClient):
    """Connects with an empty token, which the server maps to the 'readonly' role."""

    def __init__(self) -> None:
        super().__init__(token="")  # No token -> readonly

    def run_interactive(self) -> None:
        if not self.connect():
            return
        print("[CLIENT] Connected as read-only.")
        print(_HELP_READONLY)
        print("         Type messages and press Enter. /quit or Ctrl-C to exit.\n")
        try:
            while True:
                try:
                    line = input("[readonly] > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not line:
                    continue
                if line == "/quit":
                    break
                if line == "/help":
                    print(_HELP_READONLY)
                    continue

                if line.startswith("/"):
                    # Allow read-style commands: /list, /read, /download, /search, /info
                    resp = self._cmd(line.split(maxsplit=1)[0],
                                     [line.split(maxsplit=1)[1]] if len(line.split(maxsplit=1)) > 1 else [])
                else:
                    resp = self.send_message(line)

                if resp is None:
                    print("[CLIENT] Lost connection -- attempting reconnect...")
                    if not self.reconnect():
                        print("[CLIENT] Could not reconnect. Exiting.")
                        break
                    continue

                payload = resp.get("payload", {})
                # Print errors first
                if "error" in payload:
                    print(f"[ERROR] {payload['error']}")
                    continue

                # /list and /search return dicts with lists
                if "files" in payload or "matches" in payload:
                    print(json.dumps(payload, indent=2))
                    continue

                # /read returns 'content'
                if "content" in payload:
                    print(f"-- {payload.get('filename', '')} --")
                    print(payload["content"])
                    print("--------------------------------")
                    continue

                # /download returns base64 content
                if "content_b64" in payload:
                    filename = payload.get("filename", "download.bin")
                    data = base64.b64decode(payload.get("content_b64", ""))
                    save_path = os.path.join(os.getcwd(), filename)
                    with open(save_path, "wb") as fh:
                        fh.write(data)
                    print(f"[OK] Downloaded '{filename}' -> {save_path}  ({len(data):,} bytes)")
                    continue

                # Fallback: print any textual payload
                print(payload.get("text") or str(payload))
        finally:
            self.disconnect()
            print("[CLIENT] Disconnected.")


    # -- Helpers -------------------------------------------------------------

    def _cmd(self, cmd: str, args: list) -> dict:
        return self._send_and_recv("command", {"cmd": cmd, "args": args})


if __name__ == "__main__":
    ReadOnlyClient().run_interactive()
