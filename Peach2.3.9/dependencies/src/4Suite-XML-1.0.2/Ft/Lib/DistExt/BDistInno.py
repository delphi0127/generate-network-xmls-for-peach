import os
import sys
import zipfile
from distutils import util
from distutils.core import Command
from distutils.errors import DistutilsInternalError, DistutilsPlatformError
from distutils.dir_util import remove_tree
from distutils.sysconfig import get_python_version

INNO_MIN_VERSION = '5.1.5'
INNO_MAX_VERSION = '5.1.7'

PY_SOURCE_EXTS = ('.py', '.pyw')

ISCC_TEMPLATE = r"""
[Setup]
OutputDir=%(output-dir)s
OutputBaseFilename=%(output-basename)s
Compression=lzma
SolidCompression=yes
AppName=%(name)s
AppVersion=%(version)s
AppVerName=%(name)s %(version)s for Python %(target-version)s
AppId=%(name)s-%(target-version)s
AppPublisher=%(publisher)s
AppPublisherURL=%(publisher-url)s
AppSupportURL=%(support-url)s
UninstallFilesDir=%(uninstall-dir)s
DefaultDirName={code:GetDefaultDir}
DefaultGroupName={code:GetDefaultGroup}
LicenseFile=%(license-file)s
UserInfoPage=no
DisableReadyMemo=yes
DirExistsWarning=no
AppendDefaultDirName=no

[Types]
Name: "full"; Description: "Full installation"
Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
%(components)s

%(sections)s

[Code]
{ Define parameters as constants to easy sharing between the script file
  and the template in BDistInno.py }
const
  GroupName = '%(name)s';
  TargetVersion = '%(target-version)s';

var
  PythonDir, PythonGroup: String;

function GetDefaultDir(Param: String): String;
begin
  Result := RemoveBackslashUnlessRoot(PythonDir);
end; { GetDefaultDir }

function GetDefaultGroup(Param: String): String;
begin
  Result := AddBackslash(PythonGroup) + GroupName;
end; { GetDefaultGroup }

procedure MutateConfigFile(Filename: String);
var
  Config: String;
  Prefix: String;
begin
  Filename := ExpandConstant(Filename);
  LoadStringFromFile(Filename, Config);
  Prefix := AddBackslash(WizardDirValue());
  StringChange(Prefix, '\', '\\')
  StringChange(Config, '\\PREFIX\\', Prefix);
  SaveStringToFile(Filename, Config, False);
end; { MutateConfigFile }

procedure InitializeSelectDirPage;
var
  Page: TWizardPage;
  Text: TLabel;
  Top, Left, Width: Integer;
begin
  Page := PageFromID(wpSelectDir);
  Top := WizardForm.DirEdit.Top + WizardForm.DirEdit.Height + 16;
  Left := WizardForm.SelectDirBrowseLabel.Left;
  Width := WizardForm.SelectDirBrowseLabel.Width;

  Text := TLabel.Create(Page);
  Text.Parent := Page.Surface;
  Text.Top := Top;
  Text.Left := Left;
  Text.Font.Style := [fsBold];
  Text.AutoSize := True;
  Text.WordWrap := True;
  Text.Width := Width;
  Text.Caption := 'Warning: A valid Python ' + TargetVersion +
                  ' installation could not be found.';
  Top := Top + Text.Height + 16;

  Text := TLabel.Create(Page);
  Text.Parent := Page.Surface;
  Text.Top := Top;
  Text.Left := Left;
  Text.AutoSize := True;
  Text.WordWrap := True;
  Text.Width := Width;
  Text.Caption := 'If you have a custom build of Python installed, select' +
                  ' the folder where it is installed as the installation' +
                  ' location.';
end; { InitializeSelectDirPage }

procedure InitializeWizard;
begin
  { Add customizations to the SelectDir page if Python is not found }
  if PythonDir = '' then
    InitializeSelectDirPage;
end; { InitializeWizard }

function InitializeSetup(): Boolean;
var
  Key: String;
begin
  { Get the default installation directory }
  Key := 'Software\Python\PythonCore\' + TargetVersion + '\InstallPath';
  if not RegQueryStringValue(HKEY_CURRENT_USER, Key, '', PythonDir) then
    RegQueryStringValue(HKEY_LOCAL_MACHINE, Key, '', PythonDir);

  { Get default Start Menu group }
  Key := Key + '\InstallGroup';
  if not RegQueryStringValue(HKEY_CURRENT_USER, Key, '', PythonGroup) then
    RegQueryStringValue(HKEY_LOCAL_MACHINE, Key, '', PythonGroup);

  Result := True;
end; { InitializeSetup }

function NextButtonClick(CurPage: Integer): Boolean;
begin
  Result := True;
  if CurPage = wpSelectDir then
  begin
    { Check that the install directory is part of PYTHONPATH }
  end
end; { NextButtonClick }
"""

