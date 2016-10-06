
# Convert C structs and 010 Templates to data models
# Copyright (c) 2007-2008 Michael Eddington

use strict;

# #########################################################################################
# #   S t r u c t  T o  P e a c h
# #########################################################################################

## Contains configuration info for Morf application.
package StructToPeach;

sub new
{
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $self  = {};
	bless ($self, $class);
	
	my %knownTypesLittle = (
		"BOOL",			'<Number name="%NAME%" size="8" endian="little" signed="false" />',
		"BYTE",			'<Number name="%NAME%" size="8" endian="little" signed="false" />',
		"byte",			'<Number name="%NAME%" size="8" endian="little" signed="false" />',
		"uchar",		'<Number name="%NAME%" size="8" endian="little" signed="false" />',
		"INT8",			'<Number name="%NAME%" size="8" endian="little" signed="true" />',
		"UINT8",		'<Number name="%NAME%" size="8" endian="little" signed="false" />',
		"INT16",		'<Number name="%NAME%" size="16" endian="little" signed="true" />',
		"UINT16",		'<Number name="%NAME%" size="16" endian="little" signed="false" />',
		"int",			'<Number name="%NAME%" size="32" endian="little" signed="true" />',
		"long",			'<Number name="%NAME%" size="32" endian="little" signed="true" />',
		"INT32",		'<Number name="%NAME%" size="32" endian="little" signed="true" />',
		"unsigned int",	'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"unsigned long",'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"UINT32",		'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"INT64",		'<Number name="%NAME%" size="64" endian="little" signed="true" />',
		"UINT64",		'<Number name="%NAME%" size="64" endian="little" signed="false" />',
		"int32",		'<Number name="%NAME%" size="32" endian="little" signed="true" />',
		"uint32",		'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"WORD",			'<Number name="%NAME%" size="16" endian="little" signed="false" />',
		"int16",		'<Number name="%NAME%" size="16" endian="little" signed="true" />',
		"uint16",		'<Number name="%NAME%" size="16" endian="little" signed="false" />',
		"ushort",		'<Number name="%NAME%" size="16" endian="little" signed="false" />',
		"int64",		'<Number name="%NAME%" size="64" endian="little" signed="true" />',
		"uint64",		'<Number name="%NAME%" size="64" endian="little" signed="false" />',
		"INT",			'<Number name="%NAME%" size="32" endian="little" signed="true" />',
		"UINT",			'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"LONG",			'<Number name="%NAME%" size="32" endian="little" signed="true" />',
		"ULONG",		'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"LONGLONG",		'<Number name="%NAME%" size="64" endian="little" signed="true" />',
		"LARGE_INTEGER",'<Number name="%NAME%" size="64" endian="little" signed="true" />',
		"BOOLEAN",		'<Number name="%NAME%" size="64" endian="little" signed="true" />',
		"DWORD",		'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"DWORDLONG",	'<Number name="%NAME%" size="64" endian="little" signed="false" />',
		"SSIZE_T",		'<Number name="%NAME%" size="32" endian="little" signed="false" />',
		"SHORT",		'<Number name="%NAME%" size="16" endian="little" signed="true" />',
		"USHORT",		'<Number name="%NAME%" size="16" endian="little" signed="false" />',
		"WCHAR",		'<String name="%NAME%" type="wchar" value="A" />',
		"CHAR",			'<String name="%NAME%" value="A" />',
		"char",			'<String name="%NAME%" value="A" />',
		"unsigned char",'<String name="%NAME%" value="A" />',
		"UCHAR",		'<Blob name="%NAME%" length="1" value="A" />',
		"PCSTR",		'<String name="%NAME%" value="A" />',
		"LPCSTR",		'<String name="%NAME%" value="A" />',
		"LPCTSTR",		'<String name="%NAME%" value="A" />',
		);
	$self->KnownTypesLittle(\%knownTypesLittle);
	
	my %knownTypesBig= (
		"BOOL",			'<Number name="%NAME%" size="8" endian="big" signed="false" />',
		"byte",			'<Number name="%NAME%" size="8" endian="big" signed="false" />',
		"BYTE",			'<Number name="%NAME%" size="8" endian="big" signed="false" />',
		"uchar",		'<Number name="%NAME%" size="8" endian="big" signed="false" />',
		"INT8",			'<Number name="%NAME%" size="8" endian="big" signed="true" />',
		"UINT8",		'<Number name="%NAME%" size="8" endian="big" signed="false" />',
		"INT16",		'<Number name="%NAME%" size="16" endian="big" signed="true" />',
		"UINT16",		'<Number name="%NAME%" size="16" endian="big" signed="false" />',
		"int",			'<Number name="%NAME%" size="32" endian="big" signed="true" />',
		"long",			'<Number name="%NAME%" size="32" endian="big" signed="true" />',
		"INT32",		'<Number name="%NAME%" size="32" endian="big" signed="true" />',
		"unsigned int",	'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"unsigned long",'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"UINT32",		'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"INT64",		'<Number name="%NAME%" size="64" endian="big" signed="true" />',
		"UINT64",		'<Number name="%NAME%" size="64" endian="big" signed="false" />',
		"int16",		'<Number name="%NAME%" size="16" endian="big" signed="true" />',
		"uint16",		'<Number name="%NAME%" size="16" endian="big" signed="false" />',
		"ushort",		'<Number name="%NAME%" size="16" endian="big" signed="false" />',
		"WORD",			'<Number name="%NAME%" size="16" endian="big" signed="false" />',
		"int32",		'<Number name="%NAME%" size="32" endian="big" signed="true" />',
		"uint32",		'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"int64",		'<Number name="%NAME%" size="64" endian="big" signed="true" />',
		"uint64",		'<Number name="%NAME%" size="64" endian="big" signed="false" />',
		"INT",			'<Number name="%NAME%" size="32" endian="big" signed="true" />',
		"UINT",			'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"LONG",			'<Number name="%NAME%" size="32" endian="big" signed="true" />',
		"ULONG",		'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"LONGLONG",		'<Number name="%NAME%" size="64" endian="big" signed="true" />',
		"LARGE_INTEGER",'<Number name="%NAME%" size="64" endian="big" signed="true" />',
		"BOOLEAN",		'<Number name="%NAME%" size="64" endian="big" signed="true" />',
		"DWORD",		'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"DWORDLONG",	'<Number name="%NAME%" size="64" endian="big" signed="false" />',
		"SSIZE_T",		'<Number name="%NAME%" size="32" endian="big" signed="false" />',
		"SHORT",		'<Number name="%NAME%" size="16" endian="big" signed="true" />',
		"USHORT",		'<Number name="%NAME%" size="16" endian="big" signed="false" />',
		"WCHAR",		'<String name="%NAME%" type="wchar" value="A" />',
		"CHAR",			'<String name="%NAME%" value="A" />',
		"char",			'<String name="%NAME%" value="A" />',
		"unsigned char",'<String name="%NAME%" value="A" />',
		"UCHAR",		'<Blob name="%NAME%" length="1" />',
		"PCSTR",		'<String name="%NAME%" value="A" />',
		"LPCSTR",		'<String name="%NAME%" value="A" />',
		"LPCTSTR",		'<String name="%NAME%" value="A" />',
		);
	$self->KnownTypesBig(\%knownTypesBig);
	
	my %knownArrayTypes = (
		"BYTE",			'<Blob name="%NAME%" length="ARRAYSIZE" value="A" />',
		"byte",			'<Blob name="%NAME%" length="ARRAYSIZE" value="A" />',
		"uchar",		'<Blob name="%NAME%" length="ARRAYSIZE" value="A" />',
		"char",			'<String name="%NAME%" length="ARRAYSIZE" value="A" />',
		"unsigned char",'<String name="%NAME%" length="ARRAYSIZE" value="A" />',
		"CHAR",			'<String name="%NAME%" length="ARRAYSIZE" value="A" />',
		"UCHAR",		'<String name="%NAME%" length="ARRAYSIZE" value="A" />',
		"WCHAR",		'<String name="%NAME%" type="wchar" length="ARRAYSIZE" value="A" />',
		"TCHAR",		'<String name="%NAME%" type="wchar" length="ARRAYSIZE" value="A" />',
		"wchar",		'<String name="%NAME%" type="wchar" length="ARRAYSIZE" value="A" />',
		);
	$self->KnownArrayTypes(\%knownArrayTypes);
	
	my $endian = shift;
	
	if($endian eq 'little')
	{
		$self->KnownTypes($self->KnownTypesLittle);
	}
	else
	{
		$self->KnownTypes($self->KnownTypesBig);
	}
	
	$self->Block("Block([\nSTUFF\n\t])\n");

	{
	my %hash = ();
	$self->KnownStructs(\%hash);
	}
	{
	my %hash = ();
	$self->KnownTypedefs(\%hash);
	}
	{
	my %hash = ();
	$self->KnownDefines(\%hash);
	}
	
	$self->Typedef(0);
	
	return $self;
}

