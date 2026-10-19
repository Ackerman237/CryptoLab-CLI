import re

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

# Fix pattern: function definition at N spaces, followed by statement at same indentation
# Should be: function def at N spaces, body at N+4 spaces

# Fix nested functions at 4 spaces (inside a function at 0 spaces)
content = re.sub(
    r'(^ {4}def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):)\n( {4})([^\s#\n])',
    r'\1\n    \3',
    content,
    flags=re.MULTILINE
)

# Fix nested functions at 8 spaces (inside a function at 4 spaces)
content = re.sub(
    r'(^ {8}def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):)\n( {8})([^\s#\n])',
    r'\1\n        \3',
    content,
    flags=re.MULTILINE
)

# Fix nested functions at 12 spaces (inside a function at 8 spaces)
content = re.sub(
    r'(^ {12}def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):)\n( {12})([^\s#\n])',
    r'\1\n            \3',
    content,
    flags=re.MULTILINE
)

# Fix specific known patterns
replacements = [
    # handle_hash_compute -> process_fn
    ('        def process_fn(inputs):\n        res = hash_compute(inputs["data"], algorithm=inputs["algo"], encoding=inputs["encoding"])',
     '        def process_fn(inputs):\n            res = hash_compute(inputs["data"], algorithm=inputs["algo"], encoding=inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = hash_file(inputs["filepath"], algorithm=inputs["algo"])',
     '        def process_fn(inputs):\n            res = hash_file(inputs["filepath"], algorithm=inputs["algo"])'),
    ('        def process_fn(inputs):\n        res = hmac_compute(inputs["data"], inputs["key"], algorithm=inputs["algo"], encoding=inputs["encoding"])',
     '        def process_fn(inputs):\n            res = hmac_compute(inputs["data"], inputs["key"], algorithm=inputs["algo"], encoding=inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = pbkdf2_hash(inputs["password"], salt=inputs.get("salt"), iterations=inputs["iterations"], algorithm=inputs["algo"], dklen=inputs["dklen"], encoding=inputs["encoding"])',
     '        def process_fn(inputs):\n            res = pbkdf2_hash(inputs["password"], salt=inputs.get("salt"), iterations=inputs["iterations"], algorithm=inputs["algo"], dklen=inputs["dklen"], encoding=inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = bcrypt_hash(inputs["password"], rounds=inputs["rounds"])',
     '        def process_fn(inputs):\n            res = bcrypt_hash(inputs["password"], rounds=inputs["rounds"])'),
    ('        def process_fn(inputs):\n        res = bcrypt_verify(inputs["password"], inputs["expected"])',
     '        def process_fn(inputs):\n            res = bcrypt_verify(inputs["password"], inputs["expected"])'),
    ('        def process_fn(inputs):\n        res = hash_verify_integrity(inputs["data"], inputs["expected"], algorithm=inputs["algo"], encoding=inputs["encoding"])',
     '        def process_fn(inputs):\n            res = hash_verify_integrity(inputs["data"], inputs["expected"], algorithm=inputs["algo"], encoding=inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = generate_random_bytes(inputs["length"], encoding=inputs["encoding"])',
     '        def process_fn(inputs):\n            res = generate_random_bytes(inputs["length"], encoding=inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = aes_encrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])',
     '        def process_fn(inputs):\n            res = aes_encrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])'),
    ('        def process_fn(inputs):\n        res = aes_decrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])',
     '        def process_fn(inputs):\n            res = aes_decrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])'),
    ('        def process_fn(inputs):\n        res = des_encrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])',
     '        def process_fn(inputs):\n            res = des_encrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])'),
    ('        def process_fn(inputs):\n        res = des_decrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])',
     '        def process_fn(inputs):\n            res = des_decrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"])'),
    ('        def process_fn(inputs):\n        res = rc2_encrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"], inputs["effective_keylen"])',
     '        def process_fn(inputs):\n            res = rc2_encrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"], inputs["effective_keylen"])'),
    ('        def process_fn(inputs):\n        res = rc2_decrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"], inputs["effective_keylen"])',
     '        def process_fn(inputs):\n            res = rc2_decrypt(inputs["text"], inputs["key"], inputs["mode"], inputs["iv"], inputs["padding"], inputs["effective_keylen"])'),
    ('        def process_fn(inputs):\n        res = rsa_generate_keypair(inputs["size"])',
     '        def process_fn(inputs):\n            res = rsa_generate_keypair(inputs["size"])'),
    ('        def process_fn(inputs):\n        res = rsa_encrypt(inputs["text"], inputs["pubkey"], inputs["padding"], inputs["hash"], inputs["encoding"])',
     '        def process_fn(inputs):\n            res = rsa_encrypt(inputs["text"], inputs["pubkey"], inputs["padding"], inputs["hash"], inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = rsa_decrypt(inputs["text"], inputs["privkey"], inputs["padding"], inputs["hash"], inputs["encoding"])',
     '        def process_fn(inputs):\n            res = rsa_decrypt(inputs["text"], inputs["privkey"], inputs["padding"], inputs["hash"], inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = rsa_sign(inputs["text"], inputs["privkey"], inputs["padding"], inputs["hash"], inputs["encoding"])',
     '        def process_fn(inputs):\n            res = rsa_sign(inputs["text"], inputs["privkey"], inputs["padding"], inputs["hash"], inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = rsa_verify(inputs["text"], inputs["sig"], inputs["pubkey"], inputs["padding"], inputs["hash"], inputs["encoding"])',
     '        def process_fn(inputs):\n            res = rsa_verify(inputs["text"], inputs["sig"], inputs["pubkey"], inputs["padding"], inputs["hash"], inputs["encoding"])'),
    ('        def process_fn(inputs):\n        res = dh_key_exchange(inputs["bits"], alice_private=inputs.get("alice"), bob_private=inputs.get("bob"))',
     '        def process_fn(inputs):\n            res = dh_key_exchange(inputs["bits"], alice_private=inputs.get("alice"), bob_private=inputs.get("bob"))'),
    ('        def process_fn(inputs):\n        res = dh_derive_key(inputs["shared"], key_length=inputs["keylen"], hash_algo=inputs["hash"])',
     '        def process_fn(inputs):\n            res = dh_derive_key(inputs["shared"], key_length=inputs["keylen"], hash_algo=inputs["hash"])'),
    ('        def process_fn(inputs):\n        res = playfair_encrypt(inputs["text"], inputs["key"])',
     '        def process_fn(inputs):\n            res = playfair_encrypt(inputs["text"], inputs["key"])'),
    ('        def process_fn(inputs):\n        res = playfair_decrypt(inputs["text"], inputs["key"])',
     '        def process_fn(inputs):\n            res = playfair_decrypt(inputs["text"], inputs["key"])'),
    ('        def process_fn(inputs):\n        res = hill_encrypt(inputs["text"], inputs["key"], inputs["size"])',
     '        def process_fn(inputs):\n            res = hill_encrypt(inputs["text"], inputs["key"], inputs["size"])'),
    ('        def process_fn(inputs):\n        res = hill_decrypt(inputs["text"], inputs["key"], inputs["size"])',
     '        def process_fn(inputs):\n            res = hill_decrypt(inputs["text"], inputs["key"], inputs["size"])'),
    ('        def process_fn(inputs):\n        res = affine_encrypt(inputs["text"], inputs["a"], inputs["b"])',
     '        def process_fn(inputs):\n            res = affine_encrypt(inputs["text"], inputs["a"], inputs["b"])'),
    ('        def process_fn(inputs):\n        res = affine_decrypt(inputs["text"], inputs["a"], inputs["b"])',
     '        def process_fn(inputs):\n            res = affine_decrypt(inputs["text"], inputs["a"], inputs["b"])'),
    ('        def process_fn(inputs):\n        res = railfence_encrypt(inputs["text"], inputs["rails"])',
     '        def process_fn(inputs):\n            res = railfence_encrypt(inputs["text"], inputs["rails"])'),
    ('        def process_fn(inputs):\n        res = railfence_decrypt(inputs["text"], inputs["rails"])',
     '        def process_fn(inputs):\n            res = railfence_decrypt(inputs["text"], inputs["rails"])'),
    ('        def process_fn(inputs):\n        res = caesar_encrypt(inputs["text"], inputs["shift"])',
     '        def process_fn(inputs):\n            res = caesar_encrypt(inputs["text"], inputs["shift"])'),
    ('        def process_fn(inputs):\n        res = caesar_decrypt(inputs["text"], inputs["shift"])',
     '        def process_fn(inputs):\n            res = caesar_decrypt(inputs["text"], inputs["shift"])'),
    ('        def process_fn(inputs):\n        res = vigenere_encrypt(inputs["text"], inputs["key"])',
     '        def process_fn(inputs):\n            res = vigenere_encrypt(inputs["text"], inputs["key"])'),
    ('        def process_fn(inputs):\n        res = vigenere_decrypt(inputs["text"], inputs["key"])',
     '        def process_fn(inputs):\n            res = vigenere_decrypt(inputs["text"], inputs["key"])'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.write(content)

print('Fixed all indentation issues')