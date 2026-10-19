import re

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

# Split by handler function definitions
parts = re.split(r'(^def handle_\w+\(\) -> None:\n)', content, flags=re.MULTILINE)

new_parts = [parts[0]]  # imports and preamble

for i in range(1, len(parts), 2):
    func_def = parts[i]
    body = parts[i+1] if i+1 < len(parts) else ''
    
    # Dedent function body by 4 spaces (from 8 to 4, 12 to 8, etc.)
    body_lines = body.splitlines(keepends=True)
    new_body_lines = []
    for line in body_lines:
        if line.strip() == '' or line.lstrip().startswith('#'):
            new_body_lines.append(line)
        elif line.startswith('    run_action(') and line.startswith('    '):
            new_body_lines.append(line)
        elif line.startswith('    ])\n') or line.startswith('    }]'):
            new_body_lines.append(line)
        elif line.startswith('        '):  # 8 spaces -> 4 spaces
            new_body_lines.append(line[4:])
        else:
            new_body_lines.append(line)
    
    new_body = ''.join(new_body_lines)
    new_parts.append(func_def)
    new_parts.append(new_body)

new_content = ''.join(new_parts)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.write(content)

print('Fixed')