sub Endian
{
	my $self = shift;
	$self->{__PACKAGE__ .'Endian'} = shift if @_;
	return $self->{__PACKAGE__ .'Endian'};
}

sub KnownTypesLittle
{
	my $self = shift;
	$self->{__PACKAGE__ .'KnownTypesLittle'} = shift if @_;
	return $self->{__PACKAGE__ .'KnownTypesLittle'};
}

sub KnownTypesBig
{
	my $self = shift;
	$self->{__PACKAGE__ .'KnownTypesBig'} = shift if @_;
	return $self->{__PACKAGE__ .'KnownTypesBig'};
}

sub KnownTypes
{
	my $self = shift;
	$self->{__PACKAGE__ .'KnownTypes'} = shift if @_;
	return $self->{__PACKAGE__ .'KnownTypes'};
}

sub KnownArrayTypes
{
	my $self = shift;
	$self->{__PACKAGE__ .'KnownArrayTypes'} = shift if @_;
	return $self->{__PACKAGE__ .'KnownArrayTypes'};
}

sub KnownStructs
{
	my $self = shift;
	$self->{__PACKAGE__ .'KnownStructs'} = shift if @_;
	return $self->{__PACKAGE__ .'KnownStructs'};
}
sub KnownTypedefs
{
	my $self = shift;
	$self->{__PACKAGE__ .'KnownTypedefs'} = shift if @_;
	return $self->{__PACKAGE__ .'KnownTypedefs'};
}
sub KnownDefines
{
	my $self = shift;
	$self->{__PACKAGE__ .'KnownDefines'} = shift if @_;
	return $self->{__PACKAGE__ .'KnownDefines'};
}
sub StructName
{
	my $self = shift;
	$self->{__PACKAGE__ .'StructName'} = shift if @_;
	return $self->{__PACKAGE__ .'StructName'};
}
sub Typedef
{
	my $self = shift;
	$self->{__PACKAGE__ .'Typedef'} = shift if @_;
	return $self->{__PACKAGE__ .'Typedef'};
}

