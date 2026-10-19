with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# First, let's understand the structure by analyzing the file
# We'll do a proper parse: track nested functions and their control structures

new_lines = []
in_nested_fn = False
fn_indent = 0
block_stack = []  # stack of (control_type, indent_level, start_line_index)

for i, line in enumerate(lines):
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    
    # Track entering nested functions (process_fn, input_fn at indent 4)
    if stripped.startswith('def process_fn(') or stripped.startswith('def input_fn('):
        in_nested_fn = True
        fn_indent = 4
        block_stack = []
        new_lines.append(line)
        continue
    elif in_nested_fn and indent <= fn_indent and stripped and not stripped.startswith('#'):
        # Leaving nested function
        in_nested_fn = False
        block_stack = []
    
    if in_nested_fn:
        # Handle control structures
        if indent == 8 and stripped.startswith(('if ', 'elif ')):
            # Start of if/elif block
            block_stack.append(('if', 8, len(new_lines)))
            new_lines.append(line)
            continue
        elif indent == 8 and stripped == 'else:':
            # else: at same level as if
            if block_stack and block_stack[-1][0] in ('if', 'elif'):
                block_stack[-1] = ('else', 8, len(new_lines))
            new_lines.append(line)
            continue
        elif indent == 8 and stripped.startswith(('for ', 'while ', 'try:', 'with ')):
            block_stack.append(('loop', 8, len(new_lines)))
            new_lines.append(line)
            continue
        elif indent == 8 and stripped.startswith('except'):
            block_stack.append(('except', 8, len(new_lines)))
            new_lines.append(line)
            continue
        elif indent == 8 and stripped.startswith('finally:'):
            block_stack.append(('finally', 8, len(new_lines)))
            new_lines.append(line)
            continue
        
        # Determine current block context
        current_block_indent = 8
        if block_stack:
            current_block_indent = block_stack[-1][1] + 4  # body is 4 more than control
        
        # If we're in a block body and line is at indent 8, fix to proper indent
        if block_stack and stripped and not stripped.startswith('#'):
            if indent == 8 and current_block_indent == 12:
                # This line should be in the block body
                new_lines.append(' ' * 12 + stripped + '\n')
                continue
            elif indent == 8 and current_block_indent > 12:
                new_lines.append(' ' * current_block_indent + stripped + '\n')
                continue
            elif indent > 8:
                # Already indented, keep as is
                new_lines.append(line)
                continue
        
        # Check for dedent (end of block)
        if block_stack and indent == 8 and not stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
            # Check if this line is at the same level as the control statement
            # If so, we might be ending the block
            pass
    
    new_lines.append(line)

with open(r'D:\praktikum-semester-5\Prakrikum-Keamanan_Informasi\CLI Encryption & Decryption Toolkit\src\cryptolab\interactive.py', 'w', encoding='utf-8') as f:
    f.write(''.join(new_lines))

print('Fixed')