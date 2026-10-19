with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'rb') as f:
    content = f.read()

# Find the run_action line
idx = content.find(b'run_action("Affine Cipher"')
if idx >= 0:
    start = max(0, idx - 50)
    end = idx + 100
    context = content[start:end]
    print(repr(context))