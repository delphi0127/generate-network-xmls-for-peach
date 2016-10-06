########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/CommandLine/Options.py,v 1.13 2005/04/13 23:41:04 jkloth Exp $
"""
Classes that support advanced option processing for command-line scripts

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from distutils.fancy_getopt import wrap_text
from Ft.Lib.CommandLine import CommandLineUtil, CONSOLE_WIDTH

class Options(list):
    """
    A set of options that are available to be used in an invocation of a
    command-line script, plus related functions.
    """
    def __init__(self, options=None):
        if options is None:
            options = ()
        list.__init__(self, options)

        # Sanity check the supplied options
        shorts = []
        longs = []
        for opt in options:
            if not isinstance(opt, BaseOption):
                raise TypeError("Option %s is not of BaseOption" % opt)
            (short, long) = opt.getForGetOpt({}, {})
            for s in short:
                if s != ':' and s in shorts:
                    raise Exception('Duplicate short option in %s' % str(self))
                shorts.append(s)
            for l in long:
                if l in longs:
                    raise Exception('Duplicate long option in %s' % str(self))
                longs.append(l)

    def findMaxOption(self, level=0):
        max_opt = 0
        for option in self:
            l = option.displayLength()

            # add two spaces for each level of sub-options
            l = l + 2*level

            if hasattr(option, 'subOptions'):
                sublen = option.subOptions.findMaxOption(level+1)
                if sublen > l:
                    l = sublen

            if l > max_opt:
                max_opt = l

        return max_opt

    def generate_help(self, level=1, max_opt=0):
        """Generate help text (a list of strings, one per suggested line of
        output) from the option table for this FancyGetopt object.
        """
        # If max_opt is > 0, this is help for a sub-option
        # maximum width has already been determined.
        if max_opt > 0:
            # The indent for sub-options is included in option length
            opt_width = max_opt - 2*(level-1)
        else:
            opt_width = max_opt = self.findMaxOption()

        # room for indent + short option + dashes + longest option + gutter + add'l indent
        col_width = 2*level + 4 + 2 + max_opt + 2 + 2

        # Typical help block looks like this:
        #   --foo       controls foonabulation
        # Help block for longest option looks like this:
        #   --flimflam  set the flim-flam level
        # and with wrapped text:
        #   --flimflam  set the flim-flam level (must be between
        #               0 and 100, except on Tuesdays)
        # Options with short names will have the short name shown (but
        # it doesn't contribute to max_opt):
        #   -f, --foo   controls foonabulation
        # If adding the short option would make the left column too wide,
        # we push the explanation off to the next line
        #   -l, --flimflam
        #               set the flim-flam level
        # Important parameters:
        #   - 2 spaces before option block start lines
        #   - 2 dashes for each long option name
        #   - min. 2 spaces between option and explanation (gutter)

        # Now generate lines of help text.
        line_width = CONSOLE_WIDTH
        text_width = line_width - col_width
        indent = '  ' * level
        big_indent = ' ' * (col_width)
        lines = []

        for option in self:
            if isinstance(option, ExclusiveOptions):
                lines.extend(option.choices.generate_help(level, max_opt))
                continue

            text = wrap_text(option.description, text_width)

            short_opt = option.shortName
            if option.takesArg:
                long_opt = '%s=<%s>' % (option.longName, option.argName)
            else:
                long_opt = option.longName
            if option.shortName:
                short_part = '-%s' % (short_opt)
            else:
                short_part = '  '
            if option.shortName and option.longName:
                short_part += ', '
            else:
                short_part += '  '
            long_part = "--%-*s" % (opt_width, long_opt)
            if text:
                lines.append('%s%s%s  %s' % (indent, short_part, long_part, text[0]))
            else:
                lines.append('%s%s%s' % (indent, short_part, long_part))

            # Add any description that didn't fit on the first line
            for line in text[1:]:
                lines.append(big_indent + line)

            if isinstance(option, TypedOption):
                for (val, desc) in option.allowed:
                    text = wrap_text(desc, text_width)
                    lines.append('%s    %-*s%s' % (indent, opt_width, val, text[0]))
                    for line in text[1:]:
                        lines.append(big_indent + line)

            if hasattr(option, 'subOptions'):
                lines.extend(option.subOptions.generate_help(level + 1, max_opt))

        return lines


class BaseOption:
    """
    An option that is available to be used in an invocation of a
    command-line script, plus related functions.
    """
    multiple = False

    def validate(self):
        return

    def getForGetOpt(self, short2long, takes_arg):
        raise NotImplementedError('subclass must override')

    def displayLength(self):
        raise NotImplementedError('subclass %s must override' % self.__class__)

    def gen_command_line(self):
        raise NotImplementedError('subclass %s must override' % self.__class__)

    def gen_description(self):
        raise NotImplementedError('subclass %s must override' % self.__class__)

    def apply_options(self, options):
        raise NotImplementedError('subclass %s must override' % self.__class__)

    def isApplied(self):
        raise NotImplementedError('subclass %s must override' % self.__class__)

    def getName(self):
        raise NotImplementedError('subclass %s must override' % self.__class__)

    def __str__(self):
        return self.gen_command_line()
    __repr__ = __str__


class Option(BaseOption):

    def __init__(self, shortName, longName, description, subOptions=None,
                 multiple=False):
        # Type- and value-check the option names
        if len(longName) < 2:
            raise SyntaxError('invalid long option: ' + longName)
        if shortName is not None and len(shortName) != 1:
            raise SyntaxError('invalid short option: ' + shortName)

        self.shortName = shortName or ''
        i = longName.find('=')
        if i > 0:
            self.takesArg = 1
            argName = longName[i+1:]
            longName = longName[:i]
            self.argName = argName or longName
        else:
            self.takesArg = 0
        self.longName = longName
        self.description = description

        if not isinstance(subOptions, Options):
            subOptions = Options(subOptions)
        self.subOptions = subOptions
        self.multiple = multiple

    def getForGetOpt(self, short2long, takes_arg):
        short_opts = self.shortName
        if self.takesArg:
            if short_opts:
                short_opts = short_opts + ':'
            long_opts = [self.longName + '=']
        else:
            long_opts = [self.longName]

        takes_arg[self.longName] = self.takesArg
        if self.shortName:
            short2long[self.shortName] = self.longName

        # get getopt options for any sub-options
        for option in self.subOptions:
            (short, long) = option.getForGetOpt(short2long, takes_arg)
            short_opts = short_opts + short
            long_opts.extend(long)

        return (short_opts, long_opts)

    def displayLength(self):
        l = len(self.longName)
        if self.takesArg:
            # add the "=argName" length
            l = l + 1 + len(self.argName)
        return l

    def validate(self):
        for option in self.subOptions:
            option.validate()

        for option in self.subOptions:
            if option.isApplied() and not self.applied:
                raise CommandLineUtil.ArgumentError("%s specified without %s" % (option.getName(),self.longName))
        return

    def apply_options(self, options):
        self.applied = options.has_key(self.longName)
        for option in self.subOptions:
            option.apply_options(options)
        return


    def isApplied(self):
        return self.applied

    def getName(self):
        return self.longName

    def gen_command_line(self):
        cl = '[--%s' % self.longName
        if self.takesArg:
            cl = cl + '=<%s>' % self.argName
        if self.subOptions:
            sub = map(lambda s: s.gen_command_line(), self.subOptions)
            if len(sub) > 1:
                cl = cl + ' [%s]' % ' '.join(sub)
            else:
                cl = cl + ' ' + sub[0]
        return cl + ']'





class TypedOption(Option):
    def __init__(self, shortName, longName, description, allowed, subOptions=None):
        Option.__init__(self, shortName, longName, description, subOptions)
        self.allowedValues = map(lambda (value, desc): value, allowed)
        self.allowed = allowed

    def apply_options(self, options):
        self.applied = options.get(self.longName)
        for option in self.subOptions:
            option.apply_options(options)
        return

    def validate(self):
        if self.applied and self.applied not in self.allowedValues:
            expected = ', '.join(self.allowedValues)
            raise SyntaxError('option %s: expected %s, got %s' %
                              (self.longName, expected, self.applied))

        Option.validate(self)
        return

    def gen_command_line(self):
        sub = ''
        for option in self.subOptions:
            sub = sub + '%s ' % option.gen_command_line()
        av = '['
        for a in self.allowedValues:
            av = av + a
            if a != self.allowedValues[-1]:
                av = av + '|'
        av =av + ']'
        if sub:
            return '[--%s=%s [%s]]' % (self.longName,av,sub)
        else:
            return '[--%s=%s]' % (self.longName,av)


class ExclusiveOptions(BaseOption):
    def __init__(self, choices):
        if not isinstance(choices, Options):
            choices = Options(choices)
        self.choices = choices

    def getForGetOpt(self, short2long, takes_arg):
        short_opts = ''
        long_opts = []
        # get getopt options for all choices
        for option in self.choices:
            (short, long) = option.getForGetOpt(short2long, takes_arg)
            short_opts = short_opts + short
            long_opts.extend(long)

        return (short_opts, long_opts)

    def displayLength(self):
        return self.choices.findMaxOption()

    def validate(self):
        # make sure only one of our choices is in the options

        applied = 0
        for opt in self.choices:
            if opt.isApplied():
                if applied:
                    opts = ', '.join(map(lambda x: '--%s' % x.getName(), self.choices))
                    raise CommandLineUtil.ArgumentError("Only one of %s allowed" % opts)
                applied = opt
        if applied:
            #NOTE, this allows some sub commands to sneak in
            applied.validate()
        else:
            #Validate them all
            for option in self.choices:
                option.validate()

    def apply_options(self, options):
        for option in self.choices:
            option.apply_options(options)
        return

    def isApplied(self):
        for option in self.choices:
            if option.isApplied(): return 1
        return 0


    def getName(self):
        return '(%s)' % ', '.join(map(lambda x: '--%s' % x.getName(), self.choices))


    def gen_command_line(self):
        cl = '['
        first = 1
        for c in self.choices:
            if not first:
                cl = cl + ' | '
            else:
                first = 0
            cl = cl + c.gen_command_line()
        return cl + ']'


