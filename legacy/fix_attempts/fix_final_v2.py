with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

lines = content.splitlines(keepends=True)
new_lines = []
for line in content.splitlines(keepends=True):
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    if line.strip() == '' or line.lstrip().startswith('#'):
        new_lines.append(line)
    elif line.lstrip().startswith('def ') and indent == 12:
        # Nested function at 12 -> 4
        new_lines.append('    ' + stripped)
    elif indent >= 16 and stripped and not stripped.startswith('#'):
        # Dedent body lines by 8
        new_lines.append(' ' * (indent - 8) + stripped + ('\n' if line.endswith('\n') else ''))
    elif indent == 16 and stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ')):
        new_lines.append('        ' + stripped)
    elif indent == 16 and stripped == 'else:':
        new_lines.append('        else:\n')
    elif indent == 20 and stripped.startswith('return '):
        new_lines.append('            ' + stripped)
    elif indent == 20 and stripped.startswith('result.'):
        new_lines.append('            ' + stripped)
    elif indent == 20 and stripped.startswith('print('):
        new_lines.append('            ' + stripped)
    elif indent == 20 and '=' in stripped and not stripped.startswith('#'):
        new_lines.append('            ' + stripped)
    elif indent == 20 and stripped.startswith('#'):
        new_lines.append('            ' + stripped)
    elif indent == 8 and stripped.startswith('run_action('):
        new_lines.append('    ' + stripped)
    elif indent == 12 and stripped.startswith('{"key":'):
        new_lines.append('        ' + stripped)
    elif indent == 8 and stripped.startswith('])'):
        new_lines.append('    ])')
    elif indent == 12 and stripped == '}]':
        new_lines.append('        }]')
    elif indent == 28 and stripped.startswith('lambda '):
        new_lines.append('                        ' + stripped)
    else:
        new_lines.append(line)

content = ''.join(new_lines)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.write(content)
print('Fixed')