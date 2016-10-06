import os, re, sys, zipfile, imp
from distutils.command import build, install
from distutils.core import Command
from distutils.dep_util import newer
from distutils.dir_util import remove_tree
from distutils.errors import *
from distutils.sysconfig import get_python_version
from distutils.util import byte_compile

from Ft.Lib import ImportUtil
from Ft.Lib.DistExt import Structures, Util

__zipsafe__ = True

EXTENSION_MODULE_STUB = """# dynamic module loader stub for .egg zipfiles
def __bootstrap__():
    global __bootstrap__, __loader__, __file__
    import imp, pkg_resources
    __file__ = pkg_resources.resource_filename(__name__, %(file)r)
    del __bootstrap__, __loader__
    imp.load_dynamic(__name__, __file__)
__bootstrap__()
"""

NAMESPACE_PACKAGE_STUB = """# loader stub for .egg namespace packages
__import__("pkg_resources").declare_namespace(__name__)
"""

class BDistEgg(Command):

    command_name = 'bdist_egg'

    description = "create a Python Egg (.egg) built distribution"

    user_options = [
        ('bdist-dir=', None,
         "temporary directory for creating the distribution"),
        ('keep-temp', 'k',
         "keep the pseudo-installation tree around after " +
         "creating the distribution archive"),
        ('plat-name=', 'p',
         "platform name to embed in generated filenames"),
        ('dist-dir=', 'd',
         "directory to put final built distributions in"),
        ('skip-build', None,
         "skip rebuilding everything (for testing/debugging)"),
        ]

    boolean_options = ['keep-temp', 'skip-build']

    build_commands = ['build_py', 'build_clib', 'build_ext', 'build_scripts']

    install_commands = ['install_lib', 'install_data', 'install_l10n',
                        'install_config']

    def initialize_options(self):
        self.bdist_dir = None
        self.plat_name = None
        self.keep_temp = None
        self.dist_dir = None
        self.skip_build = None
        return

    def finalize_options(self):
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            egg_dir = self.distribution.get_name() + '.egg'
            self.bdist_dir = os.path.join(bdist_base, egg_dir)

        self.set_undefined_options('bdist',
                                   ('keep_temp', 'keep_temp'),
                                   ('plat_name', 'plat_name'),
                                   ('dist_dir', 'dist_dir'),
                                   ('skip_build', 'skip_build'))
        return

    def run(self):
        if sys.version < '2.3':
            raise DistutilsPlatformError('Python Eggs require Python 2.3+')

        if not self.skip_build:
            # Run any build commands
            self.run_command_family('build', self.build_commands)

        self.mkpath(self.bdist_dir)

        # Set the options for the installation commands
        install = self.reinitialize_command('install')
        # We need a "prestine" command (no options from anywhere else)
        install.initialize_options()
        for cmd_name, predicate in install.sub_commands:
            self.reinitialize_command(cmd_name).initialize_options()
        install.skip_build = self.skip_build
        install.compile = True
        install.install_base = install.install_platbase = self.bdist_dir
        install.select_scheme('zip')
        install.ensure_finalized()
        # Make the install appear to be a "chroot" install
        install.root = self.bdist_dir
        install.install_base = install.install_platbase = None

        # Run the commands that install "resources"
        commands = self.run_command_family('install', self.install_commands)
        outputs = []
        for command in commands:
            cmd = self.get_finalized_command(command)
            outputs.extend(cmd.get_outputs())

        # Create stub loaders for any extension modules
        py_files = self.write_extension_module_stubs()

        # Create namespace package loaders
        py_files.extend(self.write_namespace_package_stubs())

        # Byte-compile any additional Python source files
        if py_files:
            outputs.extend(py_files)
            # Byte-compile the stubs and record the compiled filenames
            install_lib = self.get_finalized_command('install_lib')
            install_lib.byte_compile(py_files)
            for py_file in py_files:
                if install_lib.compile:
                    outputs.append(py_file + 'c')
                if install_lib.optimize > 0:
                    outputs.append(py_file + 'o')

        # Add the standard metadata (EGG-INFO directory)
        outputs.extend(self.write_metadata())

        # Make the egg distribution
        dist_filename = self.make_distribution(outputs)

        # Add to 'Distribution.dist_files' so that the "upload" command works
        if hasattr(self.distribution, 'dist_files'):
            spec = ('bdist_egg', get_python_version(), dist_filename)
            self.distribution.dist_files.append(spec)

        if not self.keep_temp:
            remove_tree(self.bdist_dir, self.verbose, self.dry_run)
        return

    def run_command_family(self, family, commands):
        command = self.get_finalized_command(family)
        sub_commands = command.get_sub_commands()
        have_run = []
        for cmd_name in commands:
            if cmd_name in sub_commands:
                self.run_command(cmd_name)
                have_run.append(cmd_name)
        return have_run

    def write_extension_module_stubs(self):
        outputs = []
        build_ext = self.get_finalized_command('build_ext')
        for extension in build_ext.extensions:
            fullname = build_ext.get_ext_fullname(extension.name)
            filename = build_ext.get_ext_filename(fullname)
            contents = EXTENSION_MODULE_STUB % {
                'file' : os.path.basename(filename)}
            barename, ext = os.path.splitext(filename)
            if barename.endswith('module'):
                barename = barename[:-6]
            filename = os.path.join(self.bdist_dir, barename + '.py')
            description = "extension module stub for %r" % extension.name
            if self.force or self.newer(description, filename):
                self.write_file(description, contents, filename)
            outputs.append(filename)
        return outputs

    def write_namespace_package_stubs(self):
        outputs = []
        for package in self.distribution.namespace_packages:
            dirname = package.replace('.', os.sep)
            filename = os.path.join(self.bdist_dir, dirname, '__init__.py')
            description = "namespace package stub for %r" % package
            if self.force or self.newer(description, filename):
                self.write_file(description, NAMESPACE_PACKAGE_STUB, filename)
            outputs.append(filename)
        return outputs

    def write_metadata(self):
        outputs = []
        metadata_dir = os.path.join(self.bdist_dir, 'EGG-INFO')
        self.mkpath(metadata_dir)

        filename = os.path.join(metadata_dir, 'PKG-INFO')
        description = "package metadata"
        if self.force or self.newer(description, filename):
            self.announce("writing %s to %s" % (description, filename), 2)
            if not self.dry_run:
                f = open(filename, 'w')
                try:
                    self.distribution.metadata.write_pkg_file(f)
                finally:
                    f.close()
        outputs.append(filename)

        entry_points = self.get_entry_points()
        if entry_points:
            filename = os.path.join(metadata_dir, 'entry_points.txt')
            description = "entry points"
            if self.force or self.newer(description, filename):
                self.write_file_sections(description, entry_points, filename)
            outputs.append(filename)

        eager_resources = self.get_eager_resources()
        if eager_resources:
            prefix = self.bdist_dir + os.sep
            prefix_len = len(prefix)
            lines = []
            for resource in eager_resources:
                if resource.startswith(prefix):
                    resource = resource[prefix_len:]
                lines.append(resource.replace(os.sep, '/'))
            description = "eager resources"
            if self.force or self.newer(description, filename):
                self.write_file_lines(description, lines, filename)
            outputs.append(filename)

        # Create the ZIP safety flag file
        if self.check_zip_safe():
            filename = 'zip-safe'
        else:
            filename = 'not-zip-safe'
        filename = os.path.join(metadata_dir, filename)
        self.write_file_lines('ZIP safety flag', (), filename)
        outputs.append(filename)

        return outputs

    def get_entry_points(self):
        entry_points = {}
        # Get the scripts which will be turned into console_script entries
        if self.distribution.has_scripts():
            entry_points['console_scripts'] = console_scripts = []
            for script in self.distribution.scripts:
                if isinstance(script, Structures.Script):
                    entry_point = '%s = %s:%s' % (script.name, script.module,
                                                  script.function)
                    console_scripts.append(entry_point)
                else:
                    self.announce("WARNING: script '%s' skipped"
                                  " (unsupported format)" % script.name, 3)

        return entry_points

    def get_eager_resources(self):
        eager_resources = []

        # Python's gettext requires true filesystem paths, so add the
        # localization catalogs to the list of "eager resources".
        if self.distribution.has_l10n():
            install_l10n = self.get_finalized_command('install_l10n')
            eager_resources.append(install_l10n.install_dir)
            eager_resources.extend(install_l10n.get_outputs())

        return eager_resources

    def check_zip_safe(self):
        safe = True
        build_py = self.get_finalized_command('build_py')
        for package, module, filename in build_py.find_all_modules():
            if module == '__init__':
                fullname = package
            elif package:
                fullname = package + '.' + module

            # Get the code object for the module.
            f = open(filename, 'rU')
            try:
                code = compile(f.read(), filename, 'exec')
            finally:
                f.close()

            # If the module attribute '__zipsafe__' is defined, use its
            # value to determine zip-safety.  Otherwise check the symbols
            # used for "unsafe" names.
            if '__zipsafe__' in code.co_names:
                constants = get_constants(code)
                try:
                    safe = safe and constants['__zipsafe__']
                except KeyError:
                    # If defined, __zipsafe__ *MUST* be constant.
                    raise ValueError("%s.__zipsafe__ not constant" % fullname)
            else:
                symbols = get_symbols(code)
                unsafe = []
                for bad in ('__file__', '__path__'):
                    if bad in symbols:
                        unsafe.append(bad)
                if 'inspect' in symbols:
                    for bad in ('getsource', 'getabsfile', 'getsourcefile',
                                'getfile', 'getsourcelines', 'findsource',
                                'getcomments', 'getframeinfo',
                                'getinnerframes', 'getouterframes', 'stack',
                                'trace'):
                        if bad in symbols:
                            unsafe.append('inspect.' + bad)
                for symbol in unsafe:
                    self.announce("%s references %s" % (fullname, symbol), 2)
                    safe = False
        return safe

    def make_distribution(self, files):
        self.mkpath(self.dist_dir)
        egg_filename = os.path.join(self.dist_dir, self.get_egg_filename())
        self.announce("creating %s" % egg_filename, 2)
        if not self.dry_run:
            if sys.version < '2.4':
                # avoid 2.3 zipimport bug when 64 bits
                compression = zipfile.ZIP_STORED
            else:
                compression = zipfile.ZIP_DEFLATED
            eggfile = zipfile.ZipFile(egg_filename, "w", compression)
        else:
            eggfile = None

        prefix_len = len(self.bdist_dir) + len(os.sep)
        for filename in files:
            arcname = filename[prefix_len:]
            self.announce("adding %s" % arcname, 1)
            if eggfile is not None:
                eggfile.write(filename, arcname)

        if eggfile is not None:
            eggfile.close()
        return egg_filename

    def get_egg_filename(self):
        def make_egg_safe(name):
            return re.sub('[^a-zA-Z0-9.]+', '_', name)
        name = make_egg_safe(self.distribution.get_name())
        version = make_egg_safe(self.distribution.get_version())
        platform = get_python_version()
        if self.distribution.has_ext_modules():
            platform += '-' + self.plat_name
        return '%s-%s-py%s.egg' % (name, version, platform)

    def newer(self, description, filename):
        try:
            target_mtime = os.stat(filename).st_mtime
        except OSError:
            return True
        if self.distribution.package_file:
            source_mtime = os.stat(self.distribution.package_file).st_mtime
            if source_mtime > target_mtime:
                return True
        command_mtime = ImportUtil.GetLastModified(__name__)
        if command_mtime > target_mtime:
            return True
        self.announce("skipping %s (up-to-date)" % description, 1)
        return False

    def write_file_sections(self, description, sections, filename):
        self.announce("writing %s to %s" % (description, filename), 2)
        if not self.dry_run:
            f = open(filename, 'w')
            try:
                for section in sections:
                    f.write('[%s]\n' % section)
                    for line in sections[section]:
                        f.write(line)
                        f.write('\n')
                    f.write('\n')
            finally:
                f.close()
        return

    def write_file_lines(self, description, lines, filename):
        self.announce("writing %s to %s" % (description, filename), 2)
        if not self.dry_run:
            f = open(filename, 'w')
            try:
                for line in lines:
                    f.write(line)
                    f.write('\n')
            finally:
                f.close()
        return

    def write_file(self, description, contents, filename):
        self.announce("writing %s to %s" % (description, filename), 2)
        if not self.dry_run:
            f = open(filename, 'w')
            try:
                f.write(contents)
            finally:
                f.close()
        return

