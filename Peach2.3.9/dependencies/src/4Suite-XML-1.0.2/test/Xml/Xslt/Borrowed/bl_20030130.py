# Universal Turing Machine
# from http://www.unidex.com/turing/utm.htm

from Xml.Xslt import test_harness

source_1 = """<?xml version="1.0"?>
<turing-machine version="0.1">

<!-- This Turing machine (TM) adds one to a whole number.
     For example, if the initial tape is "199", then
     the final tape will be "200".

     The Turing machine assumes that the first (i.e.,
     leftmost) symbol on the tape is the leftmost digit
     in the number.

     If the input tape is completely blank, then the final
     tape will be "1". So, if the input tape is " 43",
     then the Turing machine will assume that tape does not
     contain a number.

     This Turing Machine Markup Language (TMML) document complies
     with the DTD for TMML, which is available at
     http://www.unidex.com/turing/tmml.dtd.

     This Turing machine can be executed by an XSLT stylesheet that is
     available at http://www.unidex.com/turing/utm.xsl. This stylesheet
     is a Universal Turing Machine.

     The following Instant Saxon command will execute the Turing machine
     described by this TMML document using the utm.xsl stylesheet:

        saxon add_one_tm.xml utm.xsl tape=199

     This TMML document is available at
     http://www.unidex.com/turing/add_one_tm.xml.

     Developed by Bob Lyons of Unidex, Inc.

     Please email any comments about this TMML document to
     boblyons@unidex.com.
-->

<!-- COPYRIGHT NOTICE and LICENSE.

     Copyright (c) 2001 Unidex, Inc. All rights reserved.

     Unidex, Inc. grants you permission to copy, modify, distribute,
     and/or use the TMML document provided that you agree to the
     following conditions:

     1. You must include this COPYRIGHT NOTICE and LICENSE
        in all copies or substantial portions of the TMML document.

     2. The TMML document is licensed to the user on an "AS IS" basis.
        Unidex Inc. makes no warranties, either express or implied,
        with respect to the TMML document including but not limited to any
        warranty of merchantability or fitness for any particular
        purpose. Unidex Inc. does not warrant that the operation
        of the TMML document will be uninterrupted or error-free,
        or that defects in the TMML document will be corrected.
        You the user are solely responsible for determining the
        appropriateness of the TMML document for your use and accept
        full responsibility for all risks associated with its use.
        Unidex Inc. is not and will not be liable for any
        direct, indirect, special, incidental or other damages
        of any kind (including loss of profits or interruption of business)
        however caused even if Unidex Inc. has been advised of the
        possibility of such damages.
-->


    <!-- The symbols are "0" through "9".
    -->
    <symbols>0123456789</symbols>

    <states>
        <!-- In the go_right state, the Turing machine moves the
             tape head to the blank symbol to the right of the
             number.
        -->
        <state start="yes">go_right</state>

        <!-- In the increment state, the Turing machine keeps moving
             left and changing 9's to 0's until it finds a digit
             other than "9" or a blank symbol. When it finds a digit
             other than "9" (or a blank symbol, which it treats as
             the digit "0"), it increments the digit (e.g., replaces
             "3" with "4").
        -->
        <state>increment</state>

        <state halt="yes">stop</state>
    </states>

    <!-- The transition function for the TM.
    -->
    <transition-function>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="0"/>
            <to next-state="go_right" next-symbol="0" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="1"/>
            <to next-state="go_right" next-symbol="1" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="2"/>
            <to next-state="go_right" next-symbol="2" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="3"/>
            <to next-state="go_right" next-symbol="3" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="4"/>
            <to next-state="go_right" next-symbol="4" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="5"/>
            <to next-state="go_right" next-symbol="5" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="6"/>
            <to next-state="go_right" next-symbol="6" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="7"/>
            <to next-state="go_right" next-symbol="7" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="8"/>
            <to next-state="go_right" next-symbol="8" movement="right"/>
        </mapping>
        <mapping>
            <!-- Move to the right of the number. -->
            <from current-state="go_right" current-symbol="9"/>
            <to next-state="go_right" next-symbol="9" movement="right"/>
        </mapping>
        <mapping>
            <!-- Found the blank that follows the number.
                 Change to the increment state and start moving left. -->
            <from current-state="go_right" current-symbol=" "/>
            <to next-state="increment" next-symbol=" " movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 9 to a 0 and move left. -->
            <from current-state="increment" current-symbol="9"/>
            <to next-state="increment" next-symbol="0" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 0 to a 1. We're done. -->
            <from current-state="increment" current-symbol="0"/>
            <to next-state="stop" next-symbol="1" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the blank to a 1. We're done. -->
            <from current-state="increment" current-symbol=" "/>
            <to next-state="stop" next-symbol="1" movement="none"/>
        </mapping>
        <mapping>
            <!-- Change the 1 to a 2. We're done. -->
            <from current-state="increment" current-symbol="1"/>
            <to next-state="stop" next-symbol="2" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 2 to a 3. We're done. -->
            <from current-state="increment" current-symbol="2"/>
            <to next-state="stop" next-symbol="3" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 3 to a 4. We're done. -->
            <from current-state="increment" current-symbol="3"/>
            <to next-state="stop" next-symbol="4" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 4 to a 5. We're done. -->
            <from current-state="increment" current-symbol="4"/>
            <to next-state="stop" next-symbol="5" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 5 to a 6. We're done. -->
            <from current-state="increment" current-symbol="5"/>
            <to next-state="stop" next-symbol="6" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 6 to a 7. We're done. -->
            <from current-state="increment" current-symbol="6"/>
            <to next-state="stop" next-symbol="7" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 7 to a 8. We're done. -->
            <from current-state="increment" current-symbol="7"/>
            <to next-state="stop" next-symbol="8" movement="left"/>
        </mapping>
        <mapping>
            <!-- Change the 8 to a 9. We're done. -->
            <from current-state="increment" current-symbol="8"/>
            <to next-state="stop" next-symbol="9" movement="left"/>
        </mapping>
    </transition-function>
</turing-machine>"""