sub Block
{
	my $self = shift;
	$self->{__PACKAGE__ .'Block'} = shift if @_;
	return $self->{__PACKAGE__ .'Block'};
}

sub Data
{
	my $self = shift;
	$self->{__PACKAGE__ .'Data'} = shift if @_;
	return $self->{__PACKAGE__ .'Data'};
}

sub Result
{
	my $self = shift;
	$self->{__PACKAGE__ .'Result'} = shift if @_;
	return $self->{__PACKAGE__ .'Result'};
}

# ############################################################################

sub ParseData
{
	my $self = shift;
	my $data = shift;
	
	$self->Result(<<EOT);
<?xml version="1.0" encoding="utf-8"?>
<Peach version="1.0" author="struct2peach" description="Autogenerated from header files">

	<!--

	A struct2peach.pl Generated DataModels.

	-->
	
	<!-- Import defaults for Peach instance -->	
	<Include ns="default" src="file:defaults.xml" />
	
	<!-- Import some common complex data types into the
	     "pt" namespace -->
	<Include ns="pt" src="file:PeachTypes.xml" />

EOT
	my @dataArray = split(/\n/, $data);
	$self->Data(\@dataArray);
	my $unknownCnt = 0;
	
	while(defined($_ = shift @{$self->Data}))
	{
		if(/typedef\s+struct/)
		{
			$self->Typedef(1);
		}
		
		if(/(?:typedef\s+)struct\b(?:\s+(\w*)|)(?:\s|{|$)/)
		{
			my $structName = $1;
			if(length($structName) < 2)
			{
				$structName= "UnkownStruct" . $unknownCnt;
				$unknownCnt++;
			}
			
			$self->StructName("$structName");
			my %hash = {};
			${$self->KnownStructs}{"" . $self->StructName} = \%hash;
			
			#print "Found struct: $structName\n";
			$_ = $self->ParseStruct("" . $self->StructName);
			
			if($self->Typedef == 1)
			{
				if(/}\s+([^\s;,]+)/)
				{
					#print "Found typedef [$1]\n";
					#${$self->KnownTypedefs}{"$1"} = $self->StructName;
					my $oldStructName = $structName;
					$structName = $1;
					
					my $obj = ${$self->KnownStructs}{"$oldStructName"};
					delete(${$self->KnownStructs}{"$oldStructName"});
					
					$self->StructName($structName);
					${$self->KnownStructs}{"$structName"} = $obj;
					
				}
			}
		}
		
		if(/\s*#define\s+([^\s]+)\s+([^\/;]+)/)
		{
			${$self->KnownDefines}{"$1"} = "$2";
		}
	}
	
	$self->GeneratePeach();
	$self->Result( $self->Result . "</Peach>\n");
}

sub ParseStruct
{
	my $self = shift @_;
	my $structName = shift @_;
	
	${$self->KnownStructs}{"$structName"} = [];
	
	while(defined($_ = shift @{$self->Data}))
	{
		if(/}/)
		{
			# the end!
			return $_;
		}
		elsif(/$\s*(\w[^\s*]+(?:\s{0,1}\w[^\s*]+|))\s+([^\s*\[\]]+)\s*;/)
		{
			#print "Found variable: $2 of type $1\n";
			push @{${$self->KnownStructs}{"$structName"}}, ["$2", "$1", 1, $_];
		}
		elsif(/$\s*(\w[^\s*]+(?:\s{0,1}\w[^\s*]+|))\s+([^\s]+)\[([^\]]+)\]\s*;/)
		{
			#print "Found variable: $2 array of type $1 size of $3\n";
			push @{${$self->KnownStructs}{"$structName"}}, ["$2", "$1", "$3", $_];
		}
		elsif(/$\s*(\w[^\s*]+(?:\s{0,1}\w[^\s*]+|))\s+([^\s]+)\[(\d+)\]\s*;/)
		{
			#print "Found variable: $2 array of type $1 size of $3\n";
			push @{${$self->KnownStructs}{"$structName"}}, ["$2", "$1", "$3", $_];
		}
		elsif(/$\s*(\w[^\s*]+(?:\s{0,1}\w[^\s*]+|))(?:\*\s+|\s+\*)([^\s*\[\]]+)\s*;/)
		{
			#print "Found variable: $2 array of type $1 size of unkown\n";
			push @{${$self->KnownStructs}{"$structName"}}, ["$2", "$1", "POINTER", $_];
		}
		elsif(/$\s*(?:union|struct)(?:\s|{)/)
		{
			my $varname = $self->EatUnion();
			#print "Found variable: $2 array of type $1 size of $3\n";
			push @{${$self->KnownStructs}{"$structName"}}, ["$varname", "union", 1, $_];
		}
	}
}

