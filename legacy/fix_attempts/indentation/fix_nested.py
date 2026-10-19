with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_process_fn = False
in_input_fn = False

for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Track entering/leaving process_fn
    if stripped.startswith('def process_fn('):
        in_process_fn = True
        new_lines.append(line)
        continue
    elif stripped.startswith('def input_fn('):
        in_input_fn = True
        new_lines.append(line)
        continue
    elif in_process_fn or in_input_fn:
        # Check if we're leaving the function (next def at indent 4 or less, or run_action)
        if indent <= 4 and stripped and not stripped.startswith('#') and not stripped.startswith(' '):
            in_process_fn = False
            in_input_fn = False
    
    new_lines.append(line)

# Now fix if/else bodies inside nested functions
final_lines = []
i = 0
while i < len(new_lines):
    line = new_lines[i]
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    final_lines.append(line)
    
    # If this line is an if/elif/else/for/while/try/except/with at indent 8
    if indent == 8 and stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
        # Next non-empty, non-comment line should be at indent 12
        j = i + 1
        while j < len(new_lines):
            next_line = new_lines[j]
            next_stripped = next_line.lstrip()
            next_indent = len(next_line) - len(next_stripped)
            if next_stripped and not next_stripped.startswith('#'):
                if next_indent == 8:
                    # Fix: change indent from 8 to 12 in final_lines (which will be the next appended)
                    # We need to modify the next line when we get to it
                    # Store a flag
                    final_lines.append('__FIX_NEXT__')
                break
            j += 1
    i += 1

# Actually, let's do a simpler single-pass approach
with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))

print('Fixed')