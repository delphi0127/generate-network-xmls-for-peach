########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/CommandLine/Command.py,v 1.13.6.1 2006/10/16 21:52:34 jkloth Exp $
"""
Superclass for a command that can be invoked by a command-line script.

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys

import CommandLineUtil
import FancyGetOpt

from Ft.Lib.CommandLine import CONSOLE_WIDTH, Options, Arguments
from Ft.Lib.CommandLine.CommandLineUtil import ArgumentError

class Command:
    """
    Superclass for a command that can be invoked by a command-line script.
    Most commands won't need to subclass this.

    A Command object encapsulates, for a particular command, a description,
    usage example, a set of valid options & arguments, methods for
    validating the actual options and arguments entered, a function for
    command invocation, and an association with subordinate Commands.

    A tree of commands can be created by associating each Command instance
    with its subordinates. Typically, only the leaves of the tree will have
    functionality; the branches just provide ways of grouping the leaves
    and will not need to encapsulate the invocation functions themselves.
    """ # -- clear as mud. how about some examples
    def __init__(self,
                 name,
                 description,
                 example,
                 verbose_description,
                 function=None,
                 options=None,
                 arguments=None,
                 subCommands=None,
                 fileName=None,
                 ):

        self.name = name
        self.description = description
        self.function = function
        self.example = example
        self.verbose_description = verbose_description
        self.options = options or Options.Options()
        self.arguments = arguments or []
        self.subCommands = subCommands or {}
        self._fileName = fileName

        if isinstance(self.subCommands, (list, tuple)):
            cmds = {}
            for c in self.subCommands:
                cmds[c.name] = c
            self.subCommands = cmds

        if not isinstance(self.options, Options.Options):
            # Options constructor takes care of validating option values
            self.options = Options.Options(self.options)

        for arg in self.arguments:
            if not isinstance(arg, Arguments.Argument):
                raise ValueError("argument %d is not an instance of Argument"
                                 % self.arguments.index(arg))
        return

    def build_parent_relationship(self):
        for c in self.subCommands.values():
            c.parent = self
            c.build_parent_relationship()

    def break_parent_relationship(self):
        for c in self.subCommands.values():
            if hasattr(c,'parent'):
                delattr(c,'parent')
            c.break_parent_relationship()


    def flatten_command_tree(self,level,previousName=''):
        if previousName:
            fName = previousName + '.' + self.name
        else:
            fName = self.name

        res = [(level,self,fName)]
        names = self.subCommands.keys()
        names.sort()
        for name in names:
            res.extend(self.subCommands[name].flatten_command_tree(
                level+1,previousName = fName))
        return res


    def run(self, options, arguments):
        if not self.function:
            raise CommandLineUtil.ArgumentError(self, "subcommand required")
        return self.function(options, arguments)


    def validate_arguments(self, arglist):
        eatenArgs = {}
        arglist = filter(str.strip, arglist)
        for arg in self.arguments:
            eaten, arglist = arg.validate(self, arglist)
            if eaten is not None:
                eatenArgs[arg.name] = eaten
        if arglist:
            raise ArgumentError(self, "invalid argument %s" % arglist[0])
        return eatenArgs

    def validate_options(self,options):
        if options.get('help'):
            raise ArgumentError(self, '')
        for opt in self.options:
            opt.apply_options(options)
        for opt in self.options:
            opt.validate()
        return 1


    def _gen_usage(self,command_string):
        """
        Generates the usage summary, example command line, and
        descriptions of options and subcommands or arguments
        """
        lines = self.__gen_command_line_help(command_string)

        # saved for use in the example
        command_size = len(command_string)

        # generate the example, if available
        if self.example is not None:
            lines.append('\nExample:')
            text_width = CONSOLE_WIDTH - command_size
            text = CommandLineUtil.wrap_text(self.example, text_width)
            lines.append(command_string + text[0])
            indent = ' ' * command_size
            lines.extend([ indent + s for s in text[1:] ])

        # generate the option descriptions
        option_desc = self.options.generate_help()
        if option_desc:
            lines.append('\nOptions:')
            lines.extend(option_desc)

        # generate the subcommand descriptions
        if self.subCommands:
            max_cmd = 0
            for cmd in self.subCommands.keys():
                if len(cmd) > max_cmd:
                    max_cmd = len(cmd)

            lines.append('\nSubcommands:')
            # column size = indent + longest command + gutter
            indent = ' ' * (2 + max_cmd + 2) + '  '
            text_width = CONSOLE_WIDTH - len(indent)
            names = self.subCommands.keys()
            names.sort()
            for name in names:
                cmd = self.subCommands[name]
                text = CommandLineUtil.wrap_text(cmd.description,
                                                 text_width)
                lines.append('  %-*s  %s' % (max_cmd, name, text[0]))
                lines.extend([ indent + s for s in text[1:] ])

        # generate the argument descriptions
        if self.arguments:
            max_arg = 0
            for arg in self.arguments:
                if len(arg.name) > max_arg:
                    max_arg = len(arg.name)

            lines.append('\nArguments:')
            # column size = indent + longest command + gutter
            indent = ' ' * (2 + max_arg + 2)
            text_width = CONSOLE_WIDTH - len(indent)
            for arg in self.arguments:
                text = CommandLineUtil.wrap_text(arg.description,
                                                 text_width)
                lines.append('  %-*s  %s' % (max_arg, arg.name,
                                             text[0]))
                lines.extend([ indent + s for s in text[1:] ])

        lines.append('')    # add a blank line
        return lines


    def _parse_command_opts(self, arglist):
        options, arglist = FancyGetOpt.FancyGetopt(self, self.options, arglist)
        if not self.validate_options(options):
            return None

        # Args can either be a subcommand, or the start of the argument
        # list. Subcommand takes precedence.
        if self.subCommands:
            try:
                cmd = arglist[0]
            except IndexError:
                msg = "subcommand required"
                raise CommandLineUtil.ArgumentError(self, msg)
            try:
                cmd = self.subCommands[cmd]
            except KeyError:
                msg = "invalid subcommand: %s" % cmd
                raise CommandLineUtil.ArgumentError(self, msg)
            parsed = cmd._parse_command_opts(arglist[1:])
        else:
            parsed = (self, options, self.validate_arguments(arglist))
        return parsed


    def __gen_command_line_help(self, command_string):
        """
        Generates the indented usage summary only.
        """
        # command_string looks like this: '  4ss create user '
        # i.e., it is '4ss create user', indented and ready to
        # have the option & argument syntax appended like so:
        # '  4ss create user (syntax line 1)
        #                    (syntax line 2)
        #                    (syntax line 3)'

        # generate the option/arg syntax string, which looks like this:
        # '[--help] [[--username=<USER>] | [--anonymous]]
        #  [--password=<PASSWORD>] [--port=<PORT>] [--host=<HOST>]
        #  [--container=<PATH>] userName '
        syntax_string = ''
        for opt in self.options:
            syntax_string += opt.gen_command_line() + ' '
        if self.subCommands:
            if len(self.arguments):
                syntax_string += '['
            syntax_string += '<subcommand> '
            if len(self.arguments):
                syntax_string += '['
            syntax_string += '<subcommand> '
            if len(self.arguments):
                syntax_string += '] | ['
        if self.arguments:
            for arg in self.arguments:
                syntax_string += arg.gen_command_line() + ' '
            if self.subCommands:
                syntax_string += ']'

        # wrap the syntax line to a width that won't exceed the console
        # width when appended to command_string
        command_size = len(command_string)
        syntax_string_lines = CommandLineUtil.wrap_text(
            syntax_string, CONSOLE_WIDTH - command_size)

        # append first line of wrapped syntax string to command_string
        # and indent the remaining lines appropriately
        lines = [command_string + syntax_string_lines[0]]
        indent = ' ' * command_size
        lines.extend([ indent + s for s in syntax_string_lines[1:] ])


        return lines