sty_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="text"/>

<!--
     This XSLT stylesheet runs the Turing machine (TM) that is
     specified by the source document. The initial tape for the
     Turing machine is specified by a global parameter named 'tape'.
     (Thus, this XSLT stylesheet is a Universal Turing Machine.)

     The source document, which specifies a Turing machine,
     is an XML document that conforms to the
     Turing Machine Markup Language (TMML). The DTD for TMML
     is available at http://www.unidex.com/turing/tmml.dtd.

     This stylesheet validates the source document using XPath
     expressions (rather than using the DTD for TMML).

     The tape for the Turing machine is specified via the
     global parameter named "tape". Each character in the
     string represents a symbol on the tape. The tape must
     contain at least one symbol.  Each of the symbols on the
     tape must be either the blank symbol or one of the symbols
     defined in the symbols element of the TMML source document.

     The following Instant SAXON command will invoke the
     utm.xsl stylesheet, in order to execute the Turing machine
     that adds one to the number specified on the tape.
     The Turing machine is described by the TMML document named
     "add_one_tm.xml".
     The input tape for the Turing machine is "199".

         saxon add_one_tm.xml utm.xsl tape=199

     The output of this command will include the final name
     which will contain the number "200".

     In theory, the tape for the Turing machine is infinite
     in both directions (i.e., both to the left and to the right).
     The stylesheet represents the tape as a string. The stylesheet
     will append the blank symbol to the right end of the tape when
     the tape head of the Turing machine moves to the right of the
     last symbol on the tape. Likewise, the stylesheet will insert a
     blank symbol at the beginning of the tape when the tape head
     of the Turing machine moves to the left of the leftmost symbol
     on the tape.

     By default, the tape head of the Turing machine is initially
     positioned over the first symbol on the tape (i.e., the first
     character of the value of the 'tape' parameter). You can
     specify a different initial position for the tape head via the
     optional global parameter named 'start_position'. The value of
     the 'start_position' parameter should be the character position
     of the symbol over which you want the tape head to be positioned
     initially. If you want the tape head to be initially positioned
     over the 2nd symbol on the tape, then set the 'start_position'
     parameter to 2. The default value for the 'start_position'
     parameter is 1.

     The Turing machine will crash if the transition
     function is not defined for the current state and the
     current symbol.

     The Turing machine will stop when it transitions to
     one of the halt states.

     The Turing machine's procedure for processing the input tape
     is as follows:
     1. When the Turing machine begins operation, the current
        state is the start state.
     2. The Turing machine reads the tape symbol that is under the
    Turing machine's tape head. This symbol is referred to as
    the current symbol. When the Turing machine begins operation,
    the tape head is positioned over the symbol whose character
        position is specified by the 'start_position' parameter. The
        default value of the 'start_position' parameter is 1.
     3. The Turing machine (TM) uses the transition function to map
        the current state and current symbol to the following:
        the next state, the next symbol and the movement for the
    tape head. If the transition function is not defined for the
        current state and current symbol, then the TM crashes.
     4. The Turing machine changes its state to the next state,
        which was returned by the transition function.
     5. The Turing machine overwrites the current symbol on the
        tape with the next symbol, which was returned by the
        transition function.
     6. The Turing machine moves its tape head one symbol to the
        left or to the right, or does not move the tape head,
        depending on the value of the 'movement' attribute that is
    returned by the transition function. If the TM moves the tape head
        to the right of the rightmost symbol, then a blank symbol
        is appended to the end of the tape and this new blank symbol
        becomes the current symbol. If the TM moves the tape head
        to the left of the leftmost symbol, then a blank symbol
        is inserted at the beginning of the tape and this new blank symbol
        becomes the current symbol.
     7. If the Turing machine's state is a halt state, then the
        TM halts. Otherwise, repeat substep #2.

     The stylesheet will display information about each iteration
     of the Turing machine's operation. This information includes
     a snapshot of the tape and a pointer (i.e., "^") under the
     current symbol. The pointer represents the tape head.

     The American Mathematical Society provides an overview of
     Turing machines at http://www.ams.org/new-in-math/cover/turing.html.

     This stylesheet is available at http://www.unidex.com/turing/utm.xsl.

     Developed by Bob Lyons of Unidex, Inc.

     Please email any comments about this stylesheet to
     boblyons@unidex.com.
