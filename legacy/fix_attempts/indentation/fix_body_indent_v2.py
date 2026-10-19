with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    lines = f.readlines()

new_lines = []
prev_was_def = False

for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    if prev_was_def and line.strip() and len(line) - len(line.lstrip()) == 4:
        # This is the first line of a function body, indent by 4 more
        line = '    ' + line
    
    # Check if this line is a function definition
    prev_was_def = line.lstrip().startswith('def ') and line.rstrip().endswith('):')
    
    # But not if it's a lambda
    if 'lambda' in line:
        pass  # Don't set prev_was_def for lambdas
    
    new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.writelines(lines)
print('Fixed')