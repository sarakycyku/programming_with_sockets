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


class ReadOnlyClient(BaseClient):
    """Connects with an empty token, which the server maps to the 'readonly' role."""

    def __init__(self) -> None:
        super().__init__(token="")  # No token -> readonly

    def run_interactive(self) -> None:
        if not self.connect():
            return
        print("[CLIENT] Connected as read-only.")
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
                resp = self.send_message(line)
                if resp is None:
                    print("[CLIENT] Lost connection -- attempting reconnect...")
                    if not self.reconnect():
                        print("[CLIENT] Could not reconnect. Exiting.")
                        break
                    continue
                payload = resp.get("payload", {})
                print(
                    payload.get("text")
                    or payload.get("error")
                    or str(payload)
                )
        finally:
            self.disconnect()
            print("[CLIENT] Disconnected.")


if __name__ == "__main__":
    ReadOnlyClient().run_interactive()
