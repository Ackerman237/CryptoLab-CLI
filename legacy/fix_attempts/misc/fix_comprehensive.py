with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Fix: dedent lines that are over-indented in handler functions
    # Target: lines at indent 12 that should be at 8 (nested function bodies)
    # Lines at 16 that should be at 8
    # Lines at 12 that should be at 8 (for else:, if bodies)
    # Lines at 16 that should be at 8
    
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    if not line.strip() or stripped.startswith('#'):
        new_lines.append(line)
        continue
    
    # Fix: dedent lines that are at 12 but should be at 8 (function bodies at level 2)
    if indent == 12 and stripped and not stripped.startswith('#'):
        # Check if this is a function definition (should be at 4, not 12)
        if stripped.startswith('def ') and stripped.endswith('):'):
            # Function definition at 12 -> 4
            new_lines.append(' ' * 4 + stripped + ('\n' if line.endswith('\n') else ''))
            continue
        elif indent == 12:
            # Body at 12 -> should be 8
            new_lines.append(' ' * 8 + stripped + ('\n' if line.endswith('\n') else ''))
            continue
        elif indent == 16:
            # Lines at 16 -> 8
            new_lines.append(' ' * 8 + stripped + ('\n' if line.endswith('\n') else ''))
            continue
        elif indent == 16:
            new_lines.append('        ' + stripped)
            continue
    
    # Fix else: at 12 -> 8
    if indent == 12 and stripped == 'else:':
        new_lines.append('        else:\n')
        continue
    
    # Fix run_action at 8 -> 4
    if indent == 8 and stripped.startswith('run_action('):
        new_lines.append('    ' + stripped)
        continue
    
    # Fix list items at 12 -> 8
    if indent == 12 and stripped.startswith('{"key":'):
        new_lines.append('        ' + stripped)
        continue
    
    # Fix closing brackets at 8 -> 4
    if indent == 8 and stripped.startswith('])'):
        new_lines.append('    ])')
        continue
    if indent == 12 and stripped == '}]':
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
    elif indent == 28 and stripped.startswith('lambda '):
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
    elif indent == 28 and stripped.startswith('lambda '):
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

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))
print('Fixed')