import InstallMisc

class InstallLocalState(InstallMisc.InstallMisc):

    command_name = 'install_localstate'

    description = "install modifiable host-specific data"

    def _get_distribution_filelists(self):
        return self.distribution.localstate_files
