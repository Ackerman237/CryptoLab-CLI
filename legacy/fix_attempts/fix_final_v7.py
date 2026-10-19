with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    if indent >= 12 and line.strip() and not stripped.startswith('#'):
        # Dedent by 4 spaces for over-indented lines
        new_line = ' ' * (indent - 4) + line.lstrip()
        if line.endswith('\n'):
            new_lines.append(' ' * (indent - 4) + stripped + '\n')
        else:
            new_lines.append(' ' * (indent - 4) + stripped)
        continue
    
    if indent == 8 and (line.lstrip().startswith('if ') or line.lstrip().startswith('elif ') or line.lstrip() == 'else:' or line.lstrip().startswith('for ') or line.lstrip().startswith('while ')):
        new_lines.append('        ' + line.lstrip())
        continue
    if indent == 12 and (line.lstrip().startswith('elif ') or line.lstrip() == 'else:' or line.lstrip().startswith('for ') or line.lstrip().startswith('while ')):
        new_lines.append('        ' + line.lstrip())
        continue
    if indent == 12 and line.lstrip() == 'else:':
        new_lines.append('        else:\n')
        continue
    if indent == 16 and stripped.startswith('return '):
        new_lines.append('            ' + line.lstrip())
        continue
    if indent == 20 and (line.lstrip().startswith('return ') or line.lstrip().startswith('result.') or line.lstrip().startswith('print(') or ('=' in line and not line.lstrip().startswith('#'))):
        new_lines.append('            ' + line.lstrip())
        continue
    if indent == 20 and line.lstrip().startswith('#'):
        new_lines.append('            ' + line.lstrip())
        continue
    if indent == 8 and line.lstrip().startswith('run_action('):
        new_lines.append('    ' + line.lstrip())
        continue
    if indent == 12 and line.lstrip().startswith('{"key":'):
        new_lines.append('        ' + line.lstrip())
        continue
    if indent == 8 and line.lstrip().startswith('])'):
        new_lines.append('    ])')
        continue
    if indent == 12 and line.lstrip() == '}]':
        new_lines.append('        }]')
        continue
    elif indent == 28 and line.lstrip().startswith('lambda '):
        new_lines.append('                        ' + line.lstrip())
        continue
    elif indent == 8 and line.lstrip().startswith('])'):
        new_lines.append('    ])')
        continue
    elif indent == 12 and line.lstrip() == '}]':
        new_lines.append('        }]')
        continue
    elif indent == 28 and line.lstrip().startswith('lambda '):
        new_lines.append('                        ' + line.lstrip())
        continue
    elif indent == 8 and line.lstrip().startswith('])'):
        new_lines.append('    ])')
        continue
    elif indent == 12 and line.lstrip() == '}]':
        new_lines.append('        }]')
        continue
    elif indent == 28 and line.lstrip().startswith('lambda '):
        new_lines.append('                        ' + line.lstrip())
        continue
    elif indent == 8 and line.lstrip().startswith('])'):
        new_lines.append('    ])')
        continue
    elif indent == 12 and line.lstrip() == '}]':
        new_lines.append('        }]')
        continue
    elif indent == 28 and line.lstrip().startswith('lambda '):
        new_lines.append('                        ' + line.lstrip())
        continue
    elif indent == 8 and line.lstrip().startswith('])'):
        new_lines.append('    ])')
        continue
    elif indent == 12 and line.lstrip() == '}]':
        new_lines.append('        }]')
        continue
    elif indent == 28 and line.lstrip().startswith('lambda '):
        new_lines.append('                        ' + line.lstrip())
        continue
    elif indent == 8 and line.lstrip().startswith('])'):
        new_lines.append('    ])')
        continue
    elif indent == 12 and line.lstrip() == '}]':
        new_lines.append('        }]')
        continue
    else:
        new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))
print('Fixed')