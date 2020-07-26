from Xml.Xslt import test_harness

expected_1="""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform' xmlns:sch='http://www.ascc.net/xml/schematron'>
  <xsl:template match='/'>
    <xsl:apply-templates mode='M0'/>
    <xsl:apply-templates mode='M1'/>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='rss' mode='M0' priority='4000'>
    <xsl:choose>
      <xsl:when test='@version'/>
      <xsl:otherwise>An RSS version identifier should be supplied</xsl:otherwise>
    </xsl:choose>
    <xsl:if test='@version != 0.91'>This Schematron validator is for RSS 0.91 only</xsl:if>
    <xsl:choose>
      <xsl:when test='count(channel) = 1'/>
      <xsl:otherwise>An RSS element can only contain a single channel element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='channel' mode='M0' priority='3999'>
    <xsl:choose>
      <xsl:when test='title'/>
      <xsl:otherwise>You must provide a title for your channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='link'/>
      <xsl:otherwise>You must provide a link for your channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='description'/>
      <xsl:otherwise>You must provide a description of your channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='language'/>
      <xsl:otherwise>You must specify the language in which the content of your channel is written.</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='count(copyright) &lt; 2'/>
      <xsl:otherwise>Only one copyright element should be supplied per channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='count(image) &lt; 2'/>
      <xsl:otherwise>Only one image element should be supplied per channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='count(textinput) &lt; 2'/>
      <xsl:otherwise>Only one textinput element can be supplied per channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='count(skipHours) &lt; 2'/>
      <xsl:otherwise>One one skipHours element can be supplied per channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='count(skipDays) &lt; 2'/>
      <xsl:otherwise>One one skipDays element can be supplied per channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='managingEditor'/>
      <xsl:otherwise>You should provide an email address for the managing editor of your channel</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='webMain'/>
      <xsl:otherwise>You should provide an email address for the webmain of your channel</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='skipHours' mode='M0' priority='3998'>
    <xsl:choose>
      <xsl:when test='count(hour) > 0'/>
      <xsl:otherwise>The skipHours element should contain a least one hour element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='skipDays' mode='M0' priority='3997'>
    <xsl:choose>
      <xsl:when test='count(day) > 0'/>
      <xsl:otherwise>The skipDays element should contain a least one day element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='title|description|link' mode='M0' priority='3996'>
    <xsl:choose>
      <xsl:when test='parent::channel or parent::image or parent::item or parent::textinput'/>
      <xsl:otherwise>A<xsl:text xml:space='preserve'> </xsl:text>
        <xsl:value-of select='name(.)'/>
        <xsl:text xml:space='preserve'> </xsl:text>element can only be contained with a channel, image, item or textinput element.</xsl:otherwise>
    </xsl:choose>
    <xsl:if test='child::*'>A<xsl:text xml:space='preserve'> </xsl:text>
      <xsl:value-of select='name(.)'/>
      <xsl:text xml:space='preserve'> </xsl:text>element cannot contain sub-elements, remove any additional markup</xsl:if>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='name' mode='M0' priority='3995'>
    <xsl:choose>
      <xsl:when test='parent::textinput'/>
      <xsl:otherwise>A name element can only be contained within a textinput element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='url' mode='M0' priority='3994'>
    <xsl:choose>
      <xsl:when test='parent::image'/>
      <xsl:otherwise>A url element can only be contained within an image element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='width' mode='M0' priority='3993'>
    <xsl:choose>
      <xsl:when test='parent::image'/>
      <xsl:otherwise>A width element can only be contained within an image element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='height' mode='M0' priority='3992'>
    <xsl:choose>
      <xsl:when test='parent::image'/>
      <xsl:otherwise>A height element can only be contained within an image element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='image' mode='M0' priority='3991'>
    <xsl:choose>
      <xsl:when test='title'/>
      <xsl:otherwise>Images must have titles. The title is used for the ALT text of the image.</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='count(width) = count(height)'/>
      <xsl:otherwise>Width and Height elements should be balanced</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='url'/>
      <xsl:otherwise>This image does not have a url</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='textinput' mode='M0' priority='3990'>
    <xsl:choose>
      <xsl:when test='title'/>
      <xsl:otherwise>A textinput must have a title. It is used to label the submit button for the field</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='name'/>
      <xsl:otherwise>A textinput must have a name. It is used to identify the input element in the form</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='link'/>
      <xsl:otherwise>A textinput must have a link. It is used to identify the target to which the form is sent</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='item' mode='M0' priority='3989'>
    <xsl:choose>
      <xsl:when test='parent::channel'/>
      <xsl:otherwise>An item element can only occur within a channel element</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='title'/>
      <xsl:otherwise>You must provide a title for this item</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='link'/>
      <xsl:otherwise>You must provide a link for this item</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='width' mode='M0' priority='3988'>
    <xsl:choose>
      <xsl:when test='preceding::height or following::height'/>
      <xsl:otherwise>A width should be accompanied by a height</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='height' mode='M0' priority='3987'>
    <xsl:choose>
      <xsl:when test='preceding::width or following::width'/>
      <xsl:otherwise>A height should be accompanied by a width</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M0'/>
  </xsl:template>
  <xsl:template match='text()' mode='M0' priority='-1'/>
  <xsl:template match='language' mode='M1' priority='4000'>
    <xsl:choose>
      <xsl:when test='string-length(.) > 0'/>
      <xsl:otherwise>You must specify a valid language code within a language element</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test=". = 'af' or . = 'sq' or . = 'eu' or . = 'be' or . = 'bg' or . = 'ca' or         . = 'zh-cn' or . = 'zh-tw' or . = 'hr' or . = 'cs' or . = 'da' or . = 'nl' or         . = 'nl-be' or . = 'nl-nl' or . = 'en' or . = 'en-au' or . = 'en-bz' or         . = 'en-ca' or . = 'en-ie' or . = 'en-jm' or . = 'en-nz' or . = 'en-ph' or         . = 'en-za' or . = 'en-tt' or . = 'en-gb' or . = 'en-us' or . = 'en-zw' or         . = 'fo' or . = 'fi' or . = 'fr' or . = 'fr-be' or . = 'fr-ca' or . = 'fr-fr' or         . = 'fr-lu' or . = 'fr-mc' or . = 'fr-ch' or . = 'gl' or . = 'gd' or . = 'de' or         . = 'de-at' or . = 'de-de' or . = 'de-li' or . = 'de-lu' or . = 'de-ch' or         . = 'el' or . = 'hu' or . = 'is' or . = 'in' or . = 'ga' or . = 'it' or         . = 'it-it' or . = 'it-ch' or . = 'ja' or . = 'ko' or . = 'mk' or . = 'no' or         . = 'pl' or . = 'pt' or . = 'pt-br' or . = 'pt-pt' or . = 'ro' or . = 'ro-mo' or         . = 'ro-ro' or . = 'ru' or . = 'ru-mo' or . = 'ru-ru' or . = 'sr' or . = 'sk' or         . = 'sl' or . = 'es' or . = 'es-ar' or . = 'es-bo' or . = 'es-cl' or . = 'es-co' or         . = 'es-cr' or . = 'es-do' or . = 'es-ec' or . = 'es-sv' or . = 'es-gt' or . = 'es-hn' or         . = 'es-mx' or . = 'es-ni' or . = 'es-pa' or . = 'es-py' or . = 'es-pe' or . = 'es-pr' or         . = 'es-es' or . = 'es-uy' or . = 'es-ve' or . = 'sv' or . = 'sv-fi' or . = 'sv-se' or . = 'tr' or         . = 'uk'"/>
      <xsl:otherwise>Invalid language code</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='link' mode='M1' priority='3999'>
    <xsl:choose>
      <xsl:when test="starts-with(., 'http://') or starts-with(., 'ftp://')"/>
      <xsl:otherwise>Links should only be made to http or ftp resources.</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='skipHours' mode='M1' priority='3998'>
    <xsl:choose>
      <xsl:when test='count(hour) &lt; 25'/>
      <xsl:otherwise>There is a limit of 24 hour elements within a<xsl:text xml:space='preserve'> </xsl:text>
        <xsl:value-of select='name(.)'/>
        <xsl:text xml:space='preserve'> </xsl:text>element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='hour' mode='M1' priority='3997'>
    <xsl:choose>
      <xsl:when test='number(.) > 0 and number(.) &lt; 24'/>
      <xsl:otherwise>Hour values should be in the range 0-23</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='skipDays' mode='M1' priority='3996'>
    <xsl:choose>
      <xsl:when test='count(day) &lt; 8'/>
      <xsl:otherwise>There is a limit of 7 day elements within a<xsl:text xml:space='preserve'> </xsl:text>
        <xsl:value-of select='name(.)'/>
        <xsl:text xml:space='preserve'> </xsl:text>element</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='day' mode='M1' priority='3995'>
    <xsl:choose>
      <xsl:when test=". = 'Monday' or . = 'Tuesday' or . = 'Wednesday' or         . = 'Thursday' or . = 'Friday' or         . = 'Saturday' or . = 'Sunday'"/>
      <xsl:otherwise>Days should be listed as Monday, Tuesday, Wednesday, Thursday, Friday, Saturday and Sunday</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='image' mode='M1' priority='3994'>
    <xsl:choose>
      <xsl:when test='height'/>
      <xsl:otherwise>An image height has not been supplied. A default height of 31 pixels will be assumed</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='width'/>
      <xsl:otherwise>An image width has not been supplied. A default width of 88 pixels will be assumed</xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test='url'/>
      <xsl:otherwise>This image does not have a url</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='width' mode='M1' priority='3993'>
    <xsl:choose>
      <xsl:when test='string-length(.) > 0'/>
      <xsl:otherwise>Width elements should not be empty</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='height' mode='M1' priority='3992'>
    <xsl:choose>
      <xsl:when test='string-length(.) > 0'/>
      <xsl:otherwise>Height elements should not be empty</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M1'/>
  </xsl:template>
  <xsl:template match='text()' mode='M1' priority='-1'/>
  <xsl:template match='channel' mode='M2' priority='4000'>
    <xsl:if test='rating and         ((string-length(.) &lt; 20 or           string-length(.) > 500))'>Supplied PICS ratings must be between 20-500 characters in length</xsl:if>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='link' mode='M2' priority='3999'>
    <xsl:choose>
      <xsl:when test='string-length(.) > 1 and         string-length(.) &lt; 500'/>
      <xsl:otherwise>Link urls must be between 1-500 characters in length.</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='width' mode='M2' priority='3998'>
    <xsl:choose>
      <xsl:when test='number(.) &lt; 144 and         number(.) > 0'/>
      <xsl:otherwise>Images width must be between 1-144 pixels</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='height' mode='M2' priority='3997'>
    <xsl:choose>
      <xsl:when test='number(.) &lt; 400 and         number(.) > 0'/>
      <xsl:otherwise>Images height must be between 1-400 pixels</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='title' mode='M2' priority='3996'>
    <xsl:choose>
      <xsl:when test='string-length(.) > 1 and         string-length(.) &lt; 100'/>
      <xsl:otherwise>Titles must be between 1-100 characters in length</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='description' mode='M2' priority='3995'>
    <xsl:if test='parent::channel and         (string-length(.) = 0 or          string-length(.) > 500)'>Channel descriptions must be between 1-500 characters in length</xsl:if>
    <xsl:if test='parent::item and         (string-length(.) = 0 or          string-length(.) > 500)'>Item descriptions must be between 1-500 characters in length</xsl:if>
    <xsl:if test='parent::image and         (string-length(.) = 0 or          string-length(.) > 100)'>Image descriptions must be between 1-100 characters in length</xsl:if>
    <xsl:if test='parent::textinput and         (string-length(.) = 0 or          string-length(.) > 500)'>Textinput descriptions must be between 1-500 characters in length</xsl:if>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='copyright|pubDate|lastBuildDate|managingEditor|webMain' mode='M2' priority='3994'>
    <xsl:choose>
      <xsl:when test='string-length(.) > 1 and         string-length(.) &lt; 100'/>
      <xsl:otherwise>
        <xsl:text xml:space='preserve'> </xsl:text>
        <xsl:value-of select='name(.)'/>
        <xsl:text xml:space='preserve'> </xsl:text>elements must be between 1-100 characters in length</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='url' mode='M2' priority='3993'>
    <xsl:choose>
      <xsl:when test='string-length(.) > 0'/>
      <xsl:otherwise>url elements must not be empty</xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates mode='M2'/>
  </xsl:template>
  <xsl:template match='text()' mode='M2' priority='-1'/>
  <xsl:template match='text()' priority='-1'/>
</xsl:stylesheet>"""


def Test(tester):
    source = test_harness.FileInfo(uri="Xml/Xslt/Borrowed/rss.schematron")
    sheet = test_harness.FileInfo(uri="Xml/Xslt/Borrowed/schematron-skel-ns.xslt")
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
