import sys

msg = sys.stdin.read()
lines = [l for l in msg.split('\n') if 'Co-authored-by: Cursor' not in l]
# strip trailing blank lines
while lines and not lines[-1].strip():
    lines.pop()
print('\n'.join(lines))
