'''Functions to manage apport problem report files.'''

# Copyright (C) 2006 - 2009 Canonical Ltd.
# Author: Martin Pitt <martin.pitt@ubuntu.com>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import os, glob, subprocess, os.path

try:
    from configparser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    # Python 2
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError

from problem_report import ProblemReport

report_dir = os.environ.get('APPORT_REPORT_DIR', '/var/crash')

#_config_file = '~/.config/apport/settings'
#def find_package_desktopfile(package):
#def likely_packaged(file):
#def find_file_package(file):
#def seen_report(report):
#def mark_report_seen(report):
#def get_config(section, setting, default=None, bool=False):
#get_config.config = None

def get_all_reports():
    '''Return a list with all report files accessible to the calling user.'''

    reports = []
    for r in glob.glob(os.path.join(report_dir, '*.crash')):
        try:
            if os.path.getsize(r) > 0 and os.access(r, os.R_OK):
                reports.append(r)
        except OSError:
            # race condition, can happen if report disappears between glob and
            # stat
            pass
    return reports

def get_new_reports():
    '''Get new reports for calling user.

    Return a list with all report files which have not yet been processed
    and are accessible to the calling user.
    '''
    reports = []
    for r in get_all_reports():
        try:
            if not seen_report(r):
                reports.append(r)
        except OSError:
            # race condition, can happen if report disappears between glob and
            # stat
            pass
    return reports

def get_all_system_reports():
    '''Get all system reports.

    Return a list with all report files which belong to a system user (i. e.
    uid < 500 according to LSB).
    '''
    reports = []
    for r in glob.glob(os.path.join(report_dir, '*.crash')):
        try:
            if os.path.getsize(r) > 0 and os.stat(r).st_uid < 500:
                reports.append(r)
        except OSError:
            # race condition, can happen if report disappears between glob and
            # stat
            pass
    return reports

def get_new_system_reports():
    '''Get new system reports.

    Return a list with all report files which have not yet been processed
    and belong to a system user (i. e. uid < 500 according to LSB).
    '''
    return [r for r in get_all_system_reports() if not seen_report(r)]

def delete_report(report):
    '''Delete the given report file.

    If unlinking the file fails due to a permission error (if report_dir is not
    writable to normal users), the file will be truncated to 0 bytes instead.
    '''
    try:
        os.unlink(report)
    except OSError:
        open(report, 'w').truncate(0)

def get_recent_crashes(report):
    '''Return the number of recent crashes for the given report file.

    Return the number of recent crashes (currently, crashes which happened more
    than 24 hours ago are discarded).
    '''
    pr = ProblemReport()
    pr.load(report, False)
    try:
        count = int(pr['CrashCounter'])
        report_time = time.mktime(time.strptime(pr['Date']))
        cur_time = time.mktime(time.localtime())
        # discard reports which are older than 24 hours
        if cur_time - report_time > 24*3600:
            return 0
        return count
    except (ValueError, KeyError):
        return 0

def make_report_path(report, uid=None):
    '''Construct a canonical pathname for the given report.

    If uid is not given, it defaults to the uid of the current process.
    '''
    if 'ExecutablePath' in report:
        subject = report['ExecutablePath'].replace('/', '_')
    elif 'Package' in report:
        subject = report['Package'].split(None, 1)[0]
    else:
        raise ValueError('report has neither ExecutablePath nor Package attribute')

    if not uid:
        uid = os.getuid()

    return os.path.join(report_dir, '%s.%s.crash' % (subject, str(uid)))

def check_files_md5(sumfile):
    '''Check file integrity against md5 sum file.

    sumfile must be md5sum(1) format (relative to /).

    Return a list of files that don't match.
    '''
    assert os.path.exists(sumfile)
    m = subprocess.Popen(['/usr/bin/md5sum', '-c', sumfile],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True,
        cwd='/', env={})
    out = m.communicate()[0].decode()

    # if md5sum succeeded, don't bother parsing the output
    if m.returncode == 0:
        return []

    mismatches = []
    for l in out.splitlines():
        if l.endswith('FAILED'):
            mismatches.append(l.rsplit(':', 1)[0])

    return mismatches


# end
