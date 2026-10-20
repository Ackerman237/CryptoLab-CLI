"""Unit tests for interactive terminal menu, input validation, and navigation.

Karakterisasi UI pasca-rombak (menu 3-elemen + navigasi panah):

- Menu navigasi (``navigation_menu`` / ``Menu.run``) membaca input via
  ``readchar.readkey()`` — dimock di sini lewat fixture ``ui``.
- Prompt teks (``Prompt.ask``) membaca via ``builtins.input`` — dimock juga.
- Menu utama (``run_interactive_menu``) memakai ``read_key`` dari
  ``cryptolab.interactive`` — dimock terpisah.

Script input yang habis membangkitkan ``ScriptExhausted`` (BaseException)
supaya bug skrip tes gagal cepat, TIDAK tertelan ``except Exception`` di
handler, dan TIDAK menggantung seperti readchar blocking.
"""

from collections import deque

import pytest


class ScriptExhausted(BaseException):
    """Input habis — sengaja BaseException agar tidak tertelan handler."""


class UIScript:
    """Scripted input terpusat: tombol (readchar) + baris teks (input)."""

    def __init__(self):
        self.keys = deque()
        self.lines = deque()

    # --- scripting (dipakai tes) ---
    def press(self, *keys):
        """Tombol menu: 'enter', 'down', 'up', 'end', atau karakter tunggal."""
        self.keys.extend(keys)
        return self

    def type(self, *texts):
        """Baris teks untuk Prompt.ask / builtins.input."""
        self.lines.extend(texts)
        return self

    # --- konsumsi (dipakai aplikasi) ---
    #: nama tombol ramah -> konstanta readchar.key (dipakai Menu.run & read_key)
    _NAMES = None

    @classmethod
    def _names(cls):
        if cls._NAMES is None:
            from readchar import key as rk

            cls._NAMES = {
                "up": rk.UP,
                "down": rk.DOWN,
                "left": rk.LEFT,
                "right": rk.RIGHT,
                "home": getattr(rk, "HOME", "\x1b[H"),
                "end": getattr(rk, "END", "\x1b[F"),
                "enter": rk.ENTER,
                "esc": rk.ESC,
                "pgup": getattr(rk, "PAGE_UP", "\x1b[5~"),
                "pgdn": getattr(rk, "PAGE_DOWN", "\x1b[6~"),
            }
        return cls._NAMES

    def readkey(self):
        if not self.keys:
            raise ScriptExhausted("key script habis (readchar.readkey)")
        k = self.keys.popleft()
        # Nama ramah ("enter", "down", ...) diterjemahkan ke konstanta readchar
        # agar cocok untuk Menu.run (perbandingan langsung) maupun _normalize_key.
        return self._names().get(k, k)

    def read_line(self, prompt=""):
        if not self.lines:
            raise ScriptExhausted("line script habis (builtins.input)")
        print(prompt, end="")
        return self.lines.popleft()


@pytest.fixture
def ui(monkeypatch):
    """Mock dua jalur input UI: readchar (menu) + builtins.input (prompt)."""
    script = UIScript()

    import readchar

    monkeypatch.setattr(readchar, "readkey", script.readkey)
    monkeypatch.setattr("builtins.input", script.read_line)
    # read_key (menu utama) memanggil readchar.readkey() yang sudah di-patch
    # di atas, sehingga normalisasi _normalize_key tetap berjalan seperti aslinya.
    return script