class Section(object):
    section_name = None
    required_parameters = None
    optional_parameters = ['Languages', 'MinVersion', 'OnlyBelowVersion',
                           'BeforeInstall', 'AfterInstall']

    def __init__(self):
        assert self.section_name is not None, \
            "'section_name' must be defined"
        assert self.required_parameters is not None, \
            "'required_parameters' must be defined"
        self.entries = []

    def addEntry(self, **parameters):
        entry = []
        # Add the required parameters
        for parameter in self.required_parameters:
            try:
                value = parameters[parameter]
            except KeyError:
                raise DistutilsInternalError(
                    "missing required parameter '%s'" % parameter)
            else:
                del parameters[parameter]
            entry.append('%s: %s' % (parameter, value))
        # Add any optional parameters.
        for parameter in self.optional_parameters:
            if parameter in parameters:
                entry.append('%s: %s' % (parameter, parameters[parameter]))
                del parameters[parameter]
        # Any remaining parameters are errors.
        for parameter in parameters:
            raise DistutilsInternalError(
                "unsupported parameter '%s'" % parameter)
        # Create the entry string and store it.
        self.entries.append('; '.join(entry))
        return

class DirsSection(Section):
    section_name = 'Dirs'
    required_parameters = ['Name']
    optional_parameters = Section.optional_parameters + [
        'Attribs', 'Permissions', 'Flags']

class FilesSection(Section):
    section_name = 'Files'
    required_parameters = ['Source', 'DestDir']
    optional_parameters = Section.optional_parameters + [
        'DestName', 'Excludes', 'CopyMode', 'Attribs', 'Permissions',
        'FontInstall', 'Flags']

class IconsSection(Section):
    section_name = 'Icons'
    required_parameters = ['Name', 'Filename']
    optional_parameters = Section.optional_parameters + [
        'Parameters', 'WorkingDir', 'HotKey', 'Comment', 'IconFilename',
        'IconIndex', 'Flags']

class RunSection(Section):
    section_name = 'Run'
    required_parameters = ['Filename']
    optional_parameters = Section.optional_parameters + [
        'Description', 'Parameters', 'WorkingDir', 'StatusMsg', 'RunOnceId',
        'Flags']

class UninstallDeleteSection(Section):
    section_name = 'UninstallDelete'
    required_parameters = ['Type', 'Name']

class Component:
    section_mapping = {
        'Dirs' : DirsSection,
        'Files' : FilesSection,
        'Icons' : IconsSection,
        'Run' : RunSection,
        'UninstallDelete' : UninstallDeleteSection,
        }

    def __init__(self, name, description, types):
        self.name = name
        self.description = description
        self.types = types
        self.sections = {}

    def getEntry(self):
        return 'Name: "%s"; Description: "%s"; Types: %s' % (
            self.name, self.description, self.types)

    def hasEntries(self):
        for section in self.sections.itervalues():
            if section.entries:
                return True
        return False

    def getSection(self, name):
        if name not in self.sections:
            try:
                section_class = self.section_mapping[name]
            except KeyError:
                raise DistutilsInternalError("unknown section '%s'" % name)
            self.sections[name] = section_class()
        return self.sections[name]

    def getSectionEntries(self, name):
        return [ '%s; Components: %s' %(entry, self.name)
                 for entry in self.getSection(name).entries ]

