#!/usr/bin/env python3
"""
Fix indentation in interactive.py for all handler functions.
The issue: handler functions have their bodies indented 4 spaces too deep.
- Handler functions at module level (indent 0)
- Their bodies should start at 4 spaces
- Nested functions (input_fn, process_fn) should be at 4 spaces
- Their bodies at 8 spaces
- run_action calls at 4 spaces
- List items at 8 spaces
- Closing brackets at 4 spaces
"""

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_handler = False
handler_base_indent = 0

for i, line in enumerate(open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8')):
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Detect handler function definition
    if line.lstrip().startswith('def handle_') and line.rstrip().endswith('):\n') and len(line) - len(line.lstrip()) == 0:
        in_handler = True
        handler_base = 0
        new_lines.append(line)
        continue
    
    # Detect end of handler function (next function at module level or end of file)
    if in_handler and line.strip() and not line.lstrip().startswith('#'):
        if len(line) - len(line.lstrip()) == 0 and line.lstrip().startswith('def '):
            in_handler = False
    
    if in_handler:
        # We're inside a handler function
        # The function body should be at indent 4
        # Nested functions at 4, their bodies at 8
        # run_action at 4, list items at 8, closing brackets at 4
        
        stripped = line.lstrip()
        indent = len(line) - len(line.lstrip())
        
        if line.strip() == '' or line.lstrip().startswith('#'):
            new_lines.append(line)
            continue
        
        # Dedent nested function definitions (at 8 -> 4)
        if line.lstrip().startswith('def ') and line.rstrip().endswith('):\n') and indent == 8:
            new_lines.append('    ' + line.lstrip())
            continue
        
        # Dedent function bodies (at 12 -> 8, 16->8, 20->12, etc.)
        if indent >= 12 and line.strip() and not line.lstrip().startswith('#'):
            # Check if we're inside a nested function (not at module level)
            new_line = ' ' * (indent - 4) + line.lstrip()
            new_lines.append(line[:len(line)-len(line.lstrip()) - 4] + line.lstrip())
            continue
        
        # Fix else: at 8 -> 4
        if indent == 8 and line.lstrip() == 'else:':
            new_lines.append('    else:\n')
            continue
        
        # Fix if/elif/else/for/while at 16 -> 8
        if indent == 16 and (line.lstrip().startswith('if ') or line.lstrip().startswith('elif ') or line.lstrip().startswith('for ') or line.lstrip().startswith('while ')):
            new_lines.append('        ' + line.lstrip())
            continue
        
        # Fix else: at 16
        if indent == 16 and line.lstrip() == 'else:':
            new_lines.append('        else:\n')
            continue
        
        # Fix return/result.add/print/assignments at 20 -> 12
        if indent == 20 and (line.lstrip().startswith('return ') or line.lstrip().startswith('result.') or line.lstrip().startswith('print(') or ('=' in line and not line.lstrip().startswith('#'))):
            new_lines.append('            ' + line.lstrip())
            continue
        
        # Fix comments at 20
        if indent == 20 and line.lstrip().startswith('#'):
            new_lines.append('            ' + line.lstrip())
            continue
        
        # Fix run_action at 8 -> 4
        if indent == 8 and line.lstrip().startswith('run_action('):
            new_lines.append('    ' + line.lstrip())
            continue
        
        # Fix list items at 12 -> 8
        if indent == 12 and line.lstrip().startswith('{"key":'):
            new_lines.append('        ' + line.lstrip())
            continue
        
        # Fix closing brackets at 8 -> 4
        if indent == 8 and stripped.startswith('])'):
            new_lines.append('    ])')
            continue
        
        # Fix closing braces at 12 -> 8
        if indent == 12 and line.lstrip() == '}]':
            new_lines.append('        }]')
            continue
        
        # Fix lambda at 28 -> 24
        if indent == 28 and stripped.startswith('lambda '):
            new_lines.append('                        ' + stripped)
            continue
        
        # Fix closing brackets at 8 -> 4
        if indent == 8 and stripped.startswith('])'):
            new_lines.append('    ])')
            continue
        
        # Fix closing braces at 12 -> 8
        if indent == 12 and stripped == '}]':
            new_lines.append('        }]')
            continue
        
        # Fix lambda at 28 -> 24
        if indent == 28 and stripped.startswith('lambda '):
            new_lines.append('                        ' + stripped)
            continue
        
        # Fix closing brackets at 8 -> 4
        if indent == 8 and stripped.startswith('])'):
            new_lines.append('    ])')
            continue
        
        # Fix closing braces at 12 -> 8
        if indent == 12 and stripped == '}]':
            new_lines.append('        }]')
            continue
        
        # Fix lambda at 28 -> 24
        if indent == 28 and stripped.startswith('lambda '):
            new_lines.append('                        ' + stripped)
            continue
        
        # Fix closing brackets at 8 -> 4
        if indent == 8 and stripped.startswith('])'):
            new_lines.append('    ])')
            continue
        
        # Fix closing braces at 12 -> 8
        if indent == 12 and stripped == '}]':
            new_lines.append('        }]')
            continue
        
        # Fix lambda at 28 -> 24
        if indent == 28 and stripped.startswith('lambda '):
            new_lines.append('                        ' + stripped)
            continue
        elif indent == 8 and stripped.startswith('])'):
            new_lines.append('    ])')
            continue
        elif indent == 12 and stripped == '}]':
            new_lines.append('        }]')
            continue
        elif indent == 28 and stripped.startswith('lambda '):
            new_lines.append('                        ' + stripped)
            continue
        elif indent == 8 and stripped.startswith('])'):
            new_lines.append('    ])')
            continue
        elif indent == 12 and stripped == '}]':
            new_lines.append('        }]')
            continue
        else:
            new_lines.append(line)
            continue
    else:
        new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))
print('Fixed')