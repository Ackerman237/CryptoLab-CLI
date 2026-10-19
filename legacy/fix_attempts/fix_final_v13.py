with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Check if this is a handler function definition at module level
    if line.lstrip().startswith('def handle_') and line.rstrip().endswith('):\n') and len(line) - len(line.lstrip()) == 0:
        # Found handler function start
        new_lines.append(line)
        i += 1
        # Process handler body until we find the closing '])' at indent 4
        while i + 1 < len(lines):
            i += 1
            line = lines[i]
            stripped = line.lstrip()
            indent = len(line) - len(line.lstrip())
            
            if not line.strip() or line.lstrip().startswith('#'):
                new_lines.append(line)
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # Check for end of handler (next top-level def or class)
            if line.strip() and len(line) - len(line.lstrip()) == 0 and not line.lstrip().startswith('#') and not line.lstrip().startswith(' '):
                if line.lstrip().startswith('def ') or line.lstrip().startswith('class '):
                    # End of handler, add this line and break
                    new_lines.append(line)
                    break
            
            # Dedent by 4 for lines inside handler (indent >= 4)
            if indent >= 4 and line.strip() and not line.lstrip().startswith('#'):
                new_indent = indent - 4
                new_line = ' ' * (indent - 4) + line.lstrip()
                if line.endswith('\n'):
                    new_lines.append(' ' * (indent - 4) + line.lstrip() + '\n')
                else:
                    new_lines.append(' ' * (indent - 4) + line.lstrip())
                continue
            
            new_lines.append(line)
            continue
    
    # Regular line outside handlers
    new_lines.append(line)
    i += 1

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))
print('Fixed')