class BDistInno(Command):

    command_name = 'bdist_inno'

    description = "create an executable installer for MS Windows"

    user_options = [
        ('bdist-dir=', None,
         "temporary directory for creating the distribution"),
        ('keep-temp', 'k',
         "keep the pseudo-installation tree around after " +
         "creating the distribution archive"),
        ('target-version=', None,
         "require a specific python version on the target system"),
        ('no-target-compile', 'c',
         "do not compile .py to .pyc on the target system"),
        ('no-target-optimize', 'o',
         "do not compile .py to .pyo (optimized) on the target system"),
        ('dist-dir=', 'd',
         "directory to put final built distributions in"),
        ('skip-build', None,
         "skip rebuilding everything (for testing/debugging)"),
        ]

    boolean_options = ['keep-temp', 'no-target-compile', 'no-target-optimize',
                       'skip-build']

    def initialize_options(self):
        self.bdist_dir = None
        self.keep_temp = None
        self.target_version = None
        self.no_target_compile = None
        self.no_target_optimize = None
        self.dist_dir = None
        self.skip_build = None
        self.byte_compile = True
        return

    def finalize_options(self):
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'inno')

        self.set_undefined_options('bdist',
                                   ('keep_temp', 'keep_temp'),
                                   ('dist_dir', 'dist_dir'),
                                   ('skip_build', 'skip_build'))

        if not self.target_version:
            self.target_version = get_python_version()
        if not self.skip_build and (self.distribution.has_ext_modules() or
                                    self.distribution.has_scripts()):
            short_version = get_python_version()
            if self.target_version != short_version:
                raise DistutilsOptionError(
                    "target version can only be %s, or the '--skip_build'"
                    " option must be specified" % short_version)
            self.target_version = short_version

        self.license_file = self.distribution.license_file
        if self.license_file:
            self.license_file = util.convert_path(self.license_file)

        self.output_basename = '%s.win32'
        return

    def run(self):
        if sys.platform != 'win32':
            raise DistutilsPlatformError("InnoSetup distributions must be"
                                         " created on a Windows platform")
        # Locate information about Inno Setup from the registry
        from _winreg import OpenKeyEx, QueryValueEx, HKEY_LOCAL_MACHINE
        try:
            key = OpenKeyEx(HKEY_LOCAL_MACHINE,
                            r'SOFTWARE\Microsoft\Windows'
                            r'\CurrentVersion\Uninstall'
                            r'\Inno Setup 5_is1')
            inno_version = QueryValueEx(key, 'DisplayVersion')[0]
            inno_path = QueryValueEx(key, 'InstallLocation')[0]
        except WindowsError:
            raise DistutilsPlatformError(
                'Inno Setup version %s to %s is required to build the'
                ' installer, but was not found on this system.' %
                (INNO_MIN_VERSION, INNO_MAX_VERSION))
        if inno_version < INNO_MIN_VERSION or inno_version > INNO_MAX_VERSION:
            raise DistutilsPlatformError(
                'Inno Setup version %s to %s is required to build the'
                ' installer, but version %s was found on this system.' %
                (INNO_MIN_VERSION, INNO_MAX_VERSION, inno_version))
        iss_compiler = os.path.join(inno_path, 'iscc.exe')

        if not self.skip_build:
            self.run_command('build')

        self.mkpath(self.bdist_dir)

        config = self.reinitialize_command('config')
        config.cache_filename = None
        config.prefix = 'PREFIX'
        config.ensure_finalized()

        install = self.reinitialize_command('install')
        install.root = self.bdist_dir
        install.skip_build = self.skip_build

        # Always include "compiled" py-files
        install.compile = install.optimize = self.byte_compile

        # don't warn about installing into a directory not in sys.path
        install.warn_dir = False

        # always include documentation
        install.with_docs = True

        self.announce("installing to %s" % self.bdist_dir, 2)
        install.ensure_finalized()
        install.run()

        if self.license_file:
            self.copy_file(self.license_file, self.bdist_dir)

        # create the InnoSetup script
        iss_file = self.build_iss_file()
        iss_path = os.path.join(self.bdist_dir,
                                '%s.iss' % self.distribution.get_name())
        self.announce("writing %r" % iss_path)
        if not self.dry_run:
            f = open(iss_path, "w")
            f.write(iss_file)
            f.close()

        # build distribution using the Inno Setup 5 Command-Line Compiler
        self.announce("creating Inno Setup installer", 2) # log.info
        self.spawn([iss_compiler, iss_path])

        # Add an empty ZIP file to the installer executable to allow for
        # uploading to PyPI (it checks for the bdist_wininst format).
        dist_filename = self.get_installer_filename()
        if os.path.exists(dist_filename) and not self.dry_run:
            install_egg_info = self.get_finalized_command('install_egg_info')
            install_dir = install_egg_info.install_dir
            zip_dir = 'PLATLIB'
            if install_dir.endswith(os.sep):
                zip_dir += os.sep
            zip_file = zipfile.ZipFile(dist_filename, 'a')
            for filename in install_egg_info.get_outputs():
                arcname = filename.replace(install_dir, zip_dir, 1)
                zip_file.write(filename, arcname)
            zip_file.close()

        # Add to 'Distribution.dist_files' so that the "upload" command works
        if hasattr(self.distribution, 'dist_files'):
            target_version = self.target_version or 'any'
            spec = ('bdist_wininst', target_version, dist_filename)
            self.distribution.dist_files.append(spec)

        if not self.keep_temp:
            remove_tree(self.bdist_dir, self.verbose, self.dry_run)
        return

    def build_iss_file(self):
        """Generate the text of an InnoSetup iss file and return it as a
        list of strings (one per line).
        """
        # [Icons]
        filespec = 'Source: "%s"; DestDir: "%s"; Components: %s'
        dirspec = 'Name: "%s"; Components: %s'
        uninstallspec = 'Type: files; Name: "%s"'
        iconspec = 'Name: "%s"; Filename: "%s"; Components: %s'
        runspec = ('Description: "%s"; Filename: "%s"; Components: %s; '
                   'Flags: %s')

        main_component = Component('Main',
                                   self.distribution.get_name() + ' Library',
                                   'full compact custom')
        docs_component = Component('Main\\Documentation', 'Documentation',
                                   'full')
        test_component = Component('Main\\Testsuite', 'Test suite', 'full')

        install = self.get_finalized_command('install')
        for command_name in install.get_sub_commands():
            command = self.get_finalized_command(command_name)
            # Get the mutated outputs split by type.
            dirs, files, uninstall = self._mutate_outputs(command)
            # Perform any command-specific processing
            if command_name == 'install_html':
                component = docs_component
                for document in command.documents:
                    flags = getattr(document, 'flags', ())
                    if 'postinstall' in flags:
                        section = component.getSection('Run')
                        filename = command.get_output_filename(document)
                        filename = self._mutate_filename(filename)[1]
                        section.addEntry(
                            Description='"View %s"' % document.title,
                            Filename='"%s"' % filename,
                            Flags='postinstall shellexec skipifsilent')
                    if 'shortcut' in flags:
                        section = component.getSection('Icons')
                        filename = command.get_output_filename(document)
                        filename = self._mutate_filename(filename)[1]
                        section.addEntry(
                            Name='"{group}\\%s"' % document.title,
                            Filename='"%s"' % filename)
            elif command_name == 'install_text':
                component = docs_component
            elif command_name == 'install_devel':
                component = test_component
            elif command_name == 'install_config':
                component = main_component
                section = component.getSection('Files')
                for source, destdir, extra in files:
                    dest = os.path.join(destdir, os.path.basename(source))
                    extra['AfterInstall'] = "MutateConfigFile('%s')" % dest
            else:
                component = main_component

            if dirs:
                section = component.getSection('Dirs')
                for name in dirs:
                    section.addEntry(Name='"%s"' % name)
            if files:
                section = component.getSection('Files')
                for source, destdir, extra in files:
                    section.addEntry(Source='"%s"' % source,
                                     DestDir='"%s"' % destdir,
                                     Flags='ignoreversion',
                                     **extra)
            if uninstall:
                section = component.getSection('UninstallDelete')
                for name in uninstall:
                    section.addEntry(Type='files',
                                     Name='"%s"' % name)

        components = []
        sections = {}
        for component in (main_component, docs_component, test_component):
            has_entries = False
            for section in component.sections:
                entries = component.getSectionEntries(section)
                if entries:
                    has_entries = True
                    if section not in sections:
                        sections[section] = ['[%s]' % section]
                    sections[section].extend(entries)
            if has_entries:
                components.append(component.getEntry())
        components = '\n'.join(components)

        for name in sections:
            sections[name] = '\n'.join(sections[name])
        sections = '\n\n'.join(sections.values())

        output_filename = self.get_installer_filename()
        output_dir, output_basename = os.path.split(output_filename)
        output_basename = os.path.splitext(output_basename)[0]
        uninstall_dir = os.path.join(install.install_localstate, 'Uninstall')
        _, uninstall_dir = self._mutate_filename(uninstall_dir)
        subst = {
            'output-dir' : os.path.abspath(output_dir),
            'output-basename' : output_basename,
            'name' : self.distribution.get_name(),
            'version' : self.distribution.get_version(),
            'publisher' : self.distribution.get_author(),
            'publisher-url' : self.distribution.get_author_email(),
            'support-url' : self.distribution.get_url(),
            'uninstall-dir' : uninstall_dir,
            'license-file' : os.path.basename(self.license_file or ''),
            'target-version' : sys.version[:3],
            'custom-page' : self.license_file and 'wpLicense' or 'wpWelcome',
            'components' : components,
            'sections' : sections,
            }

        return ISCC_TEMPLATE % subst

    def _mutate_filename(self, filename):
        # Strip the bdist_dir from the filename as the files will be
        # relative to the setup script which is in bdist_dir.  This
        # is to make the setup script more readable.
        source = filename[len(self.bdist_dir) + len(os.sep):]
        # Translate the filename to what is used in the setup script
        dest = source.replace('PREFIX', '{app}', 1)
        return source, dest

    def _mutate_outputs(self, command):
        dirs = []
        files = []
        uninstall = []
        compile = getattr(command, 'compile', 0)
        optimize = getattr(command, 'optimize', 0)
        for filename in command.get_outputs():
            source, dest = self._mutate_filename(filename)
            if os.path.isdir(filename):
                # An empty directory
                dirs.append(dest)
            else:
                files.append((source, os.path.dirname(dest), {}))
                # Add uninstall entries for possible bytecode files created
                # *after* installation.
                for extension in PY_SOURCE_EXTS:
                    if dest.endswith(extension):
                        barename = dest[:-len(extension)]
                        if not compile:
                            uninstall.append(barename + '.pyc')
                        if not optimize:
                            uninstall.append(barename + '.pyo')
        return dirs, files, uninstall

    def get_installer_filename(self):
        installer_name = '%s.win32' % self.distribution.get_fullname()
        if self.target_version:
            # if we create an installer for a specific python version,
            # include this in the name to match bdist_wininst.
            installer_name += '-py' + self.target_version
        return os.path.join(self.dist_dir, installer_name + '.exe')
