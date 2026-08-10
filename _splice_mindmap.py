import io, os

base_dir = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.join(base_dir, 'templates', 'dashboard', 'base.html')
new_block_path = os.path.join(base_dir, '_mindmap_new.html')

with io.open(base_path, 'r', encoding='utf-8') as f:
    src = f.read()

with io.open(new_block_path, 'r', encoding='utf-8') as f:
    new_block = f.read()

marker = '<!-- Mind Map -->'
start = src.index(marker)
line_start = src.rindex('\n', 0, start) + 1

endif_idx = src.index('{% endif %}', start)
line_end = src.index('\n', endif_idx) + 1

result = src[:line_start] + new_block + src[line_end:]

with io.open(base_path, 'w', encoding='utf-8') as f:
    f.write(result)

print('OK: spliced mind map block (bytes:', len(new_block), ') into base.html')
print('Replaced lines were', src[line_start:line_end].count(chr(10)), 'lines; new block is', new_block.count(chr(10)), 'lines.')