class TestInteractive:
    """Test suite for interactive CLI menus."""

    @pytest.fixture(autouse=True)
    def clean_hist(self):
        from cryptolab import clear_history

        clear_history()
        yield
        clear_history()

    # ============================================================
    # Menu utama (run_interactive_menu)
    # ============================================================
    def test_menu_exit_with_9(self, ui, capsys):
        # Semula tombol angka '9'; menu baru keluar via 'q'.
        from cryptolab import run_interactive_menu

        ui.press("q")
        run_interactive_menu()
        captured = capsys.readouterr().out
        assert "Sampai jumpa" in captured

    def test_menu_exit_with_0(self, ui, capsys):
        # Semula angka '0'; menu baru: navigasi ke item "Keluar" lalu Enter.
        from cryptolab import run_interactive_menu

        ui.press("end", "enter")
        run_interactive_menu()
        captured = capsys.readouterr().out
        assert "Sampai jumpa" in captured

    def test_menu_invalid_input_retries(self, ui, capsys):
        # Input tak dikenal diabaikan tanpa crash; menu tetap berfungsi.
        from cryptolab import run_interactive_menu

        ui.press("x", "9", "?", "q")
        run_interactive_menu()
        captured = capsys.readouterr().out
        assert "Sampai jumpa" in captured

    # ============================================================
    # Caesar
    # ============================================================
    def test_caesar_interactive_encrypt_and_decrypt(self, ui, capsys):
        from cryptolab import handle_caesar

        # Enkripsi "Halo" shift 3 -> ulangi -> Dekripsi "Kdor" shift 3 -> kembali.
        ui.press("enter", "enter", "down", "enter", "b")
        ui.type("Halo", "3", "Kdor", "3")
        handle_caesar()
        captured = capsys.readouterr().out
        assert "Kdor" in captured
        assert "Halo" in captured

    def test_caesar_interactive_brute_force(self, ui, capsys):
        from cryptolab import handle_caesar

        # Brute Force (opsi 3) -> "KHOOR" -> kandidat terbaik saja -> kembali.
        ui.press("down", "down", "enter", "b")
        ui.type("KHOOR", "y")
        handle_caesar()
        captured = capsys.readouterr().out
        assert "HELLO" in captured

    # ============================================================
    # Vigenere
    # ============================================================
    def test_vigenere_interactive(self, ui, capsys):
        from cryptolab import handle_vigenere

        # Enkripsi -> "ATTACK"/"LEMON" -> kembali.
        ui.press("enter", "b")
        ui.type("ATTACK", "LEMON")
        handle_vigenere()
        captured = capsys.readouterr().out
        assert "LXFOPV" in captured

    def test_vigenere_invalid_key_recovery(self, ui, capsys):
        from cryptolab import handle_vigenere

        # Key tidak valid "123!" -> ulangi -> key valid "KEY" -> kembali.
        ui.press("enter", "enter", "b")
        ui.type("Hello", "123!", "Hello", "KEY")
        handle_vigenere()
        captured = capsys.readouterr().out
        assert "huruf alfabet" in captured
        assert "Rijvs" in captured

    # ============================================================
    # Encoding
    # ============================================================
    def test_base64_interactive(self, ui, capsys):
        from cryptolab import handle_base64

        # Encode "Testing" -> ulangi -> Decode -> kembali.
        ui.press("enter", "enter", "down", "enter", "b")
        ui.type("Testing", "VGVzdGluZw==")
        handle_base64()
        captured = capsys.readouterr().out
        assert "VGVzdGluZw==" in captured
        assert "Testing" in captured

    def test_hex_interactive(self, ui, capsys):
        from cryptolab import handle_hex

        # Encode "Lab" (pemisah default) -> ulangi -> Decode -> kembali.
        ui.press("enter", "enter", "down", "enter", "b")
        ui.type("Lab", "", "4c 61 62")
        handle_hex()
        captured = capsys.readouterr().out
        assert "4c 61 62" in captured
        assert "Lab" in captured

    def test_binary_interactive(self, ui, capsys):
        from cryptolab import handle_binary

        # Encode "A" (pemisah default) -> ulangi -> Decode -> kembali.
        ui.press("enter", "enter", "down", "enter", "b")
        ui.type("A", "", "01000001")
        handle_binary()
        captured = capsys.readouterr().out
        assert "01000001" in captured
        assert "A" in captured

    # ============================================================
    # DES
    # ============================================================
    def test_des_interactive_cbc_decrypt(self, ui, capsys):
        from cryptolab import handle_des

        # Dekripsi -> CBC -> ct/key/iv -> PKCS7 -> kembali -> keluar.
        ui.press("enter", "down", "enter", "enter", "b", "b")
        ui.type("5828b071ff8b9fe9f28e2f22bd9c3f21", "abcdefgh", "hgfedcba")
        handle_des()
        captured = capsys.readouterr().out
        assert "des_enkripsi" in captured
        assert "CBC" in captured

    def test_des_interactive_ecb_decrypt(self, ui, capsys):
        from cryptolab import handle_des

        # Dekripsi -> ECB (tanpa IV) -> padding None -> kembali -> keluar.
        ui.press("enter", "down", "down", "enter", "down", "enter", "b", "b")
        ui.type("5828b071ff8b9fe9f28e2f22bd9c3f21", "abcdefgh")
        handle_des()
        captured = capsys.readouterr().out
        assert "ECB" in captured

    def test_des_interactive_auto_mode(self, ui, capsys):
        from cryptolab import handle_des

        # Dekripsi -> Auto -> ct/key/iv -> kembali -> keluar.
        ui.press("enter", "enter", "b", "b")
        ui.type("5828b071ff8b9fe9f28e2f22bd9c3f21", "abcdefgh", "hgfedcba")
        handle_des()
        captured = capsys.readouterr().out
        assert "des_enkripsi" in captured
        assert "HASIL ANALISIS DES" in captured

    # ============================================================
    # Auto Analyze
    # ============================================================
    def test_auto_analyze_keyless_flow(self, ui, capsys):
        from cryptolab import handle_auto_analyze

        # Flag Base64 -> Enter skip key -> kembali.
        flag_b64 = "RkxBR3tjcnlwdG9fbGFiXzIwMjR9"  # FLAG{crypto_lab_2024} in base64
        ui.press("b")
        ui.type(flag_b64, "")
        handle_auto_analyze()
        captured = capsys.readouterr().out
        assert "FLAG{crypto_lab_2024}" in captured

    def test_auto_analyze_des_challenge_flow(self, ui, capsys):
        from cryptolab import handle_auto_analyze

        # Ciphertext DES -> key -> IV -> kembali.
        ui.press("b")
        ui.type("5828b071ff8b9fe9f28e2f22bd9c3f21", "abcdefgh", "hgfedcba")
        handle_auto_analyze()
        captured = capsys.readouterr().out
        assert "des_enkripsi" in captured

    def test_auto_analyze_rc2_challenge_flow(self, ui, capsys):
        from cryptolab import handle_auto_analyze

        # Ciphertext RC2 -> key -> IV -> kembali.
        ui.press("b")
        ui.type(
            "c73ded509ad5c3039cf3cb63ce5448d1ace59962c45889a23ab61bb826eeebf8",
            "12345678",
            "qwertyui",
        )
        handle_auto_analyze()
        captured = capsys.readouterr().out
        assert "laboratorium_keamanan_3d" in captured
        assert "RC2 (CBC, Padding PKCS7)" in captured

    # ============================================================
    # History & util
    # ============================================================
    def test_history_interactive_view_and_clear(self, ui, capsys):
        from cryptolab import handle_history

        # Bersihkan riwayat -> konfirmasi "y" -> kembali.
        ui.press("enter", "b")
        ui.type("y")
        handle_history()
        captured = capsys.readouterr().out
        assert "berhasil dibersihkan" in captured

    def test_save_result_prompt(self, monkeypatch, tmp_path):
        from cryptolab import save_result_prompt

        target_file = tmp_path / "test_output.txt"
        inputs = iter(["y", str(target_file)])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        save_result_prompt("Teks Konten Uji Coba")
        assert target_file.exists()
        assert target_file.read_text(encoding="utf-8") == "Teks Konten Uji Coba"

    def test_back_navigation_with_b(self, ui, capsys):
        from cryptolab import handle_caesar

        # Tekan 'b' di menu pertama -> langsung kembali tanpa error.
        ui.press("b")
        handle_caesar()
        captured = capsys.readouterr().out
        assert "CAESAR CIPHER" in captured
