# Uche gets nasty with nested copies and other arcana (too bad we had to ixnay the namespace axis hacking)
# jkloth: 2002-01-22
#   Fixed test to expect null-namespace on unprefixed attributes

from Xml.Xslt import test_harness


sheet_1 = """<?xml version='1.0'?>
<xsl:stylesheet version='1.0'
  xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
  xmlns:es='http://www.snowboard-info.com/EndorsementSearch.wsdl'
  xmlns:esxsd='http://schemas.snowboard-info.com/EndorsementSearch.xsd'
  xmlns:soap='http://schemas.xmlsoap.org/wsdl/soap/'
  xmlns:wsdl='http://schemas.xmlsoap.org/wsdl/'
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
>

  <xsl:output method='xml' indent='yes'/>

  <!-- template 1 -->
  <xsl:template match='wsdl:definitions'>
    <xsl:copy>
      <xsl:apply-templates select='@*'/>
      <xsl:apply-templates select='*'/>
      <rdf:RDF>
        <xsl:apply-templates select='*' mode='convert-to-rdf'/>
      </rdf:RDF>
    </xsl:copy>
  </xsl:template>

  <!-- template 2 -->
  <xsl:template match='wsdl:message|wsdl:portType|wsdl:binding|wsdl:service|wsdl:operation|wsdl:port' mode='convert-to-rdf'>
    <xsl:copy>
      <xsl:attribute name='rdf:ID' namespace='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
        <xsl:value-of select='@name'/>
      </xsl:attribute>
      <xsl:apply-templates select='@*' mode='convert-to-rdf'/>
      <xsl:apply-templates select='*'/>
      <xsl:apply-templates select='*' mode='convert-to-rdf'/>
    </xsl:copy>
  </xsl:template>

  <!-- template 3 -->
  <xsl:template match='wsdl:part' mode='convert-to-rdf'>
    <xsl:copy>
      <xsl:apply-templates select='@*' mode='convert-to-rdf'/>
      <xsl:apply-templates select='*'/>
      <xsl:apply-templates select='*' mode='convert-to-rdf'/>
    </xsl:copy>
  </xsl:template>

  <!-- template 4 -->
  <xsl:template match='wsdl:message|wsdl:portType|wsdl:binding|wsdl:service|wsdl:operation|wsdl:port|wsdl:part'/>

  <!-- template 5 -->
  <xsl:template match='@*' mode='convert-to-rdf'>
    <xsl:attribute name="{concat('wsdl', ':', name())}"
                   namespace='{namespace-uri()}'>
      <xsl:value-of select='.'/>
    </xsl:attribute>
  </xsl:template>

  <!-- template 6 -->
  <xsl:template match='*' mode='convert-to-rdf'/>

  <!-- template 7 -->
  <xsl:template match='*|@*'>
    <xsl:copy>
      <xsl:apply-templates select='@*|node()'/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>"""