def get_constants(code):
    """Returns the mapping of top-level "constants" defined by
    'code'.
    """
    # perform a "mini-eval" of the global assignments
    import dis
    LOAD_CONST = dis.opmap['LOAD_CONST']
    LOAD_NAME = dis.opmap['LOAD_NAME']
    STORE_NAME = dis.opmap['STORE_NAME']
    EXTENDED_ARG = dis.opmap['EXTENDED_ARG']
    # convert the bytecode string to a series of integers
    opcodes = iter(map(ord, code.co_code))
    next_instr = opcodes.next
    constants = {}
    value = undefined = object()
    for opcode in opcodes:
        if opcode >= dis.HAVE_ARGUMENT:
            oparg = next_instr() + next_instr()*256
            while opcode == EXTENDED_ARG:
                opcode = next_instr()
                oparg = oparg << 16 + next_instr() + next_instr()*256
        if opcode == LOAD_CONST:
            value = code.co_consts[oparg]
        elif opcode == LOAD_NAME:
            name = code.co_names[oparg]
            if name in constants:
                value = constants[name]
            elif name in __builtins__:
                value = __builtins__[name]
            else:
                # not a constant delaration
                value = undefined
        elif opcode == STORE_NAME:
            name = code.co_names[oparg]
            if value is not undefined:
                constants[name] = value
                value = undefined
        else:
            # either not a variable binding opcode or not a LOAD/STORE pairing
            value = undefined
    return constants

def get_symbols(code, _symbols=None):
    """Returns the set of names and string constants used by 'code'
    and any nested code objects."""
    if _symbols is None:
        _symbols = {}
    for name in code.co_names:
        _symbols[name] = code
    for const in code.co_consts:
        if isinstance(const, (str, unicode)):
            _symbols[const] = code
        elif isinstance(const, type(code)):
            get_symbols(const, _symbols)
    return _symbols
