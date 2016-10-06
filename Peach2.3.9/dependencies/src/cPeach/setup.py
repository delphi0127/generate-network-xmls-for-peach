
from distutils.core import setup
from distutils.extension import Extension
setup(name='cPeach',
	author='Michael Eddington',
	author_email='mike@phed.org',
	description='Native Peach Methods',
	version='0.2',
	packages = [],
	package_dir = None,
	extra_path = None,
	include_dirs = ['Include'],
	headers = None,
	ext_modules = [Extension('cPeach', ['cPeach.c']),]
	)

# end
