with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_nested_fn = False
control_stack = []  # stack of (line_index, expected_indent)

for i, line in enumerate(lines):
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    
    # Track entering nested functions
    if stripped.startswith('def process_fn(') or stripped.startswith('def input_fn('):
        in_nested_fn = True
        control_stack = []
        new_lines.append(line)
        continue
    elif in_nested_fn and indent <= 4 and stripped and not stripped.startswith('#'):
        # Leaving nested function
        in_nested_fn = False
        control_stack = []
    
    if in_nested_fn:
        # Check for control statements at indent 8
        if indent == 8 and stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
            control_stack.append((len(new_lines), 12))  # body should be at indent 12
            new_lines.append(line)
            continue
        
        # Check if we're at a line that should be indented due to control statement
        if control_stack and stripped and not stripped.startswith('#'):
            expected_indent = control_stack[-1][1]
            if indent == 8 and expected_indent == 12:
                # Fix: indent to 12
                new_lines.append(' ' * 12 + stripped + '\n')
                # Pop if this is not a compound statement
                if not stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
                    control_stack.pop()
                continue
            elif indent > 8:
                # Already properly indented or deeper
                new_lines.append(line)
                continue
        
        # Handle else: at indent 8
        if indent == 8 and stripped == 'else:':
            new_lines.append(line)
            continue
    
    new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))

print('Fixed')