import re

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The file has a consistent pattern: all handler functions have their bodies indented 4 spaces too deep
# Pattern:
# def handle_xxx() -> None:  # at 0
#     def input_fn():        # at 4 (correct)
#         body at 8 (correct)
#     def process_fn(inputs): at 8 (should be 4)
#     body at 8 (should be 12) -> but currently at 8
#     run_action at 8 (should be 4)
#     list items at 12 (should be 8)
#     ]]) at 4 (correct)

# The issue: all nested functions (input_fn, process_fn) are at 8 instead of 4
# Their bodies at 8 instead of 8 (wait, for def at 4, body should be 8)
# Actually: def at 4, body at 8 (correct for def at 4)
# But def at 8, body at 8 (should be 12)

# The issue: nested functions (input_fn, process_fn) are at 8 instead of 4
# Their bodies at 8 (should be 8 if def at 4, but def at 8 so body should be 12)
# run_action at 8 should be 4
# List items at 12 should be 8

# The root cause: the entire body of each handler function is indented by 4 extra spaces
# Handler function at 0, body should start at 4
# But body starts at 8 (4 extra)
# So nested functions at 8 (should be 4), bodies at 12 (should be 8)
# run_action at 8 (should be 4)
# List items at 12 (should be 8)
# Closing brackets at 4 (correct)

# Fix: dedent the entire body of each handler function by 4 spaces
# But only for the handler functions (handle_*), not for module-level code

import re

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Split by handler functions
# Pattern: ^def handle_\w+\(\) -> None:\n
parts = re.split(r'(^def handle_\w+\(\) -> None:\n)', content, flags=re.MULTILINE)

new_parts = [parts[0]]  # imports and preamble

for i in range(1, len(parts), 2):
    func_def = parts[i]
    body = parts[i+1] if i+1 < len(parts) else ''
    
    # Dedent the function body by 4 spaces (from 4 to 0 for body start)
    # But careful: the function def is at 0, body starts at 4
    # Currently body starts at 8 (4 extra)
    # So dedent body by 4 spaces
    
    body_lines = body.splitlines(keepends=True)
    new_body_lines = []
    in_handler = True
    
    for line in body_lines:
        if line.strip() == '' or line.lstrip().startswith('#'):
            new_body_lines.append(line)
            continue
        
        indent = len(line) - len(line.lstrip())
        stripped = line.lstrip()
        
        # Check if we've exited the handler function (next top-level def or class)
        if indent == 0 and stripped.startswith('def ') and not line.startswith('    '):
            # End of handler function
            new_lines.append(line)
            break
        
        # Dedent by 4 spaces for lines that are at indent >= 4
        if indent >= 4 and stripped and not stripped.startswith('#'):
            # But don't dedent the handler function definition itself (at 0)
            # Only dedent lines that are inside the handler (indent >= 4)
            if indent >= 4:
                new_lines.append(' ' * (indent - 4) + line.lstrip())
                continue
        
        new_lines.append(line)
    
    new_body = ''.join(new_body_lines)
    new_parts.append(func_def)
    new_parts.append(new_body)

new_content = ''.join(new_parts)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed')