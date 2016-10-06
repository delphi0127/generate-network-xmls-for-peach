import re
from distutils.version import Version, StrictVersion

__all__ = ['CommonVersion', 'VersionPredicate', 'SplitProvision',
           'SplitComparison',
           ]

class CommonVersion(Version):
    """
    Version numbering that handles most version numbering schemes.
    Implements the standard interface for version number classes as
    described by distutils.version.Version.

    A version consists of an alternating series of release numbers followed
    by an optional series of pre-release or post-release tags. A release
    number is a series of dot-separated numeric components. Release tags are
    a series of letters optionally followed by a release number. The
    pre-release tag name is alphabetically before "final". The post-release
    tag name is alphabetically greater than or equal to "final".

    For example, "1.0b2.dev-r41475" could denote Subversion revision 41475 of
    the in-development version of the second beta of release 1.0. Notice that
    "dev" is a pre-release tag, so this version is a lower version number
    than 1.0b2, which would be the actual second beta of release 1.0. But
    the "-r41475" is a post-release tag, so this version is newer than
    "1.0b2.dev".
    """

    version_re = re.compile(r'\d+(\.\d+)*')
    tag_re = re.compile(r'[_.-]?([a-zA-Z]+)?(\d+(?:\.\d)*)?')

    # 'tag_aliases' maps release tags to the tag that should be used for
    # comparison purposes.
    tag_aliases = {'pr' : 'c',
                   'pre' : 'c',
                   'preview' : 'c',
                   'rc' : 'c',
                   }

    def parse(self, vstring):
        # save the original string for use by __str__
        self._original = vstring

        def versiontuple(vstring):
            """
            Converts a dot-separated version number into a tuple of ints
            with any trailing zeros removed.
            """
            version = map(int, vstring.split('.'))
            while version and not version[-1]:
                del version[-1]
            return tuple(version)

        # Get the version number
        match = self.version_re.match(vstring)
        if not match:
            raise ValueError("invalid version number: %r" % vstring)
        self.version = versiontuple(match.group())

        # Check for pre- and post-release tags
        tags = []
        start = match.end()
        end = len(vstring)
        while start < end:
            match = self.tag_re.match(vstring, start)
            if not match:
                raise ValueError("invalid release tag: %r" % vstring[start:])
            tag, version = match.groups()
            tag = tag and tag.lower()
            if tag in self.tag_aliases:
                tag = self.tag_aliases[tag]
            if version:
                version = versiontuple(version)
            else:
                version = None
            tags.append((tag, version))
            start = match.end()
        self.tags = tuple(tags)
        return

    def __str__(self):
        return self._original

    def __cmp__(self, other):
        if isinstance(other, str):
            other = self.__class__(other)
        compare = cmp(self.version, other.version)
        if compare == 0:
            compare = cmp(self.tags, other.tags)
        return compare

try:
    from distutils.versionpredicate import VersionPredicate, \
         split_provision as SplitProvision, \
         splitUp as SplitComparison
except ImportError:
    import operator

    re_validPackage = re.compile(r"(?i)^\s*([a-z_]\w*(?:\.[a-z_]\w*)*)(.*)")
    re_paren = re.compile(r"^\s*\((.*)\)\s*$") # (list) inside of parentheses
    re_provision = re.compile(
        "([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)(?:\s*\(\s*([^)\s]+)\s*\))?$")
    re_splitComparison = re.compile(r"^\s*(<=|>=|<|>|!=|==)\s*([^\s,]+)\s*$")

    compmap = {"<": operator.lt, "<=": operator.le, "==": operator.eq,
               ">": operator.gt, ">=": operator.ge, "!=": operator.ne}

    class VersionPredicate:
        """
        Parse and test package version predicates.
        """

        def __init__(self, versionPredicateStr):
            """Parse a version predicate string."""
            # Fields:
            #    name:  package name
            #    pred:  list of (comparison string, StrictVersion)

            versionPredicateStr = versionPredicateStr.strip()
            if not versionPredicateStr:
                raise ValueError("empty package restriction")
            match = re_validPackage.match(versionPredicateStr)
            if not match:
                raise ValueError("bad package name in %r" % versionPredicateStr)
            self.name, paren = match.groups()
            paren = paren.strip()
            if paren:
                match = re_paren.match(paren)
                if not match:
                    raise ValueError("expected parenthesized list: %r" % paren)
                str = match.groups()[0]
                self.pred = [ SplitComparison(p) for p in str.split(",") ]
                if not self.pred:
                    raise ValueError("empty parenthesized list in %r"
                                     % versionPredicateStr)
            else:
                self.pred = []

        def __str__(self):
            if self.pred:
                seq = [cond + " " + str(ver) for cond, ver in self.pred]
                return self.name + " (" + ", ".join(seq) + ")"
            else:
                return self.name

        def satisfied_by(self, version):
            """True if version is compatible with all the predicates in self.
            The parameter version must be acceptable to the StrictVersion
            constructor.  It may be either a string or StrictVersion.
            """
            for cond, ver in self.pred:
                if not compmap[cond](version, ver):
                    return False
            return True

    # originally distutils.versionpredicate.split_provision()
    def SplitProvision(value):
        """Return the name and optional version number of a provision.

        The version number, if given, will be returned as a `StrictVersion`
        instance, otherwise it will be `None`.
        """
        value = value.strip()
        m = re_provision.match(value)
        if not m:
            raise ValueError("illegal provides specification: %r" % value)
        ver = m.group(2) or None
        if ver:
            ver = StrictVersion(ver)
        return m.group(1), ver

    # originally distutils.versionpredicate.splitUp()
    def SplitComparison(pred):
        """Parse a single version comparison.

        Return (comparison string, StrictVersion)
        """
        res = re_splitComparison.match(pred)
        if not res:
            raise ValueError("bad package restriction syntax: %r" % pred)
        comp, verStr = res.groups()
        return (comp, StrictVersion(verStr))

