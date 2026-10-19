import os
import re

root = r"src\cryptolab\cli\commands"

# Patterns to replace for CLI commands
replacements = [
    # classical
    (r'from cryptolab\.classical\.(\w+) import', r'from cryptolab import'),
    # analysis
    (r'from cryptolab\.analysis\.(\w+) import', r'from cryptolab import'),
    # exceptions
    (r'from cryptolab\.exceptions import', r'from cryptolab import'),
    # utils
    (r'from cryptolab\.utils\.(\w+) import', r'from cryptolab import'),
]

for dirpath, dirnames, filenames in os.walk(root):
    for filename in filenames:
        if filename.endswith('.py'):
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            for pattern, repl in replacements:
                content = re.sub(pattern, repl, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated: {filepath}")

print("Done!")