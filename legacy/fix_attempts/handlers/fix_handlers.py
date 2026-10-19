import re

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

# Split by handler functions
# Pattern: ^def handle_\w+\(\) -> None:
parts = re.split(r'(^def handle_\w+\(\) -> None:\n)', content, flags=re.MULTILINE)

# parts[0] = imports and preamble
# parts[1] = "def handle_hmac() -> None:\n"
# parts[2] = body of handle_hmac
# parts[3] = "def handle_pbkdf2()..."
# etc.

new_parts = [parts[0]]  # imports

for i in range(1, len(parts), 2):
    func_def = parts[i]  # "def handle_xxx() -> None:\n"
    body = parts[i+1] if i+1 < len(parts) else ''
    
    # Dedent the function body by 4 spaces (remove 4 spaces from each line)
    body_lines = body.splitlines(keepends=True)
    new_body_lines = []
    for line in body_lines:
        if line.strip() == '' or line.lstrip().startswith('#'):
            new_body_lines.append(line)
        elif len(line) - len(line.lstrip()) >= 8:
            # Dedent by 4 spaces (from 8 to 4, 12 to 8, etc.)
            new_body_lines.append(line[4:] if line.startswith(' ' * 8) else line)
        elif line.startswith('    run_action(') and line.startswith('    '):
            # run_action at 4 spaces - keep as is
            new_body_lines.append(line)
        elif line.startswith('    ])\n') or line.startswith('    }]'):
            new_body_lines.append(line)
        else:
            new_body_lines.append(line)
    
    new_body = ''.join(new_body_lines)
    new_parts.append(func_def)
    new_parts.append(new_body)

# Rejoin
new_content = ''.join(new_parts)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.write(content)

print('Fixed')