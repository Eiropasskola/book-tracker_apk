# Grāmatu izsekotājs (Book Tracker)

Cross-platform aplikācija grāmatu lasīšanas izsekošanai. Darbojas uz **Windows, macOS, Linux un Android**.

## Funkcionalitāte

- Grāmatu pievienošana manuāli vai meklējot **Open Library** API
- Statusi: vēlos lasīt / lasu / izlasīta / pamesta
- Vērtējumi (1–5 zvaigznes), piezīmes, datumi
- Vāku attēlu lejupielāde
- **Statistika ar Matplotlib**: pa mēnešiem, žanriem, vērtējumiem
- **Lasīšanas mērķi** ar progresa indikatoriem
- **CSV/JSON eksports**
- **Tumšais režīms**
- Latviešu valodas atbalsts ar DejaVu Sans fontu
- Lokāla SQLite datubāze

---

## 1. fāze - Palaišana no koda (Python)

```cmd
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Datu glabāšana: `%APPDATA%\BookTracker\` (Windows)

---

## 2. fāze - Windows EXE

```cmd
build_windows.bat
```

Rezultāts: `dist\BookTracker.exe`

---

## 4. fāze - Android APK ar GitHub Actions

**Vissvarīgākais:** APK tiek būvēts **GitHub mākonī**, ne uz tava datora. Tev nav jāinstalē Android SDK, Buildozer vai WSL2.

### Soli pa solim

#### 1. Izveido GitHub repo
1. Atver https://github.com/new
2. Repository name: `book-tracker` (vai cits nosaukums)
3. Public repository
4. **NEIEŠLIEC** "Add a README" - mums jau ir savs
5. Klikšķini "Create repository"

#### 2. Pārvērt projektu par git repo (lokāli)
Atver komandrindu projekta mapē:
```cmd
cd C:\Users\konst\Desktop\book_tracker
git init
git add .
git commit -m "Sakuma versija ar GitHub Actions"
```

Ja git nav uzstādīts: lejupielādē no https://git-scm.com/download/win

#### 3. Pievieno GitHub kā remote
GitHub jaunizveidotā repo lapā parādīs komandas - kopē tās. Tās izskatās šādi:
```cmd
git branch -M main
git remote add origin https://github.com/TAVS_LIETOTAJS/book-tracker.git
git push -u origin main
```

#### 4. Vēro būvi GitHub
1. Atver savu repo GitHub lapā
2. Klikšķini cilni "Actions"
3. Redzēsi "Buvee Android APK" workflow palaista
4. Klikšķini uz tā, lai redzētu progresu (~25-40 min)

#### 5. Lejupielādē APK
Pēc veiksmīgas būves:
1. Workflow lapā ritini uz leju
2. "Artifacts" sadaļā būs `BookTracker-APK`
3. Lejupielādē to (ZIP fails, kurā ir APK)

#### 6. Instalē uz Galaxy
1. Pārkopē APK uz tālruni (USB, Google Drive, e-pasts)
2. Tālruni: Iestatījumi → Drošība → Atļaut nezināmu avotu instalāciju
3. Atver APK failu - Android piedāvās instalēt

### Pirmajā būvē kaut kas neizdevās?

**Tas ir normāli!** Pirmā APK būve dažkārt neizdodas, bet ar dažiem labojumiem to var atrisināt. Visbiežākie iemesli:

1. **KivyMD versijas problēma** - `buildozer.spec` izmanto KivyMD 1.1.1 (ne 1.2.0), jo 1.2.0 dažkārt nesakompilējas
2. **Matplotlib trūkst** - Mums tas vēl jāpievieno; pirmā būve to izlaiž
3. **Recipe problēmas** - dažām paketēm Buildozer "recepte" var būt novecojusi

Ja neizdevās, atver workflow lapu, klikšķini uz failed step un nokopē kļūdas tekstu - tad varēsim labot.

---

## Projekta struktūra

```
book_tracker/
├── main.py                  # Ieejas punkts
├── requirements.txt         # Python atkarības (desktop)
├── BookTracker.spec         # PyInstaller (Windows/Mac)
├── buildozer.spec           # Buildozer (Android)
├── build_windows.bat        # Windows EXE skripts
├── .github/workflows/
│   └── build-apk.yml        # GitHub Actions APK būvēšana
├── .gitignore               # Git ignorētie faili
├── README.md
├── core/                    # Biznesa loģika
│   ├── database.py          # SQLite
│   ├── api_client.py        # Open Library
│   ├── charts.py            # Matplotlib grafiki
│   ├── exporter.py          # CSV/JSON eksports
│   ├── fonts.py             # Latviešu fontu reģistrācija
│   └── models.py            # Datu klases
├── screens/                 # GUI ekrāni
│   ├── library_screen.py
│   ├── add_book_screen.py
│   ├── search_screen.py
│   ├── stats_screen.py
│   ├── goals_screen.py
│   └── settings_screen.py
├── kv/                      # Kivy izkārtojumi
│   └── *.kv
└── assets/
    └── covers/              # Lejupielādētie vāki
```

## Licence

MIT
