

//

def show_help(self, is_admin):
    """Shfaq ndihmën"""
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