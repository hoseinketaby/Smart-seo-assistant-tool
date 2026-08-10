import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
c = open('templates/dashboard/base.html', encoding='utf-8').read()
c = c.replace('[[[MINDMAP_HERE]]]', 'REPLACED')
open('templates/dashboard/base.html', 'w', encoding='utf-8').write(c)
print('Done')
