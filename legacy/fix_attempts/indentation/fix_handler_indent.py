with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_handler = False
handler_level = 0

for i, line in enumerate(open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r').readlines()):
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Detect handler function definitions (at module level)
    if line.lstrip().startswith('def handle_') and len(line) - len(line.lstrip()) == 0:
        in_handler = True
        handler_level = 0
        new_lines.append(line)
        continue
    
    # Detect end of handler function (next function at module level or end of file)
    if in_handler and len(line) - len(line.lstrip()) == 0 and line.strip() and not line.lstrip().startswith('#') and not line.lstrip().startswith('def '):
        in_handler = False
    
    if not in_handler:
        new_lines.append(line)
        continue
    
    # Inside a handler function
    # Nested function definitions should be at 4 spaces
    if line.lstrip().startswith('def ') and indent == 8:
        # Nested function at 8 -> should be 4
        new_lines.append('    ' + line.lstrip())
        continue
    elif indent == 4 and line.lstrip().startswith('def '):
        # Already correct
        new_lines.append(line)
        continue
    
    # Fix indentation inside handler functions
    if indent >= 12 and line.strip() and not line.lstrip().startswith('#'):
        # Dedent by 4 spaces
        new_lines.append(' ' * (indent - 4) + line.lstrip())
        continue
    elif indent == 8 and line.lstrip().startswith(('if ', 'elif ', 'else:', 'for ', 'while ')):
        new_lines.append('    ' + line.lstrip())
        continue
    elif indent == 12 and line.lstrip().startswith(('if ', 'elif ', 'else:', 'for ', 'while ')):
        new_lines.append('        ' + line.lstrip())
        continue
    elif indent == 12 and line.lstrip() == 'else:':
        new_lines.append('        else:\n')
        continue
    elif indent == 16 and line.lstrip().startswith(('if ', 'elif ', 'else:', 'for ', 'while ')):
        new_lines.append('        ' + line.lstrip())
        continue
    elif indent == 16 and line.lstrip() == 'else:':
        new_lines.append('        else:\n')
        continue
    elif indent == 20:
        new_lines.append(' ' * 12 + line.lstrip())
        continue
    elif indent == 16 and line.lstrip() == 'else:':
        new_lines.append('        else:\n')
        continue
    elif indent == 16 and line.lstrip().startswith(('if ', 'elif ', 'for ', 'while ')):
        new_lines.append('        ' + line.lstrip())
        continue
    
    new_lines.append(line)

# This approach is getting too complex. Let me use a simpler strategy:
# The issue is that all handler functions have their bodies indented by 4 extra spaces.
# The fix: for each handler function, dedent its entire body by 4 spaces.

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

# Split by handler functions
# Find all handle_* functions and fix their indentation
import re

# Split by handler functions
# Pattern: ^def handle_\w+\(\) -> None:
# Everything between handler functions should be dedented by 4 spaces

parts = re.split(r'(^def handle_\w+\(\) -> None:\n)', content, flags=re.MULTILINE)
# parts[0] is before first handler (imports)
# parts[1], parts[2], ... alternate between function def and body

# This is getting too complex. Let me use a different approach.
# Read the file, find all handler functions, and fix their indentation.

print("Analysis complete")