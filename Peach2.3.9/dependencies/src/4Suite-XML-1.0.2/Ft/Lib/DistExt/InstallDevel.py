import InstallMisc

class InstallDevel(InstallMisc.InstallMisc):

    command_name = 'install_devel'

    description = "install developer files (tests and profiles)"

    def _get_distribution_filelists(self):
        return self.distribution.devel_files
