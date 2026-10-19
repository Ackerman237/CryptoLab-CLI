with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Fix: Inside process_fn and input_fn (which are at indent 4), 
# control structures (if/elif/else/for/while/try/except/with) are at indent 8,
# their bodies should be at indent 12

# Pattern: control statement at indent 8 followed by statement at indent 8 (should be 12)
# We'll fix by finding lines at indent 8 that follow control statements at indent 8

lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    
    new_lines.append(line)
    
    # Check if this is a control statement at indent 8 inside a nested function
    if indent == 8 and stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
        # Look ahead to find next non-empty, non-comment line
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            next_stripped = next_line.lstrip()
            next_indent = len(next_line) - len(next_stripped)
            if next_stripped and not next_stripped.startswith('#'):
                if next_indent == 8:
                    # This should be at indent 12 - fix it in the next iteration
                    # We'll mark it by adding a special marker
                    pass
                break
            j += 1
    i += 1

# Actually, let's do a simpler approach: just fix all lines at indent 8 that are 
# inside process_fn or input_fn and are not control statements themselves

# Read again and do a proper fix
with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_nested_fn = False  # inside process_fn or input_fn
prev_was_control = False

for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    
    # Track entering nested functions
    if stripped.startswith('def process_fn(') or stripped.startswith('def input_fn('):
        in_nested_fn = True
        prev_was_control = False
        new_lines.append(line)
        continue
    elif in_nested_fn and indent <= 4 and stripped and not stripped.startswith('#'):
        # Leaving nested function
        in_nested_fn = False
        prev_was_control = False
    
    # Track control statements
    if in_nested_fn and indent == 8 and stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
        prev_was_control = True
        new_lines.append(line)
        continue
    elif in_nested_fn and prev_was_control and indent == 8 and stripped and not stripped.startswith('#'):
        # This line should be at indent 12
        new_lines.append(' ' * 12 + stripped + '\n')
        prev_was_control = False
        continue
    elif in_nested_fn and indent == 8 and stripped.startswith(('return ', 'result', 'match', 'res =', 'expected', 'salt', 'iterations', 'dklen', 'rounds', 'password', 'encoding', 'algo', 'length')):
        # These are regular statements at indent 8 - could be after else: or standalone
        # Check if previous was else:
        if prev_was_control and stripped.startswith('else:'):
            pass  # handled above
        new_lines.append(line)
        continue
    else:
        prev_was_control = False
        new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))

print('Fixed')