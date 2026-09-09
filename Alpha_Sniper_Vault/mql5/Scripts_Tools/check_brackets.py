import glob, re

files = ["Alpha_Sniper_v11_4.mq5", "Alpha_Sniper_v11_4_EXP.mq5"]

for fname in files:
    with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    code_no_comm = re.sub(r'//.*', '', code)
    code_no_str = re.sub(r'"[^"]*"', '', code_no_comm)

    stack = []
    err = False
    for i, line in enumerate(code_no_str.splitlines()):
        for j, c in enumerate(line):
            if c in '({':
                stack.append((c, i+1, j+1))
            elif c in ')}':
                if not stack:
                    print(f"[{fname}] UNBALANCED CLOSE {c} at line {i+1} col {j+1}")
                    err = True
                else:
                    top = stack[-1][0]
                    if (top == '(' and c == ')') or (top == '{' and c == '}'):
                        stack.pop()
                    else:
                        print(f"[{fname}] MISMATCH CLOSE {c} for open {top} at line {i+1} col {j+1}")
                        stack.pop()
                        err = True
    if stack:
        print(f"[{fname}] UNCLOSED LEFT ON STACK ({len(stack)}):")
        for item in stack[:5]:
            print(" ", item)
        err = True

    if not err:
        print(f"[{fname}] BRACKETS OK")
