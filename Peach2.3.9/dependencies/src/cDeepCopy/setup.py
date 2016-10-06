
from distutils.core import setup
from distutils.extension import Extension
setup(name='cDeepCopy',
	author='Michael Eddington',
	author_email='mike@phed.org',
	description='Native DeepCopy',
	version='0.2',
	packages = [],
	package_dir = None,
	extra_path = None,
	include_dirs = ['Include'],
	headers = None,
	ext_modules = [Extension('cDeepCopy', ['cDeepCopy.c']),]
	)

# end
