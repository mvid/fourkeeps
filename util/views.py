import pystache
import os

views = {}

def render_view(view, data):
  data = pystache.render(views[view], data)
  return pystache.render(views['layout'], {'page': unicode(data)})

# Precompile templates
for (dirpath, _, filenames) in os.walk('views'):
  for fname in filenames:
    path = dirpath + '/' + fname
    view = open(path, 'r').read()
    name = path[6:]
    if name.endswith('.stache'): name = name[0:len(name)-7]
    views[name] = pystache.parse(unicode(view))

