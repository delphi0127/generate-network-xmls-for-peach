from Ft.Lib.CommandLine import CommandLineApp
from Ft.Lib.DistExt.Formatters import XmlFormatter

class CommandLineFormatter(XmlFormatter.XmlFormatter):

    document_type = CommandLineApp.CommandLineApp

    def document(self, application):
        attributes = {'name' : application.name}
        self.start_element('application', attributes)
        self.doc_command(application)
        self.end_element('application')
        return

    def doc_command(self, command):
        if command.description:
            self.write_element('description',
                               content=self.escape(command.description))

        if command.verbose_description:
            self.write_element('verbose-description',
                               content=self.escape(command.verbose_description))

        if command.example:
            self.write_element('example',
                               content=self.escape(command.example))

        if command.options:
            options = map(lambda opt: (None, opt), command.options)
            self.section('options', options, self.doc_option)

        if command.arguments:
            arguments = map(lambda arg: (arg.name, arg), command.arguments)
            self.section('arguments', arguments, self.doc_argument)

        if command.subCommands:
            subcommands = command.subCommands.items()
            self.section('subcommands', subcommands, self.doc_subcommand)
        return

    def doc_subcommand(self, command, name):
        assert name == command.name
        self.start_element('command', {'name' : name})
        self.doc_command(command)
        self.end_element('command')
        return

    def doc_option(self, option, name):
        if hasattr(option, 'choices'):
            options = map(lambda opt: (None, opt), option.choices)
            self.section('exclusive-options', options, self.doc_option)
        else:
            attributes = {'long-name' : option.longName}

            if option.shortName:
                attributes['short-name'] = option.shortName

            self.start_element('option', attributes)

            desc = self.escape(option.description)
            self.write_element('description', content=desc)

            if option.takesArg or hasattr(option, 'allowed'):
                self.start_element('argument', {'name' : option.argName})
                for name, description in getattr(option, 'allowed', []):
                    self.start_element('value', {'name' : name})
                    desc = self.escape(description)
                    self.write_element('description', content=desc)
                    self.end_element('value')
                self.end_element('argument')

            if option.subOptions:
                options = map(lambda opt: (None, opt), option.subOptions)
                self.section('suboptions', options, self.doc_option)

            self.end_element('option')
        return

    def doc_argument(self, argument, name):
        attributes = {
            'name' : name,
            'required' : argument.requirements in [1, 4] and 'yes' or 'no',
            'multiple' : argument.requirements in [3, 4] and 'yes' or 'no',
            }
        self.start_element('argument', attributes)
        desc = self.escape(argument.description)
        self.write_element('description', content=desc)

        self.end_element('argument')
        return
