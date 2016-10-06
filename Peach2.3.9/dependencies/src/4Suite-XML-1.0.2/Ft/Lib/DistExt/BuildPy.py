import os, sys, glob
from distutils.command import build_py
from distutils.errors import DistutilsExecError
from distutils.util import convert_path

class BuildPy(build_py.build_py):

    command_name = 'build_py'

    if sys.version < '2.4':
        def initialize_options(self):
            build_py.build_py.initialize_options(self)
            self.package_data = None
            return

        def finalize_options(self):
            build_py.build_py.finalize_options(self)
            self.package_data = self.distribution.package_data
            self.data_files = self.get_data_files()
            return

        def run(self):
            if self.py_modules:
                self.build_modules()
            if self.packages:
                self.build_packages()
                self.build_package_data()
            self.byte_compile(self.get_outputs(include_bytecode=0))
            return

        def get_data_files(self):
            """Generate list of '(package, src_dir, build_dir, filenames)'
            tuples."""
            data = []
            for package in self.packages:
                # Locate package source directory
                src_dir = self.get_package_dir(package)

                # Compute package build directory
                build_dir = os.path.join(self.build_lib, *package.split('.'))

                # Length of path to strip from found files
                plen = len(src_dir)+1

                # Strip directory from globbed filenames
                filenames = self.find_data_files(package, src_dir)
                filenames = [ f[plen:] for f in filenames ]
                data.append((package, src_dir, build_dir, filenames))
            return data

        def find_data_files(self, package, src_dir):
            """Return filenames for package's data files in 'src_dir'"""
            globs = (self.package_data.get('', [])
                    + self.package_data.get(package, []))
            files = []
            for pattern in globs:
                # Each pattern has to be converted to a platform-specific path
                filelist = glob.glob(os.path.join(src_dir, convert_path(pattern)))
                # Files that match more than one pattern are only added once
                files.extend([fn for fn in filelist if fn not in files])
            return files

        def build_package_data(self):
            """Copy data files into build directory"""
            lastdir = None
            for package, src_dir, build_dir, filenames in self.data_files:
                for filename in filenames:
                    target = os.path.join(build_dir, filename)
                    self.mkpath(os.path.dirname(target))
                    self.copy_file(os.path.join(src_dir, filename), target,
                                preserve_mode=False)

        def get_outputs(self, include_bytecode=1):
            outputs = build_py.build_py.get_outputs(self, include_bytecode)
            for package, src_dir, build_dir, filenames in self.data_files:
                for filename in filenames:
                    outputs.append(os.path.join(build_dir, filename))
            return outputs

    if sys.version < '2.3':
        # Add support for both py_modules and packages
        def find_all_modules(self):
            """Compute the list of all modules that will be built, whether
            they are specified one-module-at-a-time ('self.py_modules') or
            by whole packages ('self.packages').  Return a list of tuples
            (package, module, module_file), just like 'find_modules()' and
            'find_package_modules()' do."""
            modules = []
            if self.py_modules:
                modules.extend(self.find_modules())
            if self.packages:
                for package in self.packages:
                    package_dir = self.get_package_dir(package)
                    m = self.find_package_modules(package, package_dir)
                    modules.extend(m)

            return modules

    def get_source_files(self):
        sources = build_py.build_py.get_source_files(self)
        for package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                sources.append(os.path.join(src_dir, filename))
        return sources

    def copy_file(self, src, dest, *args, **kwds):
        """
        Overridden to validate Python sources before copying them.
        """
        if src.endswith('.py') or (sys.platform == 'win32' and
                                   src.endswith('.pyw')):
            try:
                # Python 2.3+
                f = open(src, 'rU')
            except:
                # Python 2.2
                f = open(src, 'r')
                codestring = f.read()
                codestring = codestring.replace("\r\n", "\n")
                codestring = codestring.replace("\r", "\n")
            else:
                codestring = f.read()
            f.close()
            if codestring and codestring[-1] != '\n':
                codestring = codestring + '\n'
            try:
                compile(codestring, src, 'exec')
            except SyntaxError, detail:
                msg, (filename, lineno, offset, line) = detail
                if not filename: filename = src
                L = ['Syntax error in file "%s", line %d: %s' % (filename,
                                                                 lineno, msg)]
                if line is not None:
                    i = 0
                    while i < len(line) and line[i].isspace():
                        i = i+1
                    L.append('    %s' % line.strip())
                    if offset is not None:
                        s = '    '
                        for c in line[i:offset-1]:
                            if c.isspace():
                                s = s + c
                            else:
                                s = s + ' '
                        L.append('%s^' % s)
                raise DistutilsExecError('\n'.join(L))

        return build_py.build_py.copy_file(self, src, dest, *args, **kwds)
