with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    lines = f.readlines()

new_lines = []
prev_line_was_def = False

for line in lines:
    stripped = line.lstrip()
    indent = len(line) - len(line.lstrip())
    
    # Check if previous line was a function definition
    if 'prev_was_def' in locals() and prev_line_was_def:
        if line.strip() and indent == 4:
            # This is the first line of a function body, indent by 4 more
            line = '    ' + line
    
    # Check if current line is a function definition
    is_def = line.lstrip().startswith('def ') and line.rstrip().endswith('):')
    is_lambda = 'lambda' in line
    
    new_lines.append(line)
    
    # Track if current line is a function definition (for next iteration)
    prev_was_def = line.lstrip().startswith('def ') and line.rstrip().endswith('):') and 'lambda' not in line

# This won't work with line-by-line processing. Need to use a different approach.
print("Need different approach")