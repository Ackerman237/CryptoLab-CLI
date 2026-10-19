import os
import re

root = r"tests"

# Patterns to replace for test files
replacements = [
    # classical
    (r'from cryptolab\.classical import', r'from cryptolab import'),
    (r'from cryptolab\.classical\.(\w+) import', r'from cryptolab import'),
    # symmetric
    (r'from cryptolab\.symmetric import', r'from cryptolab import'),
    (r'from cryptolab\.symmetric\.(\w+) import', r'from cryptolab import'),
    # asymmetric
    (r'from cryptolab\.asymmetric import', r'from cryptolab import'),
    # hashing
    (r'from cryptolab\.hashing import', r'from cryptolab import'),
    # encoding
    (r'from cryptolab\.encoding import', r'from cryptolab import'),
    (r'from cryptolab\.encoding\.(\w+) import', r'from cryptolab import'),
    # analysis
    (r'from cryptolab\.analysis import', r'from cryptolab import'),
    (r'from cryptolab\.analysis\.(\w+) import', r'from cryptolab import'),
    # exceptions
    (r'from cryptolab\.exceptions import', r'from cryptolab import'),
    # utils
    (r'from cryptolab\.utils import', r'from cryptolab import'),
    (r'from cryptolab\.utils\.(\w+) import', r'from cryptolab import'),
    # cli
    (r'from cryptolab\.cli import', r'from cryptolab import'),
    (r'from cryptolab\.cli\.(\w+) import', r'from cryptolab import'),
    # interactive
    (r'from cryptolab\.interactive import', r'from cryptolab import'),
    (r'from cryptolab\.interactive\.(\w+) import', r'from cryptolab import'),
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