########################################################################
# $Header: /var/local/cvsroot/4Suite/docs/docs-README.txt,v 1.3 2005/10/25 02:03:30 mbrown Exp $

This is the README for the docs directory.

There is nothing in this directory for end users.

At build time, if --with-docs is set, then API documentation is
generated in an XML format based on module introspection and files in
the ../packages directory. This XML, along with the static files in the
./xml directory, is transformed into HTML (and possibly plain text).

At install time, if --with-docs is set, then the generated HTML docs
are moved to the directory given with --docdir, the defaults for which
are shown in http://4suite.org/docs/installation-locations.xhtml

Some pregenerated docs may also be downloaded and installed separately,
or browsed on the web at http://4suite.org/
