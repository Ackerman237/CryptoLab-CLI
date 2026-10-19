with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_nested_fn = False

for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    
    # Track entering nested functions
    if stripped.startswith('def process_fn(') or stripped.startswith('def input_fn('):
        in_nested_fn = True
        new_lines.append(line)
        continue
    elif in_nested_fn and indent <= 4 and stripped and not stripped.startswith('#'):
        in_nested_fn = False
    
    if in_nested_fn:
        # Fix: else: at indent 12 should be at indent 8
        if indent == 12 and stripped == 'else:':
            new_lines.append('        else:\n')
            continue
        # Fix: elif at indent 12 should be at indent 8
        elif indent == 12 and stripped.startswith('elif '):
            new_lines.append('        ' + stripped + '\n')
            continue
    
    new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))

print('Fixed')