with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    lines = f.readlines()

new_lines = []

for i, line in enumerate(lines):
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    prev_was_def = False
    if i > 0:
        prev_line = lines[i-1]
        prev_stripped = prev_line.lstrip()
        prev_indent = len(prev_line) - len(prev_line.lstrip())
        prev_was_def = prev_line.lstrip().startswith('def ') and prev_line.rstrip().endswith('):') and 'lambda' not in prev_line
    else:
        prev_was_def = False
    
    # If previous line was a function definition and current line is at indent 4 (first line of body)
    if prev_was_def and lines[i].strip() and indent == 4:
        line = '    ' + line
    
    new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.writelines(new_lines)
print('Fixed')