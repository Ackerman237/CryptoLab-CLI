# Refactor Guardrails (Always-On)

**Aturan wajib untuk semua sesi refactor. Dilanggar = stop dan review.**

---

## 1. Satu Masalah, Satu Patch Kecil
- Maksimal **satu langkah roadmap** per commit/PR
- Setelah patch: jalankan test, tampilkan diff, minta review, **baru lanjut**
- JANGAN menggabungkan A1+A2, atau B2+B3, atau C1+C2 dalam satu commit

---

## 2. Scope Terbatas ke Roadmap
- Hanya ubah file & fungsi yang tercantum di langkah roadmap aktif
- Temuan lain (typo, style, dead code di file lain) → **catat di PROGRESS.md**, jangan diperbaiki
- Exception: quick wins (Q1-Q6) boleh kapan saja tapi tetap 1 commit per item

---

## 3. Refactor = Tidak Ubah Perilaku
- **Characterization test WAJIB** sebelum pindah kode (Phase B1-B4)
- Jalankan test **sebelum** dan **sesudah** setiap perubahan
- Jika test gagal: revert, analisis, jangan "fix test to match new behavior"

---

## 4. Format Input/Output Kripto = Frozen
- Ciphertext, hash, encoding, format kunci, signature **tidak boleh berubah**
- Jika perlu ubah (misal tambah field): **persetujuan eksplisit** dulu
- Test round-trip (encrypt→decrypt, sign→verify) harus identik

---

## 5. Zero Dependensi Baru
- JANGAN tambah package ke `pyproject.toml` tanpa persetujuan
- Standard library only untuk refactor internal
- Exception: tooling (ruff, mypy, black) di Phase D2

---

## 6. Git Discipline
- JANGAN commit, push, atau rewrite history tanpa diminta
- Cukup usulkan pesan commit: `feat: extract Rule widget` / `fix: hmac constant-time compare`
- Branch strategy: `refactor/phase-X-step-Y` per phase

---

## 7. Bahasa & Konvensi
- Penjelasan ke user: **Bahasa Indonesia**
- Code, identifier, komentar: **English** (ikuti konvensi existing)
- Docstring: English, Google style (seperti existing)

---

## 8. Security Guardrails (Ref: 20-security.md)
- No secrets/keys in logs, history, error messages
- CSPRNG (`secrets`) untuk random values
- Constant-time compare untuk hash/verify
- Minimum PBKDF2 100k, Bcrypt cost 4-31
- Warning untuk weak algos (MD5, SHA1, ECB, RC2)

---

## 9. Definition of Done per Step
- [ ] Test existing pass (`pytest tests/ -v`)
- [ ] Characterization test pass (snapshot match)
- [ ] `ruff check src/` clean
- [ ] `mypy src/` clean
- [ ] Manual smoke test: `cryptolab menu`, `cryptolab <cmd> --help`
- [ ] No `print(`/`input(` in feature code (core/, cli/commands/, interactive/handlers/)
- [ ] No raw ANSI (`\033[`) in feature code
- [ ] No manual divider (`"=" * n`, `"-" * n`) in feature code

---

## 10. Stop Conditions
Berhenti dan minta review jika:
- Test gagal dan bukan flaky
- Perilaku berubah (output beda untuk input sama)
- Scope melampaui langkah roadmap
- Butuh keputusan arsitektur baru (bukan di plan)