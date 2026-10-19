with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    lines = f.readlines()

new_lines = []
prev_was_def = False

for line in open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r'):
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Check if previous line was a function definition
    if 'prev_was_def' in locals() and prev_was_def:
        if line.strip() and indent == 4:
            line = '    ' + line
    
    # Check if current line is a function definition
    is_def = line.lstrip().startswith('def ') and line.rstrip().endswith('):')
    is_lambda = 'lambda' in line
    
    # Write current line
    with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'a') as f:
        f.write(line)
    
    # Update state for next iteration
    prev_was_def = line.lstrip().startswith('def ') and line.rstrip().endswith('):')
    if 'lambda' in line:
        pass  # Don't set prev_was_def for lambdas

# This approach won't work with line-by-line processing. Let me write a proper script file.
print("Need to write proper script")