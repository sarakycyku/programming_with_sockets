
import json


class CommandHandler:
    def __init__(self, client):
        self.client = client

    def show_help(self, is_admin):
        print("\n" + "=" * 40)
        print("KOMANDAT E DISPONUESHME:")
        print("=" * 40)
        print("/list              - Listo file-t")
        print("/read <file>       - Lexo përmbajtjen e file-t")
        print("/search <keyword>  - Kërko file")
        print("/info <file>       - Info për file (madhësia, data)")
        print("/download <file>   - Shkarko file (të njëjtë me /read)")
        print("ping               - Testo lidhjen")

        if is_admin:
            print("\n--- KOMANDAT ADMIN ---")
            print("/upload <file> <content>  - Ngarko file")
            print("/delete <file>            - Fshi file")

        print("\nexit               - Mbylle lidhjen")
        print("=" * 40 + "\n")

    def execute(self, user_input: str):
        """Parse user input and return a JSON string to send to server.

        Returns None if the command is invalid or should not be sent.
        """
        user_input = user_input.strip()
        if not user_input:
            return None

        # ping is a special case
        if user_input.lower() == 'ping':
            return json.dumps({"command": "ping", "args": []})

        parts = user_input.split()
        cmd = parts[0]
        args = []

        if cmd in ['/list']:
            args = []

        elif cmd in ['/read', '/search', '/info', '/download', '/delete']:
            if len(parts) < 2:
                print(f"[!] Perdorje: {cmd} <filename>")
                return None
            args = [parts[1]]

        elif cmd == '/upload':
            # /upload <filename> <content...>
            if len(parts) < 3:
                print("[!] Perdorje: /upload <filename> <content>")
                return None
            filename = parts[1]
            content = ' '.join(parts[2:])
            args = [filename, content]

        else:
            print(f"[!] Komande e panjohur: {cmd}")
            return None

        return json.dumps({"command": cmd, "args": args})