sub EatUnion
{
	my $self = shift @_;
		
	my $varname = undef;
	
	shift @{$self->Data};
	while(defined($_ = shift @{$self->Data}))
	{
		if(/$\s*(?:union|struct)(?:\s|{)/)
		{
			$self->EatUnion();
		}
		elsif(/}\s*([^;\s,]*)/)
		{
			$varname = $1;
			last;
		}
		elsif(/}/)
		{
			last;
		}
	}
	
	return $varname;
}

# #######################################################################

sub GeneratePeach
{
	my $self = shift @_;
		
	#$self->FixDefines();
	
	$self->Result( $self->Result . "\t<!-- # STRUCTURES ###################################################### -->\n\n");

	foreach my $k (keys(%{$self->KnownStructs}))
	{
		$self->InsertStruct($k, 1);
		$self->Result($self->Result . "\n\n\n");
	}
	
	$self->Result( $self->Result . "\n\t<!-- # ################################################################# -->\n");
}

sub FixDefines
{
	my $self = shift @_;
	
	foreach my $k (keys %{$self->KnownDefines})
	{
		my $expr = ${$self->KnownDefines}{"$k"};
		${$self->KnownDefines}{"$k"} = $self->MakeSubs($expr);
	}
}

sub MakeSubs
{
	my $self = shift @_;
	my $expr = shift @_;
	
	my $madesub = 1;
	my $val;
	
	while($madesub == 1)
	{
		$madesub = 0;
		
		foreach my $k (keys %{$self->KnownDefines})
		{
			#if($expr =~ /\b$k\b/)
            # \Q quote (disable) pattern metacharacters till \E allows for metacharacters like ( or ) in $k
            if($expr =~ /\Q\b$k\b\E/)
			{
				$madesub = 1;
				$val = ${$self->KnownDefines}{"$k"};
				#$expr =~ s/\b$k\b/$val/;
                $expr =~ s/\Q\b$k\b\E/$val/;
			}
		}
	}
	
	return $expr;
}

