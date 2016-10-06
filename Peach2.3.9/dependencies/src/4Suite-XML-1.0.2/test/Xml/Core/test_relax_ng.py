import os
from cStringIO import StringIO
from xml.dom import Node

from Ft.Lib.Uri import OsPathToUri, Absolutize
from Ft.Lib.Uuid import GenerateUuid, UuidAsString
from Ft.Xml.Domlette import NonvalidatingReader, implementation, Print
from Ft.Xml.Xvif import RelaxNgValidator, RngInvalid
from Ft.Xml.ThirdParty.Xvif.rng import RngSchemaInvalidException

SPECTEST_ENV_VAR = 'RELAXNG_TEST_SUITE'
SPECTEST_URI = None
if SPECTEST_ENV_VAR in os.environ:
    spectest_path = os.environ[SPECTEST_ENV_VAR]
    SPECTEST_URI = OsPathToUri(spectest_path, attemptAbsolute=True)


def get_description(node):
    sec = node.xpath('section/text()')
    desc = node.xpath('documentation/text()')
    if sec:
        description = 'Section %s' % sec[0].data.encode('us-ascii', 'replace')
    else:
        description = ''
    if desc:
        if sec:
            description += ' - '
        description += desc[0].data.encode('us-ascii', 'replace')
    return description


def generate_uri(purpose='schema'):
    global SPECTEST_URI
    uuid = UuidAsString(GenerateUuid())
    return '%s#%s_%s' % (SPECTEST_URI, purpose, uuid)


def doc_from_fragment(node):
    doc = implementation.createRootNode(generate_uri())
    new_node = doc.importNode(node, True)
    doc.appendChild(new_node)
    return doc


def serialize_doc(node):
    buf = StringIO()
    Print(node, buf)
    return buf.getvalue()


def process_test(test, tester):
    description = get_description(test)
    tester.startGroup(description)
    incorrect_schema = test.xpath('incorrect/*')
    correct_schema = test.xpath('correct/*')
    valid_xml = test.xpath('valid/*')
    invalid_xml = test.xpath('invalid/*')
    if incorrect_schema:
        tester.startTest('Parse invalid schema')
        schema_doc = doc_from_fragment(incorrect_schema[0])
        try:
            validator = RelaxNgValidator(schema_doc)
        except RngSchemaInvalidException:
            pass
        else:
            errmsg = 'Invalid schema parse fails to raise RngSchemaInvalidException!\n'
            errmsg += 'This is the schema:\n%s' % serialize_doc(schema_doc)
            tester.error(errmsg)
        tester.testDone()
    elif correct_schema:
        schema_doc = doc_from_fragment(correct_schema[0])
        valid_docs = [doc_from_fragment(node) for node in valid_xml]
        invalid_docs = [doc_from_fragment(node) for node in invalid_xml]
        i = 0
        for valid_doc in valid_docs:
            i += 1
            desc = 'valid doc %d of %d' % (i, len(valid_docs))
            tester.startTest(desc)
            try:
                validator = RelaxNgValidator(schema_doc)
            except RngSchemaInvalidException, e:
                tester.warning('Could not complete test; schema was not valid: %s' % e)
                tester.message('This is the schema:\n%s' % serialize_doc(schema_doc))
                tester.message('This is the valid doc:\n%s' % serialize_doc(valid_doc))
                tester.testDone()
                break
            result = validator.validateNode(valid_doc)
            if not result.nullable():
                if hasattr(result, 'msg'):
                    tester.error('Valid doc fails to validate: %r' % result.msg)
                else:
                    tester.error('Valid doc fails to validate (no reason given)')
                    tester.message('Result was %r' % result)
                tester.message('This is the schema:\n%s' % serialize_doc(schema_doc))
                tester.message('This is the valid doc:\n%s' % serialize_doc(valid_doc))
            tester.testDone()
        for invalid_doc in invalid_docs:
            desc = 'invalid doc %d of %d' % (i, len(valid_docs))
            tester.startTest(desc)
            try:
                validator = RelaxNgValidator(schema_doc)
            except RngSchemaInvalidException, e:
                tester.warning('Could not complete test; schema was not valid: %s' % e)
                tester.message('This is the schema:\n%s' % serialize_doc(schema_doc))
                tester.testDone()
                break
            result = validator.validateNode(invalid_doc)
            if result.nullable():
                tester.error('Invalid doc validates as valid!')
                tester.message('This is the schema:\n%s' % serialize_doc(schema_doc))
                tester.message('This is the invalid doc:\n%s' % serialize_doc(invalid_doc))
            tester.testDone()
    else:
        tester.warning('Unknown test case format')
    tester.groupDone()
    return


def process_group(group, tester, tests_by_group):
    description = get_description(group)
    tester.startGroup(description)
    if group in tests_by_group:
        # this is a leaf group; go process its tests
        for test in tests_by_group[group]:
            process_test(test, tester)
    else:
        subgroups = group.xpath('testSuite')
        for subgroup in subgroups:
            process_group(subgroup, tester, tests_by_group)
    tester.groupDone()


def Test(tester):
    tester.startGroup("James Clark's RELAX NG test suites")
    if SPECTEST_URI is None:
        tester.warning('Test cases document not found; skipping tests.'
                       ' To enable the tests, download and unpack'
                       ' http://thaiopensource.com/relaxng/testSuite.zip'
                       ' and set the environment variable %s to be the'
                       ' complete file system path of spectest.xml.' % SPECTEST_ENV_VAR)
        tester.groupDone()
        return
    doc = NonvalidatingReader.parseUri(SPECTEST_URI)
    doc.normalize()
    tests_by_group = {}
    groups = doc.xpath('//testSuite')
    for group in groups:
        tests = group.xpath('testCase')
        if tests:
            tests_by_group[group] = tests

    process_group(groups[0], tester, tests_by_group)
    tester.groupDone()
    return
