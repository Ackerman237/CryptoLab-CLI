import re

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r') as f:
    content = f.read()

# The file has nested functions indented 8 spaces too deep (2 levels)
# Fix: dedent all nested function definitions and their bodies by 8 spaces

# Pattern 1: Nested function definitions at 12 spaces -> 4 spaces
# Pattern: "        def func_name(...):" -> "    def func_name(...):"
content = re.sub(
    r'(^ {12})def ([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):)',
    r'    def \2',
    content,
    flags=re.MULTILINE
)

# Fix function bodies at 16/20/24/28/28/32/36 -> dedent by 8
# Body lines at 16+ spaces -> dedent by 8
content = re.sub(
    r'(^ {16,})([^\s#\n])',
    lambda m: ' ' * (len(m.group(1)) - 8) + m.group(2),
    content,
    flags=re.MULTILINE
)

# Fix elif/else/if/for/while at wrong indentation (16 -> 8, 20->12, etc.)
# Fix elif/else at 16 -> 8
content = re.sub(
    r'(^ {16})(el(?:if|se):)',
    r'        \2',
    content,
    flags=re.MULTILINE
)

# Fix if/for/while at 16 -> 8
content = re.sub(
    r'(^ {16})(if |for |while )',
    r'        \2',
    content,
    flags=re.MULTILINE
)

# Fix else: at 16 -> 8
content = re.sub(
    r'(^ {16})else:',
    r'        else:',
    content,
    flags=re.MULTILINE
)

# Fix return statements at 20 -> 12
content = re.sub(
    r'(^ {20})return ',
    r'            return ',
    content,
    flags=re.MULTILINE
)

# Fix result.add/result.add at 20 -> 12
content = re.sub(
    r'(^ {20})result\.',
    r'            result.',
    content,
    flags=re.MULTILINE
)

# Fix print/print statements at 20 -> 12
content = re.sub(
    r'(^ {20})print\(',
    r'            print(',
    content,
    flags=re.MULTILINE
)

# Fix variable assignments at 20 -> 12
content = re.sub(
    r'(^ {20})(\w+ = )',
    r'            \2',
    content,
    flags=re.MULTILINE
)

# Fix comments at 20 -> 12
content = re.sub(
    r'(^ {20})#',
    r'            #',
    content,
    flags=re.MULTILINE
)

# Fix blank lines with extra spaces
content = re.sub(r'^ {1,}\n', '\n', content, flags=re.MULTILINE)

# Fix specific patterns for run_action calls at wrong indentation
# run_action at 4 spaces should stay at 4 (module level in handler)
# But if they're at 8, fix to 4
content = re.sub(
    r'(^ {8})run_action\(',
    r'    run_action(',
    content,
    flags=re.MULTILINE
)

# Fix list items in run_action at 12 -> 8
content = re.sub(
    r'(^ {12})({"key":)',
    r'        \2',
    content,
    flags=re.MULTILINE
)

# Fix closing brackets at 4 -> 4 (already correct)
# Fix closing brackets at 8 -> 4
content = re.sub(
    r'(^ {8})\]\)',
    r'    ])',
    content,
    flags=re.MULTILINE
)

# Fix closing braces at 12 -> 8
content = re.sub(
    r'(^ {12})\}\]',
    r'        }]',
    content,
    flags=re.MULTILINE
)

# Fix lambda continuations at 28 -> 24
content = re.sub(
    r'(^ {28})lambda ',
    r'                        lambda ',
    content,
    flags=re.MULTILINE
)

# Fix specific handler functions that are still broken
# Fix HMAC handler
content = content.replace(
    '''        def process_fn(inputs):
                if inputs["action"] == "verify":
                    match = hmac_verify(inputs["message"], inputs["key"], inputs["expected"],
                                     algorithm=inputs["algo"], encoding=inputs["encoding"])
                    result = Result()
                    result.add("Algorithm", f"HMAC-{inputs['algo']}")
                    result.add("Status", "VALID (COCOK)" if match else "INVALID (TIDAK COCOK)")
                    return result
                else:
                    res = hmac_compute(inputs["message"], inputs["key"], algorithm=inputs["algo"], encoding=inputs["encoding"])
                    result = Result()
                    result.add("Algorithm", f"HMAC-{inputs['algo']}")
                    result.add("Key Length", f"{len(inputs['key'])} bytes")
                    result.add("HMAC", res.output_hmac, wrap=True)
                    return result''',
    '''        def process_fn(inputs):
                if inputs["action"] == "verify":
                    match = hmac_verify(inputs["message"], inputs["key"], inputs["expected"],
                                     algorithm=inputs["algo"], encoding=inputs["encoding"])
                    result = Result()
                    result.add("Algorithm", f"HMAC-{inputs['algo']}")
                    result.add("Status", "VALID (COCOK)" if match else "INVALID (TIDAK COCOK)")
                    return result
                else:
                    res = hmac_compute(inputs["message"], inputs["key"], algorithm=inputs["algo"], encoding=inputs["encoding"])
                    result = Result()
                    result.add("Algorithm", f"HMAC-{inputs['algo']}")
                    result.add("Key Length", f"{len(inputs['key'])} bytes")
                    result.add("HMAC", res.output_hmac, wrap=True)
                    return result''')

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w') as f:
    f.write(content)
print('Fixed')