sub InsertStruct
{
	my $self = shift;
		
	my $structName = shift;
	my $tabLevel = shift;
	
	my $tabs = "\t" x $tabLevel;
	
	if($tabLevel == 1)
	{
		$self->Result( $self->Result .  $tabs . "<DataModel name=\"$structName\">\n");
	}
	else
	{
		$self->Result( $self->Result .  $tabs . "<Block name=\"$structName\">\n");
	}
	
	my $struct = ${$self->KnownStructs}{"$structName"};
	foreach my $var (@$struct)
	{
		my $varType = $$var[1];
		#print "\t[$varType]\n";
		
		$$var[3] =~ s/^\s*(.*)\s*\n/$1/;
		$$var[3] =~ s/\s+/ /g;
		
		if($$var[2] != 1)
		{
			$self->Result( $self->Result . $tabs . "\t<!-- # " . $$var[0] . " (" . $$var[3] . ") [" . $$var[2] . "] -->\n");
		}
		else
		{
			$self->Result( $self->Result .  $tabs . "\t<!-- # " . $$var[0] . " (" . $$var[3] . ") -->\n");
		}
		
		my $name = $$var[0];
		
		if($$var[2] != 1 and defined($self->KnownArrayTypes->{$varType}))
		{
			my $str = "";
			my $size = $$var[2];
			$size = $self->MakeSubs($size);
			if($size =~ /^[^a-zA-Z_]*$/)
			{
				$size = eval($size);
			}
			
			$str = $tabs . "\t" . $self->KnownArrayTypes->{$varType} . "\n";
			$str =~ s/ARRAYSIZE/$size/g;
			$str =~ s/%NAME%/$name/;
			$self->Result( $self->Result .  $str);
		}
		else
		{
			for(my $cnt = 0; $cnt < $$var[2]; $cnt++)
			{
				if( defined($self->KnownTypes->{$varType}) )
				{
					$self->Result( $self->Result . $tabs . "\t" . ${$self->KnownTypes}{$varType} . "\n");
					my $str = $self->Result;
					$str =~ s/%NAME%/$name/;
					$self->Result($str);
				}
				elsif( defined($self->KnownTypedefs->{$varType}) )
				{
					$self->InsertStruct(${$self->KnownTypedefs}{$varType}, $tabLevel + 1);
				}
				else
				{
					$self->Result( $self->Result . $tabs . "\t<!-- # Unknown type: $varType -->\n");
				}
			}
		}
		
		$self->Result( $self->Result . "\n");
	}
	
	if($tabLevel > 1)
	{
		$self->Result( $self->Result . $tabs . "</Block>\n");
	}
	else
	{
		$self->Result( $self->Result . $tabs . "</DataModel>\n");
	}
}

# #########################################################################################

package main;

print STDERR "] c-struct2peach v0.3\n";
print STDERR "] Copyright (c) 2007-2008 Michael Eddington\n";
print STDERR "] mike\@phed.org\n\n";

my $endian = shift or die "Syntax: struct2peach.pl [little|big] < filename.h > gens.xml\n\n  Please specify endianness\n";

print STDERR "You have selected little endian.\n" if $endian eq 'little';

my $data  = "";

while(<>)
{
	$data .= $_;
}

my $parse = new StructToPeach($endian);
$parse->ParseData($data);

print $parse->Result;

# end
