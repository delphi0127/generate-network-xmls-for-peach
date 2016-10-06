import os, glob, struct, array
from distutils import dep_util
from distutils.core import Command
from distutils.errors import DistutilsFileError

class BuildL10n(Command):

    command_name = 'build_l10n'

    description = "compile message catalog to binary format"

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" (copy) to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps"),
        ]

    def initialize_options(self):
        self.build_dir = None
        self.force = None
        return

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_l10n', 'build_dir'),
                                   ('force', 'force'))
        self.localizations = self.distribution.l10n
        return

    def run(self):
        domain = self.distribution.get_name()
        for loc in self.localizations:
            # Create the build directory for this language
            build_dir = os.path.join(self.build_dir, loc.language,
                                     'LC_MESSAGES')
            self.mkpath(build_dir)

            pofile = loc.source
            mofile = os.path.join(build_dir, domain + '.mo')

            if not (self.force or dep_util.newer(pofile, mofile)):
                self.announce("not compiling %s (up-to-date)" % pofile, 1)
                continue

            self.announce("compiling %s -> %s" % (pofile, mofile), 2)

            # Parse the catalog
            msgfmt = MsgFmt()
            msgfmt.parse(pofile)

            # Compute output
            if not self.dry_run:
                fp = open(mofile, "wb")
                try:
                    msgfmt.generate(fp)
                finally:
                    fp.close()
        return

    # -- external interfaces ------------------------------------------

    def get_outputs(self):
        outputs = []
        domain = self.distribution.get_name()
        for loc in self.localizations:
            # Create the build directory for this language
            build_dir = os.path.join(self.build_dir, loc.language,
                                     'LC_MESSAGES')
            mofile = os.path.join(build_dir, domain + '.mo')
            outputs.append(mofile)
        return outputs

    def get_source_files(self):
        return [ loc.source for loc in self.localizations ]


class MsgFmt:

    def __init__(self):
        self.__messages = {}
        return

    def add(self, id, str, fuzzy):
        "Add a non-fuzzy translation to the dictionary."
        if not fuzzy and str:
            self.__messages[id] = str

    def generate(self, fp):
        "Return the generated output."
        keys = self.__messages.keys()
        # the keys are sorted in the .mo file
        keys.sort()
        offsets = []
        ids = strs = ''
        for id in keys:
            # For each string, we need size and file offset.  Each string is
            # NUL terminated; the NUL does not count into the size.
            msgstr = self.__messages[id]
            offsets.append((len(ids), len(id), len(strs), len(msgstr)))
            ids += id + '\0'
            strs += msgstr + '\0'

        # The header is 7 32-bit unsigned integers.  We don't use hash tables,
        # so the keys start right after the index tables.
        # translated string.
        keystart = 7*4+16*len(keys)
        # and the values start after the keys
        valuestart = keystart + len(ids)
        koffsets = []
        voffsets = []
        # The string table first has the list of keys, then the list of values.
        # Each entry has first the size of the string, then the file offset.
        for o1, l1, o2, l2 in offsets:
            koffsets += [l1, o1+keystart]
            voffsets += [l2, o2+valuestart]
        offsets = koffsets + voffsets
        fp.write(struct.pack("Iiiiiii",
                             0x950412deL,       # Magic
                             0,                 # Version
                             len(keys),         # # of entries
                             7*4,               # start of key index
                             7*4+len(keys)*8,   # start of value index
                             0, 0))             # size and offset of hash table
        fp.write(array.array("i", offsets).tostring())
        fp.write(ids)
        fp.write(strs)
        return

    def parse(self, pofile):
        ID = 1
        STR = 2

        try:
            lines = open(pofile).readlines()
        except IOError, (errno, errstr):
            raise DistutilsFileError("could not read from '%s': %s" % (
                pofile, errstr))
        section = None
        fuzzy = 0

        # Parse the catalog
        lno = 0
        for l in lines:
            lno += 1
            # If we get a comment line after a msgstr, this is a new entry
            if l[0] == '#' and section == STR:
                self.add(msgid, msgstr, fuzzy)
                section = None
                fuzzy = 0
            # Record a fuzzy mark
            if l[:2] == '#,' and l.find('fuzzy'):
                fuzzy = 1
            # Skip comments
            if l[0] == '#':
                continue
            # Now we are in a msgid section, output previous section
            if l.startswith('msgid'):
                if section == STR:
                    self.add(msgid, msgstr, fuzzy)
                section = ID
                l = l[5:]
                msgid = msgstr = ''
            # Now we are in a msgstr section
            elif l.startswith('msgstr'):
                section = STR
                l = l[6:]
            # Skip empty lines
            l = l.strip()
            if not l:
                continue
            # XXX: Does this always follow Python escape semantics?
            l = eval(l)
            if section == ID:
                msgid += l
            elif section == STR:
                msgstr += l
            else:
                self.warn('Syntax error on %s:%d before: %s ' % (
                    pofile, lno, l))
                return

        # Add last entry
        if section == STR:
            self.add(msgid, msgstr, fuzzy)
        return

