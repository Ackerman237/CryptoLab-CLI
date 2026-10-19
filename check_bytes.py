with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'rb') as f:
    content = f.read()

idx = content.find(b'run_action("Affine Cipher"')
if idx >= 0:
    start = max(0, idx - 50)
    end = idx + 50
    context = content[start:end]
    for i, b in enumerate(context):
        if b == 10:
            print('[%d] NL' % i)
        elif b == 13:
            print('[%d] CR' % i)
        elif b == 32:
            print('[%d] SP' % i)
        elif b == 9:
            print('[%d] TAB' % i)
        else:
            if 32 <= b < 127:
                print('[%d] %s' % (i, chr(b)))
            else:
                print('[%d] 0x%02x' % (i, b))