# Security Guardrails (Crypto Project)

**Project mengandung kode kriptografi, autentikasi, dan encoding. Aturan ini always-on.**

---

## 1. Secrets & Key Handling
- **JANGAN** log password, key, IV, salt, private key, seed phrase
- `utils/history.py`: `log_history()` default `include_secrets=False` → **enforce**
- Jika caller butuh log secret: **persetujuan eksplisit** + audit trail
- Error message: `Key invalid` bukan `Key 'abc123' invalid`

---

## 2. Random Number Generation
- **HANYA** `secrets` module untuk: key, IV, nonce, salt, challenge
- `random` module **HANYA** untuk non-security (test data, demo)
- `hashing.py:generate_random_bytes()` sudah pakai `secrets.token_bytes()` ✓

---

## 3. Constant-Time Comparison
- **WAJIB** `hmac.compare_digest(a, b)` untuk:
  - HMAC verification (`hmac_verify`)
  - Hash integrity check (`hash_verify_integrity`)
  - Password/hash compare
- **JANGAN** `==`, `!=`, `in` untuk secret comparison

---

## 4. Weak Algorithm Handling
| Algorithm | Status | Required Action |
|-----------|--------|-----------------|
| MD5 | Legacy | Warning banner saat dipilih |
| SHA-1 | Legacy | Warning banner saat dipilih |
| DES | Legacy | Warning banner + prefer AES |
| RC2/ARC2 | Deprecated | Warning banner + hide default |
| ECB Mode | Insecure | Warning banner + prefer CBC/GCM |
| RSA PKCS#1 v1.5 | Legacy | Warning + prefer OAEP/PSS |

---

## 5. KDF Parameters
- **PBKDF2**: Minimum 100,000 iterations (enforce di code)
- **Bcrypt**: Cost range 4-31 (validate, default 12)
- **Scrypt/Argon2**: Tidak tersedia → dokumentasikan gap

---

## 6. Padding & Error Handling
- Padding oracle risk: **JANGAN** bedakan error "padding invalid" vs "decrypt failed"
- Semua decrypt error → generic `DecryptionError` tanpa detail
- IV/nonce reuse detection where possible

---

## 7. Input Validation
- Key length: enforce exact size (AES-128=16, AES-256=32, DES=8)
- IV length: enforce per mode (CBC=16, GCM=12)
- Reject weak keys (all zeros, all same byte) with warning

---

## 8. Output Sanitization
- CLI/Interactive output: **strip** key/IV dari display
- History log: **mask** sensitive params
- Debug mode: opt-in only, not default

---

## 9. Dependency Security
- `pycryptodome` → pin version, monitor CVE
- No `eval`, `exec`, `pickle` untrusted data
- Subprocess: avoid, if needed use `subprocess.run` with list args

---

## 10. Compliance Checklist per Release
- [ ] No secrets in logs/history
- [ ] All verify uses `hmac.compare_digest`
- [ ] Weak algos have warnings
- [ ] KDF params meet minimum
- [ ] Error messages generic
- [ ] Dependencies scanned (`pip-audit` or `safety`)

---

*Ref: AUDIT_REPORT.md Section 4 untuk detail temuan per file:line*