-->

<!-- COPYRIGHT NOTICE and LICENSE.

     Copyright (c) 2001 Unidex, Inc. All rights reserved.

     Unidex, Inc. grants you permission to copy, modify, distribute,
     and/or use the stylesheet provided that you agree to the
     following conditions:

     1. You must include this COPYRIGHT NOTICE and LICENSE
        in all copies or substantial portions of the stylesheet.

     2. The stylesheet is licensed to the user on an "AS IS" basis.
        Unidex Inc. makes no warranties, either express or implied,
        with respect to the stylesheet including but not limited to any
        warranty of merchantability or fitness for any particular
        purpose. Unidex Inc. does not warrant that the operation
        of the stylesheet will be uninterrupted or error-free,
        or that defects in the stylesheet will be corrected.
        You the user are solely responsible for determining the
        appropriateness of the stylesheet for your use and accept
        full responsibility for all risks associated with its use.
        Unidex Inc. is not and will not be liable for any
        direct, indirect, special, incidental or other damages
        of any kind (including loss of profits or interruption of business)
        however caused even if Unidex Inc. has been advised of the
        possibility of such damages.
-->

<!-- Global parameters. -->

<xsl:param name="tape" />

<xsl:param name="start_position" select="'1'" />

<!-- Global variables. -->

<xsl:variable name="symbols" select="/turing-machine/symbols" />

<xsl:variable name="blank_symbol" >
    <xsl:choose>

    <xsl:when test="string( /turing-machine/symbols/@blank-symbol ) != '' ">
        <xsl:value-of select="/turing-machine/symbols/@blank-symbol" />
    </xsl:when>

    <xsl:otherwise>
        <xsl:text> </xsl:text>
    </xsl:otherwise>

    </xsl:choose>
</xsl:variable>

<!-- Keys. -->

<xsl:key name="state" match="/turing-machine/states/state" use="text()"/>

<xsl:key name="mapping" match="/turing-machine/transition-function/mapping"
         use="concat( from/@current-state, ' ', from/@current-symbol )"/>

<!-- Templates. -->

<xsl:template match="/">

    <xsl:variable name="tm_errors">
        <xsl:call-template name="validate_tm"/>
    </xsl:variable>

    <xsl:variable name="tape_errors">
        <xsl:if test="$tm_errors = '' ">
            <xsl:call-template name="validate_tape">
                <xsl:with-param name="tape" select="$tape"/>
            </xsl:call-template>
            <xsl:call-template name="validate_start_position">
                <xsl:with-param name="start_position" select="$start_position"/>
                <xsl:with-param name="tape_length"
                                select="string-length( $tape )" />
            </xsl:call-template>
        </xsl:if>
    </xsl:variable>

    <xsl:choose>

    <xsl:when test="$tm_errors = '' and $tape_errors = '' ">
        <xsl:variable name="start_state"
                      select="/turing-machine/states/state[@start='yes']" />

        <xsl:call-template name="go_to_next_state">
            <xsl:with-param name="step_number" select="'1' "/>
            <xsl:with-param name="state" select="$start_state"/>
            <xsl:with-param name="tape" select="$tape"/>
            <xsl:with-param name="tape_position" select="$start_position"/>
        </xsl:call-template>
    </xsl:when>

    <xsl:otherwise>
        <!-- Display errors. -->
        <xsl:value-of select="$tm_errors"/>
        <xsl:value-of select="$tape_errors"/>
    </xsl:otherwise>

    </xsl:choose>
</xsl:template>