source_1 = """<?xml version="1.0"?>
<definitions name="EndorsementSearch"
  targetNamespace="http://namespaces.snowboard-info.com"
  xmlns:es="http://www.snowboard-info.com/EndorsementSearch.wsdl"
  xmlns:esxsd="http://schemas.snowboard-info.com/EndorsementSearch.xsd"
  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
  xmlns="http://schemas.xmlsoap.org/wsdl/"
>
  <types>
    <schema targetNamespace="http://namespaces.snowboard-info.com"
            xmlns="http://www.w3.org/1999/XMLSchema">
      <element name="GetEndorsingBoarder">
        <complexType>
          <sequence>
            <element name="manufacturer" type="string"/>
            <element name="model" type="string"/>
          </sequence>
        </complexType>
      </element>
      <element name="GetEndorsingBoarderResponse">
        <complexType>
          <all>
            <element name="endorsingBoarder" type="string"/>
          </all>
        </complexType>
      </element>
      <element name="GetEndorsingBoarderFault">
        <complexType>
          <all>
            <element name="errorMessage" type="string"/>
          </all>
        </complexType>
      </element>
    </schema>
  </types>

  <message name="GetEndorsingBoarderRequest">
    <part name="body" element="esxsd:GetEndorsingBoarder"/>
  </message>

  <message name="GetEndorsingBoarderResponse">
    <part name="body" element="esxsd:GetEndorsingBoarderResponse"/>
  </message>

  <portType name="GetEndorsingBoarderPortType">
    <operation name="GetEndorsingBoarder">
      <input message="es:GetEndorsingBoarderRequest"/>
      <output message="es:GetEndorsingBoarderResponse"/>
      <fault message="es:GetEndorsingBoarderFault"/>
    </operation>
  </portType>
    
  <binding name="EndorsementSearchSoapBinding"
           type="es:GetEndorsingBoarderPortType">
    <soap:binding style="document"
                  transport="http://schemas.xmlsoap.org/soap/http"/>
    <operation name="GetEndorsingBoarder">
      <soap:operation
        soapAction="http://www.snowboard-info.com/EndorsementSearch"/>
      <input>
        <soap:body use="literal"
          namespace="http://schemas.snowboard-info.com/EndorsementSearch.xsd"/>
      </input>
      <output>
        <soap:body use="literal"
          namespace="http://schemas.snowboard-info.com/EndorsementSearch.xsd"/>
      </output>
      <fault>
        <soap:body use="literal"
          namespace="http://schemas.snowboard-info.com/EndorsementSearch.xsd"/>
      </fault>
    </operation>
  </binding>
    
  <service name="EndorsementSearchService">
    <documentation>snowboarding-info.com Endorsement Service</documentation> 
    <port name="GetEndorsingBoarderPort"
          binding="es:EndorsementSearchSoapBinding">
      <soap:address location="http://www.snowboard-info.com/EndorsementSearch"/>
    </port>
  </service>

</definitions>"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<definitions xmlns:soap='http://schemas.xmlsoap.org/wsdl/soap/' name='EndorsementSearch' targetNamespace='http://namespaces.snowboard-info.com' xmlns='http://schemas.xmlsoap.org/wsdl/' xmlns:esxsd='http://schemas.snowboard-info.com/EndorsementSearch.xsd' xmlns:es='http://www.snowboard-info.com/EndorsementSearch.wsdl'>
  <types>
    <schema xmlns='http://www.w3.org/1999/XMLSchema' targetNamespace='http://namespaces.snowboard-info.com'>
      <element name='GetEndorsingBoarder'>
        <complexType>
          <sequence>
            <element name='manufacturer' type='string'/>
            <element name='model' type='string'/>
          </sequence>
        </complexType>
      </element>
      <element name='GetEndorsingBoarderResponse'>
        <complexType>
          <all>
            <element name='endorsingBoarder' type='string'/>
          </all>
        </complexType>
      </element>
      <element name='GetEndorsingBoarderFault'>
        <complexType>
          <all>
            <element name='errorMessage' type='string'/>
          </all>
        </complexType>
      </element>
    </schema>
  </types>
  <rdf:RDF xmlns:wsdl='http://schemas.xmlsoap.org/wsdl/' xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
    <message rdf:ID='GetEndorsingBoarderRequest' name='GetEndorsingBoarderRequest'>
      <part element='esxsd:GetEndorsingBoarder' name='body'/>
    </message>
    <message rdf:ID='GetEndorsingBoarderResponse' name='GetEndorsingBoarderResponse'>
      <part element='esxsd:GetEndorsingBoarderResponse' name='body'/>
    </message>
    <portType rdf:ID='GetEndorsingBoarderPortType' name='GetEndorsingBoarderPortType'>
      <operation rdf:ID='GetEndorsingBoarder' name='GetEndorsingBoarder'>
        <input message='es:GetEndorsingBoarderRequest'/>
        <output message='es:GetEndorsingBoarderResponse'/>
        <fault message='es:GetEndorsingBoarderFault'/>
      </operation>
    </portType>
    <binding rdf:ID='EndorsementSearchSoapBinding' type='es:GetEndorsingBoarderPortType' name='EndorsementSearchSoapBinding'>
      <soap:binding transport='http://schemas.xmlsoap.org/soap/http' style='document'/>
      <operation rdf:ID='GetEndorsingBoarder' name='GetEndorsingBoarder'>
        <soap:operation soapAction='http://www.snowboard-info.com/EndorsementSearch'/>
        <input>
        <soap:body use='literal' namespace='http://schemas.snowboard-info.com/EndorsementSearch.xsd'/>
      </input>
        <output>
        <soap:body use='literal' namespace='http://schemas.snowboard-info.com/EndorsementSearch.xsd'/>
      </output>
        <fault>
        <soap:body use='literal' namespace='http://schemas.snowboard-info.com/EndorsementSearch.xsd'/>
      </fault>
      </operation>
    </binding>
    <service rdf:ID='EndorsementSearchService' name='EndorsementSearchService'>
      <documentation>snowboarding-info.com Endorsement Service</documentation>
      <port rdf:ID='GetEndorsingBoarderPort' binding='es:EndorsementSearchSoapBinding' name='GetEndorsingBoarderPort'>
        <soap:address location='http://www.snowboard-info.com/EndorsementSearch'/>
      </port>
    </service>
  </rdf:RDF>
</definitions>"""

#"

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
