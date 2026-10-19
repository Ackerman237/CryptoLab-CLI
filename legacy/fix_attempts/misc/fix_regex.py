with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: handler functions have nested functions at indent 8 that should be at indent 4
# The pattern is:
# def handle_xxx():
#     ... (indent 4)
#     def process_fn(inputs):  <- this is at indent 8, should be 4
#         ... (indent 8, should be 8)
#     run_action(...)  <- this is at indent 8, should be 4

# Replace all occurrences where a nested function def inside handler is at indent 8
import re

# Fix: def process_fn(inputs): inside handlers should be at indent 4 not 8
content = re.sub(r'^        def process_fn\(inputs\):\n', '    def process_fn(inputs):\n', content, flags=re.MULTILINE)

# Fix: body of process_fn should remain at indent 8 (it's already correct)
# But run_action and other statements at indent 8 should be at indent 4
content = re.sub(r'^        run_action\(', '    run_action(', content, flags=re.MULTILINE)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed')