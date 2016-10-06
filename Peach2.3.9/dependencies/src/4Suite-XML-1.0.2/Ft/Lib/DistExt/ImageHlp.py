import struct

__all__ = ['DataType', 'Array', 'Struct', 'Byte', 'Word', 'Dword', 'ArrayOf',
           'RT_RCDATA', 'RT_VERSION', 'UpdateResource', 'SetSubsystem',
           ]

try:
    # Python 2.3+
    issubclass(type, ())
except TypeError:
    # Python 2.2
    import __builtin__
    def issubclass(subclass, class_or_tuple):
        if isinstance(class_or_tuple, tuple):
            for class_ in class_or_tuple:
                if issubclass(subclass, class_):
                    return True
            return False
        return __builtin__.issubclass(subclass, class_or_tuple)

class DataType(type):
    def __init__(cls, name, bases, namespace):
        if Struct in bases:
            assert '__fields__' in namespace
            slots = []
            format = '<'
            for datatype, field in namespace['__fields__']:
                slots.append(field)
                if issubclass(datatype, (Struct, Array)):
                    format += '%ds' % datatype.__size__
                else:
                    format += datatype.__format__[1:]
            cls.__slots__ = tuple(slots)
            cls.__format__ = format
        else:
            assert '__format__' in namespace
            cls.__slots__ = ()
        # Update (cache) the record size
        cls.__size__ = struct.calcsize(cls.__format__)
        return super(DataType, cls).__init__(name, bases, namespace)

# allow the DataType metaclass to do its thing on the 'Struct' class
Struct = None
class Struct(object):
    __metaclass__ = DataType
    __format__ = ''

    def __init__(self, bytes=None):
        if bytes is None:
            bytes = '\0' * self.__size__
        values = struct.unpack(self.__format__, bytes)
        for (datatype, name), value in zip(self.__fields__, values):
            setattr(self, name, datatype(value))
        return

    def __repr__(self):
        values = []
        for format, name in self.__fields__:
            value = getattr(self, name)
            if issubclass(format, Struct):
                members = repr(value).split('\n')
                members.insert(0, '<%s>' % format.__name__)
                value = '\n    '.join(members)
            values.append('%s: %s' % (name, value))
        return '\n'.join(values)

    #@classmethod
    def load(cls, stream):
        return cls(stream.read(cls.__size__))
    load = classmethod(load)

    def pack(self):
        values = []
        for datatype, field in self.__fields__:
            value = getattr(self, field)
            if issubclass(datatype, (Struct, Array)):
                value = value.pack()
            values.append(value)
        return struct.pack(self.__format__, *values)

class Array(list):
    def __init__(self, bytes=None):
        if bytes is None:
            bytes = '\0' * self.__size__
        values = struct.unpack(self.__format__, bytes)
        if self.__itemtype__:
            values = map(self.__itemtype__, values)
        list.__init__(self, values)

    def pack(self):
        values = self
        if self.__itemtype__ is not None:
            values = [ item.pack() for item in values ]
        return struct.pack(self.__format__, *values)

class Byte(int):
    __metaclass__ = DataType
    __format__ = '<B'

class Word(int):
    __metaclass__ = DataType
    __format__ = '<H'

class Dword(long):
    __metaclass__ = DataType
    __format__ = '<L'

def ArrayOf(datatype, size):
    name = '%s[%d]' % (datatype.__name__, size)
    if issubclass(datatype, (Struct, Array)):
        format = '%ds' % datatype.__size__
        itemtype = datatype
    else:
        format = datatype.__format__[1:]
        itemtype = None
    namespace = {
        '__metaclass__' : DataType,
        '__format__' : '<' + (format * size),
        '__itemtype__' : itemtype,
        }
    return DataType(name, (Array,), namespace)

IMAGE_NT_OPTIONAL_HDR32_MAGIC = 0x010B
IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16
IMAGE_SIZEOF_SHORT_NAME = 8
IMAGE_DIRECTORY_ENTRY_RESOURCE = 2

IMAGE_SUBSYSTEM_WINDOWS_GUI = 2
IMAGE_SUBSYSTEM_WINDOWS_CUI = 3

# Predefined Resource Types
RT_RCDATA = 10
RT_VERSION = 16

class ImageDosHeader(Struct):
    __fields__ = [
        (Word, 'e_magic'),
        (Word, 'e_cblp'),
        (Word, 'e_cp'),
        (Word, 'e_crlc'),
        (Word, 'e_cparhdr'),
        (Word, 'e_minalloc'),
        (Word, 'e_maxalloc'),
        (Word, 'e_ss'),
        (Word, 'e_sp'),
        (Word, 'e_csnum'),
        (Word, 'e_ip'),
        (Word, 'e_cs'),
        (Word, 'e_lfarlc'),
        (Word, 'e_ovno'),
        (ArrayOf(Word, 4), 'e_res'),
        (Word, 'e_oemid'),
        (Word, 'e_oeminfo'),
        (ArrayOf(Word, 10), 'e_res2'),
        (Dword, 'e_lfanew'),
        ]

class ImageFileHeader(Struct):
    __fields__ = [
        (Word, 'Machine'),
        (Word, 'NumberOfSections'),
        (Dword, 'TimeDateStamp'),
        (Dword, 'PointerToSymbolTable'),
        (Dword, 'NumberOfSymbols'),
        (Word, 'SizeOfOptionalHeader'),
        (Word, 'Characteristics'),
        ]

class ImageDataDirectory(Struct):
    __fields__ = [
        (Dword, 'VirtualAddress'),
        (Dword, 'Size'),
        ]

class ImageOptionalHeader(Struct):
    __fields__ = [
        (Word, 'Magic'),
        (Byte, 'MajorLinkerVersion'),
        (Byte, 'MinorLinkerVersion'),
        (Dword, 'SizeOfCode'),
        (Dword, 'SizeOfInitializedData'),
        (Dword, 'SizeOfUninitializedData'),
        (Dword, 'AddressOfEntryPoint'),
        (Dword, 'BaseOfCode'),
        (Dword, 'BaseOfData'),
        (Dword, 'ImageBase'),
        (Dword, 'SectionAlignment'),
        (Dword, 'FileAlignment'),
        (Word, 'MajorOperatingSystemVersion'),
        (Word, 'MinorOperatingSystemVersion'),
        (Word, 'MajorImageVersion'),
        (Word, 'MinorImageVersion'),
        (Word, 'MajorSubsystemVersion'),
        (Word, 'MinorSubsystemVersion'),
        (Dword, 'Win32VersionValue'),
        (Dword, 'SizeOfImage'),
        (Dword, 'SizeOfHeaders'),
        (Dword, 'CheckSum'),
        (Word, 'Subsystem'),
        (Word, 'DllCharacteristics'),
        (Dword, 'SizeOfStackReserve'),
        (Dword, 'SizeOfStackCommit'),
        (Dword, 'SizeOfHeapReserve'),
        (Dword, 'SizeOfHepCommit'),
        (Dword, 'LoaderFlags'),
        (Dword, 'NumberOfRvaAndSizes'),
        (ArrayOf(ImageDataDirectory, IMAGE_NUMBEROF_DIRECTORY_ENTRIES),
         'DataDirectory'),
        ]

class ImageNTHeaders(Struct):
    __fields__ = [
        (Dword, 'Signature'),
        (ImageFileHeader, 'FileHeader'),
        (ImageOptionalHeader, 'OptionalHeader'),
        ]

class ImageSectionHeader(Struct):
    __fields__ = [
        (ArrayOf(Byte, IMAGE_SIZEOF_SHORT_NAME), 'Name'),
        (Dword, 'Misc'),
        (Dword, 'VirtualAddress'),
        (Dword, 'SizeOfRawData'),
        (Dword, 'PointerToRawData'),
        (Dword, 'PointerToRelocations'),
        (Dword, 'PointerToLinenumbers'),
        (Word, 'NumberOfRelocations'),
        (Word, 'NumberOfLinenumbers'),
        (Dword, 'Characteristics'),
        ]

class ImageResourceDirectory(Struct):
    __fields__ = [
        (Dword, 'Characteristics'),
        (Dword, 'TimeDateStamp'),
        (Word, 'MajorVersion'),
        (Word, 'MinorVersion'),
        (Word, 'NumberOfNamedEntries'),
        (Word, 'NumberOfIdEntries'),
        ]

class ImageResourceDirectoryEntry(Struct):
    __fields__ = [
        (Dword, 'Id'),
        (Dword, 'Offset'),
        ]

class ImageResourceDataEntry(Struct):
    __fields__ = [
        (Dword, 'OffsetToData'),
        (Dword, 'Size'),
        (Dword, 'CodePage'),
        (Dword, 'Reserved'),
        ]

def FindImageHeaders(image):
    # Read DOS header
    image.seek(0)
    dos_header = ImageDosHeader.load(image)
    if dos_header.e_magic != 0x5A4D: # "MZ"
        raise ValueError("not an EXE file")
    if dos_header.e_lfanew == 0:
        raise ValueError("not a PE file")
    # Read PE header and optional header
    image.seek(dos_header.e_lfanew)
    nt_headers = ImageNTHeaders.load(image)
    if nt_headers.Signature != 0x00004550: # "PE\0\0"
        raise ValueError("invalid PE signature")
    file_header = nt_headers.FileHeader
    if file_header.SizeOfOptionalHeader != ImageOptionalHeader.__size__:
        raise ValueError("invalid header size")
    opt_header = nt_headers.OptionalHeader
    if opt_header.Magic != IMAGE_NT_OPTIONAL_HDR32_MAGIC:
        raise ValueError("invaid header magic");
    return dos_header, nt_headers

def FindResourceSection(image):
    # Scan section headers for resource section
    dos_header, nt_headers = FindImageHeaders(image)
    data_directory = nt_headers.OptionalHeader.DataDirectory
    directory_entry = data_directory[IMAGE_DIRECTORY_ENTRY_RESOURCE]
    if directory_entry.VirtualAddress == 0 or directory_entry.Size == 0:
        raise ValueError("no resources")
    address = directory_entry.VirtualAddress
    for i in xrange(nt_headers.FileHeader.NumberOfSections):
        section = ImageSectionHeader.load(image)
        if address == section.VirtualAddress and section.SizeOfRawData != 0:
            return section
    raise ValueError("no resources")

def FindResourceOffset(image, anyId, resourceId, findSubdir):
    directory = ImageResourceDirectory.load(image)
    # Skip over named entries
    for i in xrange(directory.NumberOfNamedEntries):
        entry = ImageResourceDirectoryEntry.load(image)
    # Now process ID entries
    for i in xrange(directory.NumberOfIdEntries):
        entry = ImageResourceDirectoryEntry.load(image)
        if ((anyId or entry.Id == resourceId) and
            ((entry.Offset & 0x80000000L != 0) == findSubdir)):
            return (entry.Offset & 0x7FFFFFFFL)
    raise ValueError("resource not found")

def SeekToResource(image, resourceType, resourceId):
    """Sets stream `f` to the location of the resource source"""
    section = FindResourceSection(image)

    # Scan the resource directory
    image.seek(section.PointerToRawData)
    offset = FindResourceOffset(image, False, resourceType, True)
    image.seek(section.PointerToRawData + offset)
    offset = FindResourceOffset(image, False, resourceId, True)
    image.seek(section.PointerToRawData + offset)
    offset = FindResourceOffset(image, True, 0, False)
    image.seek(section.PointerToRawData + offset)
    entry = ImageResourceDataEntry.load(image)

    # Sanity check: data_entry.OffsetToData is an RVA.  It's
    # technically possible for the RVA to point to a different section,
    # but we don't support that.
    offset = entry.OffsetToData - section.VirtualAddress
    if offset < 0 or section.SizeOfRawData < (offset + entry.Size):
        raise ValueError("invalid resource")

    # Seek to the resource
    image.seek(section.PointerToRawData + offset)
    return

def UpdateResource(image, resourceType, resourceId, resourceData):
    """
    Replaces the resource in the executable file.
    """
    SeekToResource(image, resourceType, resourceId)
    image.write(resourceData.pack())
    return

def SetSubsystem(image, subsystem):
    """
    Sets the Windows subsystem required to run the executable file.
    """
    if subsystem not in (IMAGE_SUBSYSTEM_WINDOWS_GUI,
                         IMAGE_SUBSYSTEM_WINDOWS_CUI):
        raise ValueError("invalid executable subsystem")

    dos_header, nt_headers = FindImageHeaders(image)
    nt_headers.OptionalHeader.Subsystem = subsystem
    image.seek(dos_header.e_lfanew)
    image.write(nt_headers.pack())
    return
