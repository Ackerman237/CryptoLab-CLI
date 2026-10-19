with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_handler = False
handler_start = -1

for i, line in enumerate(open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8')):
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Detect handler function start
    if line.lstrip().startswith('def handle_') and line.rstrip().endswith('):\n') and len(line) - len(line.lstrip()) == 0:
        in_handler = True
        handler_start = len(new_lines)
        new_lines.append(line)
        continue
    
    # Detect end of handler
    if in_handler:
        if line.strip() and len(line) - len(line.lstrip()) == 0 and not line.lstrip().startswith('#') and not line.lstrip().startswith(' '):
            if line.lstrip().startswith('def ') or line.lstrip().startswith('class '):
                in_handler = False
    
    if in_handler:
        stripped = line.lstrip()
        indent = len(line) - len(line.lstrip())
        
        if not stripped or stripped.startswith('#'):
            new_lines.append(line)
            continue
        
        indent = len(line) - len(line.lstrip())
        
        # Dedent by 4 for lines inside handler (indent >= 4)
        if indent >= 4 and stripped and not stripped.startswith('#'):
            new_indent = indent - 4
            new_line = ' ' * new_indent + stripped
            if line.endswith('\n'):
                new_lines.append(' ' * new_indent + stripped + '\n')
            else:
                new_lines.append(' ' * (indent - 4) + stripped)
            continue
        
        new_lines.append(line)
    else:
        new_lines.append(line)
    
    # Check for end of handler
    if in_handler:
        if line.strip() and len(line) - len(line.lstrip()) == 0 and not line.lstrip().startswith('#') and not line.lstrip().startswith(' '):
            if line.lstrip().startswith('def ') or line.lstrip().startswith('class '):
                pass  # Will be handled next iteration

# This approach has a bug with the state tracking. Let me write a proper fix.
print("Need better approach")