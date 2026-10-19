import os
import re

root = r"src\cryptolab\core"

# Patterns to replace
replacements = [
    # exceptions
    (r'from cryptolab\.exceptions import', 'from ..exceptions import'),
    # classical
    (r'from cryptolab\.classical\.(\w+) import', r'from .\1 import'),
    # analysis
    (r'from cryptolab\.analysis\.(\w+) import', r'from .\1 import'),
    # encoding
    (r'from cryptolab\.encoding\.(\w+) import', r'from .\1 import'),
    # symmetric
    (r'from cryptolab\.symmetric\.(\w+) import', r'from .\1 import'),
    # hashing
    (r'from cryptolab\.hashing import', 'from ..hashing import'),
    # banner -> ui
    (r'from cryptolab\.banner import', 'from cryptolab.ui import'),
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