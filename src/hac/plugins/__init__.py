from importlib.util import spec_from_file_location, module_from_spec
from os.path import dirname, basename, isfile, join
import glob
import sys

clickcmds = []
# # auto load plugins
for path in glob.glob(join(dirname(__file__), "*/__init__.py")):
    if not isfile(path):
        continue
    spec = spec_from_file_location(basename(dirname(path)), path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if hasattr(module, 'clickcmd'):
        clickcmds.append(module.clickcmd)
