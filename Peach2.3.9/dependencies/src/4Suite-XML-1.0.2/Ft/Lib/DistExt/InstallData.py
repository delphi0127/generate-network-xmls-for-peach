from Ft.Lib.DistExt import InstallMisc, Structures

class InstallData(InstallMisc.InstallMisc):

    command_name = 'install_data'

    description = "install read-only platform-independent files"

    def _get_distribution_filelists(self):
        filelists = []

        if self.distribution.has_data_files():
            filelists.extend(self.distribution.data_files)

        return filelists