<xsl:template name="validate_tm">

    <!-- Validate the Turing machine that is described in the source document.
         This template returns error messages that describe any errors that
         are found. If no errors are found in the source document, then
         the template returns nothing.
    -->

    <xsl:if test="count( /turing-machine ) = 0">
        <xsl:text>Error in source document. The document element of the source element must be 'turing-machine'.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/@*[ name() != 'version' ] ) != 0 ">
        <xsl:text>Error in source document. The 'turing-machine' element contains an unexpected attribute. The only valid attribute for the 'turing-machine' element is 'version'.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="string( /turing-machine/@version ) != '0.1' ">
        <xsl:text>Error in source document. The 'turing-machine' element must contain the 'version' attribute, the value of which must be '0.1'.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:for-each select="/turing-machine/text()">
        <xsl:if test="translate( ., '&#x9;&#xA;&#xD;&#x20;', '' ) != '' ">
            <xsl:text>Error in source document. The 'turing-machine' element contains non-whitespace text.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>
    </xsl:for-each>

    <xsl:if test="count( /turing-machine/*[ name() != 'symbols' and
                                            name() != 'states'  and
                                            name() != 'transition-function' ] )
                  != 0 " >
        <xsl:text>Error in source document. The 'turing-machine' element contains an unexpected child element. Only the 'states', 'symbols' and 'transition-function' elements are allowed to be child elements of the 'turing-machine' element.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/states ) != 1">
        <xsl:text>Error in source document. There must be exactly one 'states' element.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/states/@* ) != 0">
        <xsl:text>Error in source document. The 'states' element must not contain any attributes.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:for-each select="/turing-machine/states/text()">
        <xsl:if test="translate( ., '&#x9;&#xA;&#xD;&#x20;', '' ) != '' ">
            <xsl:text>Error in source document. The 'states' element contains non-whitespace text.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>
    </xsl:for-each>

    <xsl:if test="count( /turing-machine/states/state ) = 0">
        <xsl:text>Error in source document. The source document must include at least one 'state' element.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/states/*[name() != 'state'] ) ">
        <xsl:text>Error in source document. The 'states' element contains an unexpected child element. Only the 'state' elements are allowed to be child elements of the 'states' element.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/states/state/* ) != 0">
        <xsl:text>Error in source document. A 'state' element must not contain any subelements.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/states/state[@start = 'yes'] ) != 1">
        <xsl:text>Error in source document. The 'turing-machine' element must contain exactly one start state.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/states/state[@halt = 'yes'] ) = 0">
        <xsl:text>Error in source document. There must be at least one halt state.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:for-each select="/turing-machine/states/state">

        <xsl:variable name="matching_nodes"
                      select="key( 'state', . )"/>
        <xsl:if test="count( $matching_nodes ) != 1 and
                      generate-id( . ) = generate-id( $matching_nodes[1] )">
            <xsl:text>Error in source document. There is more than one 'state' element that contains the value '</xsl:text>
            <xsl:value-of select="."/>
            <xsl:text>'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="string-length( . ) = 0 ">
            <xsl:text>Error in source document. Found a 'state' element that contains a null value.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./@*[ name() != 'start' and name() != 'halt' ] )
                      != 0 ">
            <xsl:text>Error in source document. A 'state' element contains an unexpected attribute. The valid attributes for the 'state' element are 'start' and 'halt'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./@halt[. != 'yes' and . != 'no'] ) != 0">
            <xsl:text>Error in source document. The 'halt' attribute in a 'state' element has an invalid value. The valid values are 'yes' and 'no'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./@start[. != 'yes' and . != 'no'] ) != 0">
            <xsl:text>Error in source document. The 'start' attribute in a 'state' element has an invalid value. The valid values are 'yes' and 'no'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="contains( translate( ., '&#x9;&#xA;&#xD;&#x20;', '    ' ),
                                ' ') ">
            <xsl:text>Error in source document. The value of a 'state' element contains whitespace.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

    </xsl:for-each>

    <xsl:if test="count( /turing-machine/symbols ) != 1">
        <xsl:text>Error in source document. The 'turing-machine' element must contain exactly one 'symbols' subelement.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/symbols/@*[name() !=
                                                    'blank-symbol'] ) != 0">
        <xsl:text>Error in source document. The 'symbols' element contains an unexpected attribute. The only valid attribute for the 'symbols' element is 'start-symbol'.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="string-length( /turing-machine/symbols/@blank-symbol ) &gt;
                  1">
        <xsl:text>Error in source document. The length of the value of the 'blank-symbol' attribute must not be greater than 1.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/symbols/* ) != 0">
        <xsl:text>Error in source document. The 'symbols' element must not contain any subelements.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="string-length( /turing-machine/symbols ) = 0 ">
        <xsl:text>Error in source document. The 'symbols' element must contain at least one symbol.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="contains( /turing-machine/symbols, $blank_symbol )" >
        <xsl:text>Error in source document. The value of the 'symbols' element must not contain the blank symbol.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/transition-function ) != 1">
        <xsl:text>Error in source document. The 'turing-machine' element must contain exactly one 'transition-function' subelement.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:for-each select="/turing-machine/transition-function/text()">
        <xsl:if test="translate( ., '&#x9;&#xA;&#xD;&#x20;', '' ) != '' ">
            <xsl:text>Error in source document. The 'transition-function' element contains non-whitespace text.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>
    </xsl:for-each>


    <xsl:if test="count( /turing-machine/transition-function/@* ) != 0">
        <xsl:text>Error in source document. The 'turing-machine' element must not contain any attributes.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/transition-function/*[name() !=
                                                               'mapping'] ) !=
                  0" >
        <xsl:text>Error in source document. The 'transition-function' element contains an unexpected child element. Only the 'mapping' elements are allowed to be child elements of the 'transition-function' element.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/transition-function/mapping/from/* )
                  != 0">
        <xsl:text>Error in source document. A 'from' element must not contain any subelements.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:if test="count( /turing-machine/transition-function/mapping/to/* )
                  != 0">
        <xsl:text>Error in source document. A 'to' element must not contain any subelements.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:if>

    <xsl:for-each select="/turing-machine/transition-function/mapping">

        <xsl:variable name="matching_nodes"
                      select="key( 'mapping',
                                   concat( ./from/@current-state,
                                           ' ',
                                           ./from/@current-symbol
                                         )
                                 )" />

        <xsl:if test="count( $matching_nodes ) != 1 and
                      generate-id( . ) = generate-id( $matching_nodes[1] )">
            <xsl:text>Error in source document. There is more than one 'mapping' element whose current symbol is '</xsl:text>
            <xsl:value-of select="./from/@current-symbol"/>
            <xsl:text>' and whose current state is '</xsl:text>
            <xsl:value-of select="./from/@current-state"/>
            <xsl:text>'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:for-each select="./text()">
            <xsl:if test="translate( ., '&#x9;&#xA;&#xD;&#x20;', '' ) != '' ">
                <xsl:text>Error in source document. A 'mapping' element contains non-whitespace text.</xsl:text>
                <xsl:text>&#x0D;&#x0A;</xsl:text>
            </xsl:if>
        </xsl:for-each>

        <xsl:if test="count( ./@* ) != 0 ">
            <xsl:text>Error in source document. A 'mapping' element must not contain any attributes.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./*[name() != 'from' and
                                 name() != 'to']      ) != 0" >
            <xsl:text>Error in source document. A 'mapping' element contains an unexpected child element. Only the 'to' and 'from' elements are allowed to be child elements of the 'mapping' element.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./from ) != 1">
            <xsl:text>Error in source document. A 'mapping' element must contain exactly one 'from' sublement.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:for-each select="./from/text()">
            <xsl:if test="translate( ., '&#x9;&#xA;&#xD;&#x20;', '' ) != '' ">
                <xsl:text>Error in source document. A 'from' element contains non-whitespace text.</xsl:text>
                <xsl:text>&#x0D;&#x0A;</xsl:text>
            </xsl:if>
        </xsl:for-each>

        <xsl:if test="count( ./to ) != 1">
            <xsl:text>Error in source document. A 'mapping' element must contain exactly one 'to' sublement.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:for-each select="./to/text()">
            <xsl:if test="translate( ., '&#x9;&#xA;&#xD;&#x20;', '' ) != '' ">
                <xsl:text>Error in source document. A 'to' element contains non-whitespace text.</xsl:text>
                <xsl:text>&#x0D;&#x0A;</xsl:text>
            </xsl:if>
        </xsl:for-each>

        <xsl:if test="count( ./from/@*[ name() != 'current-state' and
                                        name() != 'current-symbol'   ] ) != 0 ">
            <xsl:text>Error in source document. A 'from' element contains an unexpected attribute. The valid attributes for the 'from' element are 'current-state' and 'current-symbol'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./from[ count( @current-state ) != 1 ] ) != 0">
            <xsl:text>Error in source document. Found a 'from' element that does not contain a 'current-state' attribute.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./from[ count( @current-symbol ) != 1 ] ) != 0">
            <xsl:text>Error in source document. Found a 'from' element that does not contain a 'current-symbol' attribute.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( key( 'state', ./from[1]/@current-state ) ) = 0 ">
            <xsl:text>Error in source document. Found a 'current-state' attribute that contains a value ('</xsl:text>
            <xsl:value-of select="./from[1]/@current-state"/>
            <xsl:text>') that is not a value of a 'state' element.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="string-length( ./from[1]/@current-symbol ) != 1 ">
            <xsl:text>Error in source document. The length of the value of a 'current-symbol' attribute ('</xsl:text>
            <xsl:value-of select="./from[1]/@current-symbol"/>
            <xsl:text>') is not equal to 1.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="not( contains( $symbols, ./from[1]/@current-symbol ) or
                           ./from[1]/@current-symbol = $blank_symbol
                         )">
            <xsl:text>Error in source document. Found a 'current-symbol' attribute that contains a value ('</xsl:text>
            <xsl:value-of select="./from[1]/@current-symbol"/>
            <xsl:text>') that is not a symbol in the 'symbols' element and that is not the blank symbol.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./to/@*[ name() != 'next-state'  and
                                      name() != 'next-symbol' and
                                      name() != 'movement'   ] ) != 0 ">
            <xsl:text>Error in source document. A 'to' element contains an unexpected attribute. The valid attributes for the 'to' element are 'next-state', 'next-symbol' and 'movement'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./to[ count( @next-state ) != 1 ] ) != 0">
            <xsl:text>Error in source document. Found a 'to' element that does not contain a 'next-state' attribute.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./to[ count( @next-symbol ) != 1 ] ) != 0">
            <xsl:text>Error in source document. Found a 'to' element that does not contain a 'next-symbol' attribute.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./to[ count( @movement ) != 1 ] ) != 0">
            <xsl:text>Error in source document. Found a 'to' element that does not contain a 'movement' attribute.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( key( 'state', ./to[1]/@next-state ) ) = 0 ">
            <xsl:text>Error in source document. Found a 'next-state' attribute that contains a value ('</xsl:text>
            <xsl:value-of select="./from[1]/@current-state"/>
            <xsl:text>') that is not a value of a 'state' element.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="string-length( ./to[1]/@next-symbol ) != 1 ">
            <xsl:text>Error in source document. The length of the value of a 'next-symbol' attribute ('</xsl:text>
            <xsl:value-of select="./to[1]/@next-symbol"/>
            <xsl:text>') is not equal to 1.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="not( contains( $symbols, ./to[1]/@next-symbol ) or
                           ./to[1]/@next-symbol = $blank_symbol
                         )">
            <xsl:text>Error in source document. Found a 'next-symbol' attribute that contains a value ('</xsl:text>
            <xsl:value-of select="./from[1]/@current-symbol"/>
            <xsl:text>') that is not a symbol in the 'symbols' element and that is not the blank symbol.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count( ./to/@movement[. != 'left'  and
                                            . != 'right' and
                                            . != 'none'   ] ) != 0">
            <xsl:text>Error in source document. The 'movement' attribute in a 'to' element has an invalid value. The valid values are 'left', 'right' and 'none'.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

    </xsl:for-each>

</xsl:template>

<xsl:template name="validate_tape">
    <xsl:param name="tape"/>

    <!--  Verify that each symbol on the tape is either the
          blank symbol or one of the symbols defined in the
          Turing machine.

          A null tape is an error.
    -->

    <xsl:choose>

    <xsl:when test="$tape = ''">
        <xsl:text>Error. The value of the global 'tape' parameter must contain at least one symbol.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:when>

    <xsl:otherwise>
        <xsl:variable name="first_symbol" select="substring( $tape, 1, 1 )" />

        <xsl:if test="not( contains( $symbols, $first_symbol ) or
                           $first_symbol = $blank_symbol
                         )">
            <xsl:text>Error. A symbol on the tape ('</xsl:text>
            <xsl:value-of select="$first_symbol"/>
            <xsl:text>') is not one of the symbols defined in the Turing machine.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
        </xsl:if>

        <xsl:variable name="subtape"
                      select="substring( $tape, 2 )" />

        <xsl:if test="$subtape != '' ">
            <xsl:call-template name="validate_tape">
                <xsl:with-param name="tape" select="$subtape"/>
                <xsl:with-param name="start_position" select="'1'"/>
            </xsl:call-template>
        </xsl:if>

    </xsl:otherwise>

    </xsl:choose>
</xsl:template>

<xsl:template name="validate_start_position">
    <xsl:param name="start_position"/>
    <xsl:param name="tape_length"/>

    <!--  Verify that the start_position is either null or
          is a number greater than 0 and no greater then
          the length of the tape.
    -->

    <xsl:choose>

    <xsl:when test="$start_position = '' " />

    <xsl:when test="string( number( $start_position ) ) = 'NaN' ">
        <xsl:text>Error. The value of the global 'start-position' parameter is not a number.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:when>

    <xsl:when test="$start_position &gt; string-length( $tape ) or
                    $start_position &lt; 1" >
        <xsl:text>Error. The value of the global 'start-position' parameter is less then one or greater than the length of the tape.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:when>

    </xsl:choose>

</xsl:template>

<xsl:template name="go_to_next_state">
    <xsl:param name="step_number"/> <!-- Increment for each state transition.-->

    <xsl:param name="state"/> <!-- Current state of the Turing machine. -->

    <xsl:param name="tape"/> <!-- Current tape. -->

    <xsl:param name="tape_position"/> <!-- The current tape position expressed
                                           as the offset (in characters) from
                                           the beginning of the tape.
                                           The tape position for the first
                                           symbol on the tape is 1. If the tape
                                           is "abc" and the Turing machine
                                           is currently pointing to "b", then
                                           the tape position would be 2, since
                                           "b" is the 2nd character in the
                                           tape string. -->

    <!-- This recursive named template runs the Turing machine that is
         described by the source document. Each call to this template
         advances the TM to the next step.

         This template assumes that the Turing machine and the tape
         have been validated.
    -->

    <xsl:text>&#x0D;&#x0A;</xsl:text>

    <xsl:text>Step number = </xsl:text>
    <xsl:value-of select="$step_number"/>
    <xsl:text>&#x0D;&#x0A;</xsl:text>

    <xsl:text>Tape        = </xsl:text>
    <xsl:value-of select="$tape"/>
    <xsl:text>&#x0D;&#x0A;</xsl:text>
    <xsl:text>Tape head     </xsl:text>
    <xsl:call-template name="display_tape_head">
        <xsl:with-param name="tape_position" select="$tape_position"/>
    </xsl:call-template>

    <xsl:text>State       = </xsl:text>
    <xsl:value-of select="$state"/>
    <xsl:text>&#x0D;&#x0A;</xsl:text>

    <xsl:variable name="current_symbol" select="substring( $tape,
                                                           $tape_position,
                                                           1 )" />

    <!-- Get the mapping for the current state and current symbol. -->
    <xsl:variable name="mapping"
                  select="key( 'mapping',
                               concat( $state, ' ', $current_symbol )
                             )"/>

    <xsl:variable name="next_state" select="$mapping/to/@next-state"/>

    <xsl:variable name="next_symbol" select="$mapping/to/@next-symbol"/>

    <xsl:variable name="movement" select="$mapping/to/@movement"/>

    <xsl:text>Next symbol = </xsl:text>
    <xsl:value-of select="$next_symbol"/>
    <xsl:text>&#x0D;&#x0A;</xsl:text>

    <xsl:text>Next state  = </xsl:text>
    <xsl:value-of select="$next_state"/>
    <xsl:text>&#x0D;&#x0A;</xsl:text>

    <xsl:text>Movement    = </xsl:text>
    <xsl:value-of select="$movement"/>
    <xsl:text>&#x0D;&#x0A;</xsl:text>

    <xsl:choose>

    <xsl:when test="count( $mapping ) = 0">
        <xsl:text>Error. The transition function is not defined for the current state and current symbol.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
        <xsl:text>The Turing machine is crashing.</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:when>

    <xsl:otherwise>
        <!-- We can advance to the next state. -->

        <!-- Overwrite the current symbol on the tape with the next symbol. -->

        <xsl:variable name="tape_with_next_symbol"
             select="concat( substring( $tape, 1, $tape_position - 1 ),
                             $next_symbol,
                             substring( $tape,
                                        $tape_position + 1 )
                     )"
        />

        <xsl:variable name="new_tape_position">
            <xsl:call-template name="get_new_tape_position">
                <xsl:with-param name="tape_position"
                                select="$tape_position"/>
                <xsl:with-param name="movement" select="$movement"/>
            </xsl:call-template>
        </xsl:variable>

        <xsl:variable name="tape_after_movement">
            <xsl:choose>

            <xsl:when test="$new_tape_position &gt;
                            string-length( $tape_with_next_symbol )">
                <!-- We have to append a blank symbol to the end of the tape.
                -->
                <xsl:value-of select="concat( $tape_with_next_symbol,
                                              $blank_symbol )"/>
            </xsl:when>

            <xsl:when test="$tape_position = 1 and $movement = 'left'">
                <!-- We have to insert a blank symbol at the beginninng
                     of the tape.
                -->
                <xsl:value-of select="concat( $blank_symbol,
                                              $tape_with_next_symbol )"/>
            </xsl:when>

            <xsl:otherwise>
                <xsl:value-of select="$tape_with_next_symbol"/>
            </xsl:otherwise>

            </xsl:choose>

        </xsl:variable>

        <xsl:choose>

        <xsl:when test="key( 'state', $next_state )/@halt = 'yes' ">
            <xsl:text>&#x0D;&#x0A;</xsl:text>
            <xsl:text>The Turing machine has halted.</xsl:text>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
            <xsl:text>Final state = </xsl:text>
            <xsl:value-of select="$next_state"/>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
            <xsl:text>Final tape  = </xsl:text>
            <xsl:value-of select="$tape_after_movement"/>
            <xsl:text>&#x0D;&#x0A;</xsl:text>
            <xsl:text>Tape head     </xsl:text>
            <xsl:call-template name="display_tape_head">
                <xsl:with-param name="tape_position"
                                select="$new_tape_position"/>
            </xsl:call-template>

        </xsl:when>

        <xsl:otherwise>
            <!-- Call ourself recursively, in order to advance to the
                 next state.
            -->

            <xsl:call-template name="go_to_next_state">
                <xsl:with-param name="step_number" select="$step_number + 1"/>
                <xsl:with-param name="state" select="$next_state"/>
                <xsl:with-param name="tape" select="$tape_after_movement"/>
                <xsl:with-param name="tape_position"
                                select="$new_tape_position"/>
            </xsl:call-template>

        </xsl:otherwise>

        </xsl:choose>

    </xsl:otherwise>

    </xsl:choose>

</xsl:template> <!-- go_to_next_state -->

<xsl:template name="display_tape_head">
    <xsl:param name="tape_position"/>

    <!-- Display the tape head as a pointer (i.e., "^") under the
         current symbol. For example, if the tape is "abc" and
         'b' is the current symbol, then the tape head would be
         displayed as a "^" under the "b".
    -->

    <xsl:choose>

    <xsl:when test="$tape_position = 1" >
        <xsl:text>^</xsl:text>
        <xsl:text>&#x0D;&#x0A;</xsl:text>
    </xsl:when>

    <xsl:otherwise>
        <xsl:text> </xsl:text>
        <xsl:call-template name="display_tape_head">
            <xsl:with-param name="tape_position" select="$tape_position - 1"/>
        </xsl:call-template>
    </xsl:otherwise>

    </xsl:choose>
</xsl:template>

<xsl:template name="get_new_tape_position">
    <xsl:param name="tape_position"/>
    <xsl:param name="movement"/>

    <!-- Returns the new tape head position after moving the
         tape head in the direction specified by the movement
         parameter.
    -->

    <xsl:choose>

    <xsl:when test="$movement = 'left'">

        <xsl:choose>

        <xsl:when test="$tape_position = 1">
            <!-- We don't return 0, since a new blank symbol will
                 be inserted at the beginning of the tape.
            -->
            <xsl:value-of select="$tape_position"/>
        </xsl:when>

        <xsl:otherwise>
            <xsl:value-of select="$tape_position - 1"/>
        </xsl:otherwise>

        </xsl:choose>

    </xsl:when>

    <xsl:when test="$movement = 'right'">

        <xsl:value-of select="$tape_position + 1"/>

    </xsl:when>

    <xsl:when test="$movement = 'none'">

        <xsl:value-of select="$tape_position"/>

    </xsl:when>

    <xsl:otherwise>
        <xsl:message terminate="yes">
            <xsl:text>Internal error. Bad value for movement.</xsl:text>
        </xsl:message>
    </xsl:otherwise>

    </xsl:choose>

</xsl:template> <!-- get_new_tape_position -->

<xsl:template match="text()"/> <!-- Do nothing. -->

</xsl:stylesheet>"""

expected_1 = """\r
Step number = 1\r
Tape        = 199\r
Tape head     ^\r
State       = go_right\r
Next symbol = 1\r
Next state  = go_right\r
Movement    = right\r
\r
Step number = 2\r
Tape        = 199\r
Tape head      ^\r
State       = go_right\r
Next symbol = 9\r
Next state  = go_right\r
Movement    = right\r
\r
Step number = 3\r
Tape        = 199\r
Tape head       ^\r
State       = go_right\r
Next symbol = 9\r
Next state  = go_right\r
Movement    = right\r
\r
Step number = 4\r
Tape        = 199 \r
Tape head        ^\r
State       = go_right\r
Next symbol =  \r
Next state  = increment\r
Movement    = left\r
\r
Step number = 5\r
Tape        = 199 \r
Tape head       ^\r
State       = increment\r
Next symbol = 0\r
Next state  = increment\r
Movement    = left\r
\r
Step number = 6\r
Tape        = 190 \r
Tape head      ^\r
State       = increment\r
Next symbol = 0\r
Next state  = increment\r
Movement    = left\r
\r
Step number = 7\r
Tape        = 100 \r
Tape head     ^\r
State       = increment\r
Next symbol = 2\r
Next state  = stop\r
Movement    = left\r
\r
The Turing machine has halted.\r
Final state = stop\r
Final tape  =  200 \r
Tape head     ^\r
"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sty_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          topLevelParams={'tape': 199},
                          title="Universal Turing Machine")
    return
