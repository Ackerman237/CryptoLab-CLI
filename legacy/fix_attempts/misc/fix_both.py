import re

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

# Fix affine cipher handler
old_affine = '''def process_fn(inputs):
            if inputs.get("action") == "brute":
                candidates = affine_brute_force(inputs["text"])
                result = Result()
                if candidates:
                best = candidates[0]
                result.add("Best a", str(best.a))
                result.add("Best b", str(best.b))
                result.add("Output", best.output_text, wrap=True)
                result.add("Total Candidates", str(len(candidates)))
                return result
            
                if inputs["action"] == "encrypt":
                res = affine_encrypt(inputs["text"], inputs["a"], inputs["b"])
            else:
                res = affine_decrypt(inputs["text"], inputs["a"], inputs["b"])
                result = Result()
                result.add("a", str(inputs["a"]))
                result.add("b", str(inputs["b"]))
                result.add("a_inv", str(res.a_inv))
                result.add("Output", res.output_text, wrap=True)
                return result'''

new_affine = '''def process_fn(inputs):
            if inputs.get("action") == "brute":
                candidates = affine_brute_force(inputs["text"])
                result = Result()
                if candidates:
                    best = candidates[0]
                    result.add("Best a", str(best.a))
                    result.add("Best b", str(best.b))
                    result.add("Output", best.output_text, wrap=True)
                    result.add("Total Candidates", str(len(candidates)))
                    return result
            if inputs["action"] == "encrypt":
                res = affine_encrypt(inputs["text"], inputs["a"], inputs["b"])
            else:
                res = affine_decrypt(inputs["text"], inputs["a"], inputs["b"])
                result = Result()
                result.add("a", str(inputs["a"]))
                result.add("b", str(inputs["b"]))
                result.add("a_inv", str(res.a_inv))
                result.add("Output", res.output_text, wrap=True)
                return result'''

content = content.replace(old, new)

# Fix PBKDF2 handler
old_pbkdf2 = '''def process_fn(inputs):
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

new_pbkdf2 = '''def process_fn(inputs):
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
print('Fixed affine and PBKDF2 handlers')