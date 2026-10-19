with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

# Fix the PBKDF2 handler
old = '''def process_fn(inputs):
            if inputs["action"] == "verify":
                res = pbkdf2_verify(inputs["password"], inputs["salt"], inputs["expected"], 
                                iterations=inputs["iterations"], algorithm=inputs["algo"], 
                                dklen=inputs["dklen"], encoding=inputs.get("encoding", "hex"))
                result = Result()
                result.add("Algorithm", f"PBKDF2-{inputs['algo']}")
                result.add("Status", "COCOK" if res.match else "TIDAK COCOK")
                return result
                else:
                res = pbkdf2_hash(inputs["password"], salt=inputs.get("salt"), iterations=inputs["iterations"], algorithm=inputs["algo"], dklen=inputs["dklen"], encoding="hex")
                result = Result()
                result.add("Algorithm", f"PBKDF2-{inputs['algo']}")
                result.add("Iterations", f"{inputs['iterations']:,}")
                result.add("DKLen", f"{inputs['dklen']} bytes")
                result.add("Salt", res.salt)
                result.add("Hash", res.hash_value, wrap=True)
                return result'''

new = '''def process_fn(inputs):
            if inputs["action"] == "verify":
                res = pbkdf2_verify(inputs["password"], inputs["salt"], inputs["expected"], 
                                iterations=inputs["iterations"], algorithm=inputs["algo"], 
                                dklen=inputs["dklen"], encoding=inputs.get("encoding", "hex"))
                result = Result()
                result.add("Algorithm", f"PBKDF2-{inputs['algo']}")
                result.add("Status", "COCOK" if res.match else "TIDAK COCOK")
                return result
            else:
                res = pbkdf2_hash(inputs["password"], salt=inputs.get("salt"), iterations=inputs["iterations"], algorithm=inputs["algo"], dklen=inputs["dklen"], encoding="hex")
                result = Result()
                result.add("Algorithm", f"PBKDF2-{inputs['algo']}")
                result.add("Iterations", f"{inputs['iterations']:,}")
                result.add("DKLen", f"{inputs['dklen']} bytes")
                result.add("Salt", res.salt)
                result.add("Hash", res.hash_value, wrap=True)
                return result'''

content = content.replace(old, new)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.write(content)
print('Fixed PBKDF2 handler')