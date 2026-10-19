with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    lines = f.readlines()

new_lines = []
prev_line_was_def = False

for i, line in enumerate(open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r').readlines()):
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Check if previous line was a function definition
    if i > 0 and len(new_lines) > 0:
        prev_line = lines[i-1]
        prev_stripped = new_lines[-1].lstrip() if new_lines else ''
        prev_indent = len(new_lines[-1]) - len(new_lines[-1].lstrip()) if new_lines else 0
        
        # Check if previous line was a function definition
        prev_stripped = new_lines[-1].lstrip() if new_lines else ''
        prev_indent = len(new_lines[-1]) - len(new_lines[-1].lstrip()) if new_lines else 0
        
        prev_was_def = new_lines[-1].lstrip().startswith('def ') and new_lines[-1].rstrip().endswith('):') if new_lines else False
    else:
        prev_was_def = False
    
    # This approach is getting too complex. Let me use a simpler method.
    pass