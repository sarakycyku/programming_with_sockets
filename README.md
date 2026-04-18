# programming_with_sockets
# TCP Server & Client

Sistem për menaxhimin e skedarëve përmes TCP.

## Si të filloni?

1. Nis serverin: `python run_server.py`
2. Nis klientin admin: `python run_admin.py`
3. Nis klientin readonly: `python run_readonly.py`

## Komandat e admin-it

| Komanda | Përshkrimi |
|---------|-------------|
| `/list` | Liston skedarët |
| `/read sample.txt` | Lexon skedar |
| `/upload foto.jpg` | Ngarkon skedar |
| `/download sample.txt` | Shkarkon skedar |
| `/delete sample.txt` | Fshin skedar |
| `/search fjala` | Kërkon fjalë |
| `/info sample.txt` | Detajet e skedarit |
| `/help` | Ndihmë |
| `/quit` | Dil |

Çdo tekst tjetër dërgohet si mesazh i thjeshtë.

## Monitorimi

Hapni në shfletues: `http://localhost:9080/stats`

## Ndrysho IP-në

Për lidhje nga kompjuterë të tjerë, ndrysho te `client/config.py`:
`SERVER_HOST = "192.168.1.x"`

## Kufizimet

- Maksimumi 4 klientë gjithsej
- Maksimumi 3 klientë readonly
- Admin-et nuk kanë kufi (përveç totalit)
- Timeout i klientit: 120 sekonda pasivitet
- 
## Si bëhet lidhja?

1. Klienti lidhet me IP dhe portën e serverit (9000)
2. Klienti dërgon kërkesën e parë `auth` me token
3. Serveri kontrollon token-in dhe vendos nëse është admin apo readonly
4. Serveri kontrollon nëse ka vend (max 4 klientë, max 3 readonly)
5. Nëse ka vend, serveri përgjigjet me `auth_ok` dhe rolin
6. Klienti tani mund të dërgojë mesazhe ose komanda
7. Për çdo kërkesë, serveri përgjigjet me një përgjigje

## Testimi

```bash
# Terminal 1 - Server
python run_server.py

# Terminal 2 - Admin
python run_admin.py
> /list
> /read sample.txt

# Terminal 3 - Readonly
python run_readonly.py
> Pershendetje server!

