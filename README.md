# programming_with_sockets
# TCP Server & Client - PYTHON

Ky projekt eshte nje shembull i nje serveri TCP me kliente **admin** dhe **read-only** dhe nje HTTP  per monitorim dhe statistika.

---


##  Qëllimi i projektit

Qellimi i ketij projekti eshte me ndertu nje sistem klient-server per menaxhimin e files permes TCP sockets ne Python, ku perdoruesit mund te komunikojne me serverin ne distance dhe te kryejne operacione mbi file.

Ky projekt eshte i dizajnuar kryesisht per mesim dhe praktike te koncepteve te meposhtme:

Komunikimi Client–Server me TCP
Programimi me threads (multi-client handling)
Ndertimi i nje protokolli te thjeshte komunikimi (JSON messages)
Menaxhimi i role-based access (Admin / Readonly)
Operacione mbi skedare ne server (upload, download, delete, read)
Trajtimi i requests dhe responses ne kohe reale

## Kerkesat

Hape CMD ose Terminal. Sigurohuni qe python eshte i instaluar:

``python --version``

Clone the repo:
``https://github.com/sarakycyku/programming_with_sockets.git``

    
##  Si te filloni?

1. Nis serverin: `python run_server.py`
2. Nis klientin admin: `python run_admin.py`
3. Nis klientin readonly: `python run_readonly.py`

---

##  Komandat e Admin-it

| Komanda | Përshkrimi |
|---------|-------------|
| `/list` | Liston files në server |
| `/read <file>` | Lexon permbajtjen e file |
| `/upload <file>` | Ngarkon skedar ne server |
| `/download <file>` | Shkarkon file nga serveri |
| `/delete <file>` | Fshin file nga serveri |
| `/search <keyword>` | Kerkon fjale ne file |
| `/info <file>` | Tregon informacione per file |
| `/help` | Shfaq ndihmen |
| `/quit` | Dil nga klienti |

---

##  Komandat e Readonly Klientit

| Komanda | Përshkrimi |
|---------|-------------|
| `/list` | Liston files |
| `/read <file>` | Lexon fies |
| `/download <file>` | Shkarkon file nga serveri |
| `/search <keyword>` | Kerkon fjale ne skedare |
| `/info <file>` | Tregon informacione |
| `/help` | Ndihme |
| `/quit` | Dil |

Nuk lejohen: `/upload`, `/delete`

---

##  Monitorimi

Hap ne browser:
http://<IP_ADRESA>:9080/stats

Aty mund te shihni:
- klientet aktiv
- requests (komanda dhe mesazhe)
- aktivitetin ne kohe reale
- rolet e klienteve

---
## Kufizimet
Maksimumi 4 kliente gjithsej
Maksimumi 3 kliente readonly
Admin nuk ka kufizim komandash
Timeout: 120 sekonda pasivitet

##  Si funksionon lidhja?
Klienti lidhet me serverin (IP + port )
Dergon automatikisht auth me token
Serveri verifikon token-in
Serveri cakton rolin (admin ose readonly)
Klienti pranohet nese ka vend
Komunikimi vazhdon përmes TCP requests/replies


# Server
python run_server.py

# Admin
python run_admin.py
> /list
> /read sample.txt

# Readonly
python run_readonly.py
> Pershendetje server!


##  Ndryshimi i IP-se (cdo klient duhet ta beje)

Hape:

`client/config.py`

```python
SERVER_HOST = "192.168.1.x"
SERVER_PORT = 9000  
```

##  Çka duhet me pase kujdes klienti

Gjate perdorimit te ketij sistemi, klienti duhet me qene i kujdesshem ne disa pika te rendesishme per me shmang probleme dhe gabime gjate komunikimit me serverin:

###  Mos e ndrysho token-in (Admin/Readonly)
Nese token-i nuk eshte i sakte, serveri nuk te pranon dhe lidhja deshton.

###  IP adresa duhet me qenë korrekte
Nese `SERVER_HOST` eshte gabim, klienti nuk mund te lidhet me serverin.

###  Timeout i pasivitetit
Nese klienti nuk dergon asnje veprim per 120 sekonda, serveri mund ta shkepuse automatikisht.

###  Respekto kufizimet e roleve
Readonly klienti nuk guxon me perdor komanda si `/upload` ose `/delete`, sepse serveri i refuzon.

###  Komandat duhet me qene të sakta
Gabime ne shkrimin e komandave (p.sh. `/readd` ne vend te `/read`) rezultojne me error.

###  Mos e mbyll lidhjen papritur
Mbyllja pa `/quit` mund me shkaktu disconnect jo të paster dhe gabime ne server.




