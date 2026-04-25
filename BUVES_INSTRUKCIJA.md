# Kā uzbūvēt APK ar GitHub Actions

## Galvenās izmaiņas pret v8

1. **Izņemts `matplotlib`** — to nevar normāli uzbūvēt python-for-android. Grafiki tagad zīmēti ar Pillow.
2. **Fonts tagad iekļauts pakas iekšienē** (`assets/fonts/DejaVuSans*.ttf`). Vairs nemeklē matplotlib mapē.
3. **`buildozer.spec` un `requirements.txt` saskaņoti** — abos `kivy 2.3.0` + `kivymd 1.1.1`.
4. **Sākam tikai ar `arm64-v8a`** — viena arhitektūra = uz pusi ātrāka būve. (Visiem mūsdienu telefoniem pietiek.)
5. **`android.api = 34`** — atbilst jaunajām Google Play prasībām.
6. **Workflow uzlabots** — pievienots cache, atsevišķs licences solis, log faila augšupielāde kļūdas gadījumā.

## Kā palaist

```bash
# 1. Izveido jaunu GitHub repo (privātu vai publisku - vienalga)
# 2. Repo SAKNĒ ievieto VISU šī projekta saturu
#    (svarīgi: buildozer.spec jābūt repo saknē, NEVIS apakšmapē!)

git init
git add .
git commit -m "Initial book tracker"
git branch -M main
git remote add origin https://github.com/TAVS-LIETOTAJVARDS/book-tracker.git
git push -u origin main
```

3. Atver GitHub → tab **Actions** → izvēlies "Build Android APK" → **Run workflow**
4. Pirmā būve aizņem ~30–45 minūtes (lejupielādē Android SDK + NDK).
5. Nākamās būves ar cache: ~10–15 minūtes.
6. Kad pabeigts, lejupielādē **BookTracker-APK** no artifacts.

## Ja kaut kas neiet

Skaties **build-log** artifactu — tur pilns log no `buildozer.spec` palaišanas.
