# 🚀 GitHub Setup Guide for IOT Lightning Bridge HACS

## 📋 Fișierele Gata (10 fișiere)

✅ `.gitignore` - Exclud fișiere inutile din git  
✅ `LICENSE` - MIT License  
✅ `README.md` - Documentație profesională  
✅ `GITHUB_SETUP.sh` - Script helper  
✅ `manifest.json` - Metadata integrare  
✅ `__init__.py` - Setup integration  
✅ `config_flow.py` - Configuration UI  
✅ `const.py` - Constante  
✅ `switch.py` - Switch entity cu MQTT  
✅ `strings.json` - UI translations  

---

## 🔧 SETUP GITHUB STEP-BY-STEP

### **PASUL 1: Creează Cont GitHub (dacă nu ai)**

- Mergi la https://github.com
- Click "Sign up"
- Completează formularul
- Verifică email-ul

### **PASUL 2: Crea Repository Nou**

1. Accesează https://github.com/new
2. Completează:
   - **Repository name:** `iot_lightning_bridge_hacs`
   - **Description:** Bridge oficial pentru integrarea dispozitivelor IOT Lightning în Home Assistant via MQTT
   - **Public / Private:** Selectează **Public** (dacă vrei ca alții să instaleze via HACS)
3. **IMPORTANT:** ❌ NU bifează:
   - ❌ "Add a README file"
   - ❌ "Add .gitignore"
   - ❌ "Choose a license"
   
   (Avem deja aceste fișiere!)
4. Click **"Create repository"**

### **PASUL 3: Configurează Git Local**

Deschide terminal și execută:

```bash
cd /home/tzongocu/Productie/iot_lightning_bridge_hacs
```

**Configurează git (prima dată doar):**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Înlocuiește `Your Name` și `your.email@example.com` cu datele tale!

### **PASUL 4: Inițializează Repository Local**

```bash
git init
```

### **PASUL 5: Adaugă Remote (URL-ul GitHub-ului)**

```bash
git remote add origin https://github.com/YOUR_USERNAME/iot_lightning_bridge_hacs.git
```

**Înlocuiește `YOUR_USERNAME` cu username-ul tău GitHub!**

Exemplu:
```bash
# Daca username-ul tau e "john_developer"
git remote add origin https://github.com/john_developer/iot_lightning_bridge_hacs.git
```

### **PASUL 6: Adaugă Toate Fișierele**

```bash
git add .
```

Verifică ce fișiere vor fi adăugate:
```bash
git status
```

Ar trebui să vezi 10 fișiere (în verde, cu "new file:"):
- .gitignore
- GITHUB_SETUP.sh
- LICENSE
- README.md
- __init__.py
- config_flow.py
- const.py
- manifest.json
- strings.json
- switch.py

### **PASUL 7: Commit (Salvează versiunea)**

```bash
git commit -m "Initial commit: IOT Lightning Bridge HACS integration"
```

### **PASUL 8: Rename Branch (dacă necesar)**

```bash
git branch -M main
```

### **PASUL 9: Push la GitHub 🚀**

```bash
git push -u origin main
```

**Primera dată, ar putea cere autentificare:**

Opțiunile sunt:
1. **SSH Key** (recomandat pentru proiecte frecvente)
2. **Personal Access Token** (mai ușor)
3. **GitHub CLI**

**Cea mai simplă:** Token personal
- Mergi la https://github.com/settings/tokens
- Click "Generate new token"
- Selectează scopes: `repo`, `workflow`
- Copy token-ul
- Paste-l când cere parolă la `git push`

---

## ✅ VERIFICA DUPĂ PUSH

1. Mergi la https://github.com/YOUR_USERNAME/iot_lightning_bridge_hacs
2. Ar trebui să vezi:
   - ✅ Fișierele listate (10 fișiere)
   - ✅ README.md afișat frumos
   - ✅ Descrierea în pagina principală
   - ✅ "MIT License" în dreapta sus

---

## 🔄 COMENZI GIT UTILE (De Reținut)

```bash
# Vezi status local
git status

# Vezi commit-urile locale
git log --oneline

# Modifică fișier și push din nou
git add .
git commit -m "Update: description"
git push

# Vezi remote repositories
git remote -v

# Sync din GitHub (dacă au făcut alții changes)
git pull origin main
```

---

## 🆘 TROUBLESHOOTING

### ❌ "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/iot_lightning_bridge_hacs.git
```

### ❌ "Permission denied (publickey)"
- Folosește HTTPS în loc de SSH
- Sau configurează SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### ❌ "fatal: not a git repository"
```bash
cd /home/tzongocu/Productie/iot_lightning_bridge_hacs
git init
```

### ❌ "Error: Permission to access ... denied"
- Verifică dacă username-ul și repository-ul sunt corecte
- Generează token personal dacă ai 2FA activ

---

## 📝 ACTUALIZARE MANIFEST.JSON

După ce ai repository pe GitHub, actualiza:

```json
{
  "domain": "iot_lightning_bridge_hacs",
  "name": "IOT Lightning Bridge HACS",
  "codeowners": ["@yourusername"],
  "config_flow": true,
  "documentation": "https://github.com/YOUR_USERNAME/iot_lightning_bridge_hacs",
  "issue_tracker": "https://github.com/YOUR_USERNAME/iot_lightning_bridge_hacs/issues",
  "requirements": [],
  "version": "1.0.0",
  "homeassistant": "2026.1.0",
  "dependencies": ["mqtt"],
  "after_dependencies": ["mqtt"]
}
```

Înlocuiește `YOUR_USERNAME` cu al tău!

---

## 🎉 CE URMEAZĂ?

După ce e pe GitHub:

1. **Testează local pe Home Assistant** (instalare manuală)
2. **Adaugă la HACS (Custom Repository)**
3. **Publică pe Home Assistant Community Forum**
4. **Versioning** - Când faci updates, creează GitHub Release

---

**Done! 🎊**
