"""Load the original safe Pages artifact extractor without duplicating its code."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('preservation',Path(__file__).with_name('publish-showcase.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha=module.sha
unpack=module.unpack
