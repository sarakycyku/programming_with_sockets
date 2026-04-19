# programming_with_sockets
# TCP Server & Client - PYTHON

Sistem për menaxhimin e skedarëve përmes TCP me dy role: **Admin** dhe **Readonly klient**.

---

##🎯 Qëllimi i projektit

Qëllimi i këtij projekti është me ndërtu një sistem klient-server për menaxhimin e skedarëve përmes TCP sockets në Python, ku përdoruesit mund të komunikojnë me serverin në distancë dhe të kryejnë operacione mbi file.

Ky projekt është i dizajnuar kryesisht për mësim dhe praktikë të koncepteve të mëposhtme:

Komunikimi Client–Server me TCP
Programimi me threads (multi-client handling)
Ndërtimi i një protokolli të thjeshtë komunikimi (JSON messages)
Menaxhimi i role-based access (Admin / Readonly)
Operacione mbi skedarë në server (upload, download, delete, read)
Trajtimi i requests dhe responses në kohë reale

## 🚀 Si të filloni?

1. Nis serverin: `python run_server.py`
2. Nis klientin admin: `python run_admin.py`
3. Nis klientin readonly: `python run_readonly.py`

---

## 🧑‍💻 Komandat e Admin-it

| Komanda | Përshkrimi |
|---------|-------------|
| `/list` | Liston skedarët në server |
| `/read <file>` | Lexon përmbajtjen e skedarit |
| `/upload <file>` | Ngarkon skedar në server |
| `/download <file>` | Shkarkon skedar nga serveri |
| `/delete <file>` | Fshin skedarin nga serveri |
| `/search <keyword>` | Kërkon fjalë në skedarë |
| `/info <file>` | Tregon informacione për skedarin |
| `/help` | Shfaq ndihmën |
| `/quit` | Dil nga klienti |

---

## 👀 Komandat e Readonly Klientit

| Komanda | Përshkrimi |
|---------|-------------|
| `/list` | Liston skedarët |
| `/read <file>` | Lexon skedarin |
| `/download <file>` | Shkarkon skedar nga serveri |
| `/search <keyword>` | Kërkon fjalë në skedarë |
| `/info <file>` | Tregon informacione |
| `/help` | Ndihmë |
| `/quit` | Dil |

❌ Nuk lejohen: `/upload`, `/delete`

---

## 🌐 Monitorimi

Hap në browser:
http://<IP_ADRESA>:9080/stats

Aty mund të shihni:
- klientët aktiv
- requests (komanda dhe mesazhe)
- aktivitetin në kohë reale
- rolet e klientëve

---
## Kufizimet
Maksimumi 4 klientë gjithsej
Maksimumi 3 klientë readonly
Admin nuk ka kufizim komandash
Timeout: 120 sekonda pasivitet

## 🔄 Si funksionon lidhja?
Klienti lidhet me serverin (IP + port )
Dërgon automatikisht auth me token
Serveri verifikon token-in
Serveri cakton rolin (admin ose readonly)
Klienti pranohet nëse ka vend
Komunikimi vazhdon përmes TCP requests/replies

## Testimi

## Testimi

# Server
python run_server.py

# Admin
python run_admin.py
> /list
> /read sample.txt

# Readonly
python run_readonly.py
> Pershendetje server!


## 🔧 Ndryshimi i IP-së (cdo klient duhet ta beje)

Hape:

`client/config.py`

```python
SERVER_HOST = "192.168.1.x"
SERVER_PORT = 9000  
```

## ⚠️ Çka duhet me pasë kujdes klienti

Gjatë përdorimit të këtij sistemi, klienti duhet me qenë i kujdesshëm në disa pika të rëndësishme për me shmang probleme dhe gabime gjatë komunikimit me serverin:

### 🔐 Mos e ndrysho token-in (Admin/Readonly)
Nëse token-i nuk është i saktë, serveri nuk të pranon dhe lidhja dështon.

### 🌐 IP adresa duhet me qenë korrekte
Nëse `SERVER_HOST` është gabim, klienti nuk mund të lidhet me serverin.

### ⏱️ Timeout i pasivitetit
Nëse klienti nuk dërgon asnjë veprim për 120 sekonda, serveri mund ta shkëpusë automatikisht.

### 🚫 Respekto kufizimet e roleve
Readonly klienti nuk guxon me përdor komanda si `/upload` ose `/delete`, sepse serveri i refuzon.

### 📡 Komandat duhet me qenë të sakta
Gabime në shkrimin e komandave (p.sh. `/readd` në vend të `/read`) rezultojnë me error.

### 🔄 Mos e mbyll lidhjen papritur
Mbyllja pa `/quit` mund me shkaktu disconnect jo të pastër dhe gabime në server.




