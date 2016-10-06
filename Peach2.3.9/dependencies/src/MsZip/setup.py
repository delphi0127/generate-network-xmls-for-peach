
from distutils.core import setup
from distutils.extension import Extension
setup(name='MsZip',
	author='Michael Eddington',
	author_email='mike@phed.org',
	description='MsZip',
	version='0.1',
	packages = [],
	package_dir = None,
	extra_path = None,
	include_dirs = ['Include'],
	headers = None,
	ext_modules = [Extension('MsZip', ['mszip2.cpp', 'program.cpp']),]
	)

# end
