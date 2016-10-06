import sys, os
from Ft.Lib.DistExt import ModuleFinder
try:
    from py2exe import build_exe
except ImportError:
    # Fake it out for non-Windows systems to allow for documenting this file
    import new
    build_exe = new.module('py2exe.build_exe')
    build_exe.py2exe = new.classobj('py2exe', (),
                                    {'__module__' : 'py2exe.build_exe'})

class py2exe(build_exe.py2exe):
    """
    Command class replacement for py2exe's that adds Ft extension module's
    hidden imports and package data.
    """

    def parse_mf_results(self, mf):
        """
        Overridden to add our "hidden" imports.
        """
        ModuleFinder.AddHiddenModules(mf)
        return build_exe.py2exe.parse_mf_results(self, mf)

    def plat_finalize(self, modules, py_files, extensions, dlls):
        """
        Overridden to also find any package data files.
        """
        build_exe.py2exe.plat_finalize(
            self, modules, py_files, extensions, dlls)

        self.data_files = ModuleFinder.GetModuleIncludes(modules)
        return

    def copy_extensions(self, extensions):
        """
        Overridden to also copy any hidden package data files to the target
        directory.
        """
        print "*** copy package data files ***"
        for source, target in self.data_files:
            # add it to the files to be stored in the ZIP archive
            self.compiled_files.append(target)
            target = os.path.join(self.collect_dir, target)
            self.mkpath(os.path.dirname(target))
            self.copy_file(source, target)

        # continue on to copying the extensions
        return build_exe.py2exe.copy_extensions(self, extensions)

# Replace default py2exe command class module with this one
sys.modules['distutils.command.py2exe'] = sys.modules[__name__]
