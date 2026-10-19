with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8').readlines()):
    line = open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8').readlines()[i]
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Detect handler function start
    if line.lstrip().startswith('def handle_') and line.rstrip().endswith('):\n') and len(line) - len(line.lstrip()) == 0:
        in_handler = True
        new_lines.append(line)
        i += 1
        while i + 1 < len(open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8').readlines()):
            i += 1
            line = open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8').readlines()[i]
            stripped = line.lstrip()
            indent = len(line) - len(line.lstrip())
            
            if not line.strip() or line.lstrip().startswith('#'):
                new_lines.append(line)
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # Check for end of handler
            if line.strip() and len(line) - len(line.lstrip()) == 0 and not line.lstrip().startswith('#') and not line.lstrip().startswith(' '):
                if line.lstrip().startswith('def ') or line.lstrip().startswith('class '):
                    new_lines.append(line)
                    break
            
            # Fix indentation
            if line.strip() and not line.lstrip().startswith('#'):
                if len(line) - len(line.lstrip()) >= 4:
                    new_indent = len(line) - len(line.lstrip()) - 4
                    new_line = ' ' * new_indent + line.lstrip()
                    if line.endswith('\n'):
                        new_lines.append(' ' * new_indent + line.lstrip() + '\n')
                    else:
                        new_lines.append(' ' * (len(line) - len(line.lstrip()) - 4) + line.lstrip())
                    continue
            
            new_lines.append(line)
            continue
        else:
            new_lines.append(line)
        continue
    else:
        new_lines.append(line)
    
    i += 1

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))
print('Fixed')