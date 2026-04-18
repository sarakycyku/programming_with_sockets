"""
Admin client -- interactive REPL with full file-system access.

Usage:
    python run_admin.py
    python client/admin_client.py       (from project root)

Available commands:
    /list                   List files in the server directory
    /read   <filename>      Print a file's text content
    /upload <local_path>    Upload a local file to the server
    /download <filename>    Download a server file to the current directory
    /delete <filename>      Delete a file from the server
    /search <keyword>       Find files containing the keyword
    /info   <filename>      Show file metadata (size, timestamps)
    /help                   Re-print this command list
    /quit                   Exit cleanly

Any other input is sent as a plain text message.
"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.base_client import BaseClient
from client.config import ADMIN_TOKEN


_HELP = """
+- Admin Commands --------------------------------------------------+
|  /list                  List files in server directory            |
|  /read   <filename>     Print file content                        |
|  /upload <local_path>   Upload local file to server               |
|  /download <filename>   Download file from server                 |
|  /delete <filename>     Delete file from server                   |
|  /search <keyword>      Search files by keyword                   |
|  /info   <filename>     File metadata (size, created, modified)   |
|  /help                  Show this help                            |
|  /quit                  Disconnect and exit                       |
|  <any text>             Send as a plain message                   |
+-------------------------------------------------------------------+
"""


class AdminClient(BaseClient):
    def __init__(self) -> None:
        super().__init__(token=ADMIN_TOKEN)

    # -- Interactive REPL -------------------------------------------------------

    def run_interactive(self) -> None:
        if not self.connect():
            return
        print(_HELP)
        try:
            while True:
                try:
                    line = input("[admin] > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not line:
                    continue
                if line == "/quit":
                    break
                if line == "/help":
                    print(_HELP)
                    continue
                if line.startswith("/"):
                    self._dispatch(line)
                else:
                    resp = self.send_message(line)
                    self._print(resp)
        finally:
            self.disconnect()
            print("[CLIENT] Disconnected.")

    # -- Command dispatcher -----------------------------------------------------

    def _dispatch(self, line: str) -> None:
        parts = line.split(maxsplit=1)
        cmd   = parts[0].lower()
        arg   = parts[1].strip() if len(parts) > 1 else ""

        if cmd == "/list":
            self._print(self._cmd("/list", []))

        elif cmd == "/read":
            if not arg:
                print("Usage: /read <filename>")
                return
            self._print(self._cmd("/read", [arg]))

        elif cmd == "/upload":
            if not arg:
                print("Usage: /upload <local_file_path>")
                return
            self._do_upload(arg)

        elif cmd == "/download":
            if not arg:
                print("Usage: /download <filename>")
                return
            self._do_download(arg)

        elif cmd == "/delete":
            if not arg:
                print("Usage: /delete <filename>")
                return
            self._print(self._cmd("/delete", [arg]))

        elif cmd == "/search":
            if not arg:
                print("Usage: /search <keyword>")
                return
            self._print(self._cmd("/search", [arg]))

        elif cmd == "/info":
            if not arg:
                print("Usage: /info <filename>")
                return
            self._print(self._cmd("/info", [arg]))

        else:
            print(f"Unknown command '{cmd}'. Type /help for the command list.")

