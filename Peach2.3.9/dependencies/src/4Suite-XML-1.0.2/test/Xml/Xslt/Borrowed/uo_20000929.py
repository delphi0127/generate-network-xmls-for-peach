#Uche's test from Sun's SVG slide publisher
import os
from Xml.Xslt import test_harness

#From Sun's toolkit
sheet_1_uri = "Xml/Xslt/Borrowed/svgslides.xsl"
sheet_2_uri = "Xml/Xslt/Borrowed/svgslides_custom.xsl"
sheet_3_uri = "Xml/Xslt/Borrowed/slidescript.xsl"
source_1_uri = "Xml/Xslt/Borrowed/slides4svg.xml"

saxon_output = """"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<?xml-stylesheet href="slides.css" type="text/css"?>

<svg height='768' width='1024' style='pointer-events:visible' xml:space='preserve' onload='initSlides(evt)' xmlns:xlink='http://www.w3.org/2000/xlink/namespace/'>





            <script><![CDATA[
                var doc = null;

                // Called upon presentation loading
                function initSlides(evt){
                    var target = evt.getTarget();
                    doc = target.getOwnerDocument();

                    hideAndShow(evt, curSlide, curSlide);
                }

                function onPrevSlide(evt){
                    // Process new current slide
                    var oldCurSlide = curSlide;
                    curSlide = curSlide - 1;
                    if(curSlide < 0){
                        curSlide = slideList.length - 1;
                    }

                    hideAndShow(evt, oldCurSlide, curSlide);
                }

                function onNextSlide(evt){
                    // Process new current slide
                    var prevSlide = curSlide;
                    curSlide = curSlide + 1;
                    if(curSlide > (slideList.length - 1)){
                        curSlide = 0;
                    }

                    hideAndShow(evt, prevSlide, curSlide);
                    // alert("onNextSlide");
                }

                function hideAndShow(evt, hideSlide, showSlide){
                    // alert("Hiding : " + hideSlide + " and showing : " + showSlide);

                    // Hide previous current slide and show new
                    // one.
                    var hideSlideName = slideList[hideSlide];
                    var showSlideName = slideList[showSlide];

                    /*if(hideSlideName == null)
                        alert("hideSlideName is null");
                    else
                        alert("hideSlideName is NOT null:" + hideSlideName);*/


                    var slideGroup = doc.getElementById(hideSlideName);
                    slideGroup.setAttribute("style", "visibility:hidden");

                    slideGroup = doc.getElementById(showSlideName);
                    slideGroup.setAttribute("style", "visibility:show");


                    var slideMenuItemId = slideList[hideSlide] + "MenuItem";
                    var menuItem = doc.getElementById(slideMenuItemId);
                    if(menuItem != null)
                        menuItem.setAttribute("class", "slideMenuItem");

                    slideMenuItemId = slideList[showSlide] + "MenuItem";
                    menuItem = doc.getElementById(slideMenuItemId);
                    if(menuItem != null)
                        menuItem.setAttribute("class", "currentSlideMenuItem");

                }

                function onHighlightMenuItem(evt, highlight, itemId){
                    var target = evt.getTarget();
                    var doc = target.getOwnerDocument();

                    var menuItem = doc.getElementById(itemId);
                    if(highlight == "true")
                        menuItem.setAttribute("class", "highlightedSlideMenuItem");
                    else{
                        var curSlideMenuItemId = slideList[curSlide] + "MenuItem";
                        if(curSlideMenuItemId == itemId)
                            menuItem.setAttribute("class", "currentSlideMenuItem");
                        else
                            menuItem.setAttribute("class", "slideMenuItem");
                    }
                }

                function onMenuItemSelected(evt, index){
                    // alert("Should show slide # " + index);
                    var oldCurSlide = curSlide;
                    curSlide = index;
                    hideAndShow(evt, oldCurSlide, index);
                }

                function onSetFill(evt, elementId, fillValue){
                    var element = doc.getElementById(elementId);
                    element.setAttribute("style", "fill:" + fillValue);
                }

                function onExpand(evt, submenuGroupId){
                    var submenuGroup = doc.getElementById(submenuGroupId);
                    submenuGroup.setAttribute("style", "visibility:hidden");
                    var javaScriptCode = "window.expandNow('" + submenuGroupId + "')";
                    window.expandNow = expandNow;
                    setTimeout(javaScriptCode, 1000);
                }

                function expandNow(submenuGroupId){
                    var submenuGroup = doc.getElementById(submenuGroupId);
                    submenuGroup.setAttribute("style", "visibility:show");
                }

                function onCollapse(evt, submenuGroupId){
                    var submenuGroup = doc.getElementById(submenuGroupId);
                    submenuGroup.setAttribute("style", "visibility:hidden");
                }

            ]]></script>
  <script><![CDATA[
                    var slideList = new Array();
                    var slideIndex = new Object();
                    var curSlide = 0;
                slideList[0]="slideShowCover";
            slideIndex["slideShowCover"] = 0;
            slideList[1]="slidesetCover1";
                slideIndex["slidesetCover1"] = 1;
                slideList[2] = "slide1-1";
                    slideIndex["slide1-1"] = 2;
                    slideList[3]="slidesetCover2";
                slideIndex["slidesetCover2"] = 3;
                slideList[4] = "slide2-1";
                    slideIndex["slide2-1"] = 4;
                    slideList[5] = "slide2-2";
                    slideIndex["slide2-2"] = 5;
                    slideList[6] = "slide2-3";
                    slideIndex["slide2-3"] = 6;
                    slideList[7]="slidesetCover3";
                slideIndex["slidesetCover3"] = 7;
                slideList[8] = "slide3-1";
                    slideIndex["slide3-1"] = 8;
                    slideList[9] = "slide3-2";
                    slideIndex["slide3-2"] = 9;
                    ]]></script>




            <defs>
                <linearGradient spreadMethod='pad' id='slideBackgroundPaint' x1='0' y2='768' x2='1024' y1='0' gradientUnits='userSpaceOnUse'>
      <stop offset='0%' style='stop-color:black; stop-opacity:1;'/>
      <stop offset='100%' style='stop-color:rgb(103, 107, 157); stop-opacity:1;'/>
    </linearGradient>
    <linearGradient spreadMethod='pad' id='slideTitleSeparatorPaint' x1='0' y2='0' x2='1024' y1='0' gradientUnits='userSpaceOnUse'>
      <stop offset='0%' style='stop-color:rgb(23, 27, 77); stop-opacity:1;'/>
      <stop offset='.5' style='stop-color:rgb(103, 107, 157); stop-opacity:1;'/>
      <stop offset='100%' style='stop-color:rgb(23, 27, 77); stop-opacity:1;'/>
    </linearGradient>
    <linearGradient spreadMethod='pad' id='menuBarPaint' x1='0' y2='0' x2='210' y1='0' gradientUnits='userSpaceOnUse'>
      <stop offset='0%' style='stop-color:black; stop-opacity:1;'/>
      <stop offset='50%' style='stop-color:rgb(103, 107, 157); stop-opacity:1;'/>
      <stop offset='100%' style='stop-color:white; stop-opacity:1;'/>
    </linearGradient>
    <linearGradient spreadMethod='pad' id='slideBackgroundHeaderPaint' x1='0' y2='100' x2='0' y1='0' gradientUnits='userSpaceOnUse'>
      <stop offset='0%' style='stop-color:black; stop-opacity:1;'/>
      <stop offset='50%' style='stop-color:rgb(103, 107, 157); stop-opacity:1;'/>
      <stop offset='100%' style='stop-color:white; stop-opacity:1;'/>
    </linearGradient>
    <g id='stripePattern'>
      <g style='fill:black; fill-opacity:.25'>
        <rect height='2' width='1' y='0'/>
        <rect height='2' width='1' y='4'/>
        <rect height='2' width='1' y='8'/>
        <rect height='2' width='1' y='12'/>
        <rect height='2' width='1' y='16'/>
        <rect height='2' width='1' y='20'/>
        <rect height='2' width='1' y='24'/>
        <rect height='2' width='1' y='28'/>
        <rect height='2' width='1' y='32'/>
        <rect height='2' width='1' y='36'/>
        <rect height='2' width='1' y='40'/>
        <rect height='2' width='1' y='44'/>
        <rect height='2' width='1' y='48'/>
        <rect height='2' width='1' y='52'/>
        <rect height='2' width='1' y='56'/>
        <rect height='2' width='1' y='60'/>
        <rect height='2' width='1' y='64'/>
        <rect height='2' width='1' y='68'/>
        <rect height='2' width='1' y='72'/>
        <rect height='2' width='1' y='76'/>
        <rect height='2' width='1' y='80'/>
        <rect height='2' width='1' y='84'/>
        <rect height='2' width='1' y='88'/>
        <rect height='2' width='1' y='92'/>
        <rect height='2' width='1' y='96'/>
        <rect height='2' width='1' y='100'/>
        <rect height='2' width='1' y='104'/>
        <rect height='2' width='1' y='108'/>
        <rect height='2' width='1' y='112'/>
        <rect height='2' width='1' y='116'/>
        <rect height='2' width='1' y='120'/>
        <rect height='2' width='1' y='124'/>
        <rect height='2' width='1' y='128'/>
        <rect height='2' width='1' y='132'/>
        <rect height='2' width='1' y='136'/>
        <rect height='2' width='1' y='140'/>
        <rect height='2' width='1' y='144'/>
        <rect height='2' width='1' y='148'/>
        <rect height='2' width='1' y='152'/>
        <rect height='2' width='1' y='156'/>
        <rect height='2' width='1' y='160'/>
        <rect height='2' width='1' y='164'/>
        <rect height='2' width='1' y='168'/>
        <rect height='2' width='1' y='172'/>
        <rect height='2' width='1' y='176'/>
        <rect height='2' width='1' y='180'/>
        <rect height='2' width='1' y='184'/>
        <rect height='2' width='1' y='188'/>
        <rect height='2' width='1' y='192'/>
        <rect height='2' width='1' y='196'/>
        <rect height='2' width='1' y='200'/>
        <rect height='2' width='1' y='204'/>
        <rect height='2' width='1' y='208'/>
        <rect height='2' width='1' y='212'/>
        <rect height='2' width='1' y='216'/>
        <rect height='2' width='1' y='220'/>
        <rect height='2' width='1' y='224'/>
        <rect height='2' width='1' y='228'/>
        <rect height='2' width='1' y='232'/>
        <rect height='2' width='1' y='236'/>
        <rect height='2' width='1' y='240'/>
        <rect height='2' width='1' y='244'/>
        <rect height='2' width='1' y='248'/>
        <rect height='2' width='1' y='252'/>
        <rect height='2' width='1' y='256'/>
        <rect height='2' width='1' y='260'/>
        <rect height='2' width='1' y='264'/>
        <rect height='2' width='1' y='268'/>
        <rect height='2' width='1' y='272'/>
        <rect height='2' width='1' y='276'/>
        <rect height='2' width='1' y='280'/>
        <rect height='2' width='1' y='284'/>
        <rect height='2' width='1' y='288'/>
        <rect height='2' width='1' y='292'/>
        <rect height='2' width='1' y='296'/>
        <rect height='2' width='1' y='300'/>
        <rect height='2' width='1' y='304'/>
        <rect height='2' width='1' y='308'/>
        <rect height='2' width='1' y='312'/>
        <rect height='2' width='1' y='316'/>
        <rect height='2' width='1' y='320'/>
        <rect height='2' width='1' y='324'/>
        <rect height='2' width='1' y='328'/>
        <rect height='2' width='1' y='332'/>
        <rect height='2' width='1' y='336'/>
        <rect height='2' width='1' y='340'/>
        <rect height='2' width='1' y='344'/>
        <rect height='2' width='1' y='348'/>
        <rect height='2' width='1' y='352'/>
        <rect height='2' width='1' y='356'/>
        <rect height='2' width='1' y='360'/>
        <rect height='2' width='1' y='364'/>
        <rect height='2' width='1' y='368'/>
        <rect height='2' width='1' y='372'/>
        <rect height='2' width='1' y='376'/>
        <rect height='2' width='1' y='380'/>
        <rect height='2' width='1' y='384'/>
        <rect height='2' width='1' y='388'/>
        <rect height='2' width='1' y='392'/>
        <rect height='2' width='1' y='396'/>
        <rect height='2' width='1' y='400'/>
        <rect height='2' width='1' y='404'/>
        <rect height='2' width='1' y='408'/>
        <rect height='2' width='1' y='412'/>
        <rect height='2' width='1' y='416'/>
        <rect height='2' width='1' y='420'/>
        <rect height='2' width='1' y='424'/>
        <rect height='2' width='1' y='428'/>
        <rect height='2' width='1' y='432'/>
        <rect height='2' width='1' y='436'/>
        <rect height='2' width='1' y='440'/>
        <rect height='2' width='1' y='444'/>
        <rect height='2' width='1' y='448'/>
        <rect height='2' width='1' y='452'/>
        <rect height='2' width='1' y='456'/>
        <rect height='2' width='1' y='460'/>
        <rect height='2' width='1' y='464'/>
        <rect height='2' width='1' y='468'/>
        <rect height='2' width='1' y='472'/>
        <rect height='2' width='1' y='476'/>
        <rect height='2' width='1' y='480'/>
        <rect height='2' width='1' y='484'/>
        <rect height='2' width='1' y='488'/>
        <rect height='2' width='1' y='492'/>
        <rect height='2' width='1' y='496'/>
        <rect height='2' width='1' y='500'/>
        <rect height='2' width='1' y='504'/>
        <rect height='2' width='1' y='508'/>
        <rect height='2' width='1' y='512'/>
        <rect height='2' width='1' y='516'/>
        <rect height='2' width='1' y='520'/>
        <rect height='2' width='1' y='524'/>
        <rect height='2' width='1' y='528'/>
        <rect height='2' width='1' y='532'/>
        <rect height='2' width='1' y='536'/>
        <rect height='2' width='1' y='540'/>
        <rect height='2' width='1' y='544'/>
        <rect height='2' width='1' y='548'/>
        <rect height='2' width='1' y='552'/>
        <rect height='2' width='1' y='556'/>
        <rect height='2' width='1' y='560'/>
        <rect height='2' width='1' y='564'/>
        <rect height='2' width='1' y='568'/>
        <rect height='2' width='1' y='572'/>
        <rect height='2' width='1' y='576'/>
        <rect height='2' width='1' y='580'/>
        <rect height='2' width='1' y='584'/>
        <rect height='2' width='1' y='588'/>
        <rect height='2' width='1' y='592'/>
        <rect height='2' width='1' y='596'/>
        <rect height='2' width='1' y='600'/>
        <rect height='2' width='1' y='604'/>
        <rect height='2' width='1' y='608'/>
        <rect height='2' width='1' y='612'/>
        <rect height='2' width='1' y='616'/>
        <rect height='2' width='1' y='620'/>
        <rect height='2' width='1' y='624'/>
        <rect height='2' width='1' y='628'/>
        <rect height='2' width='1' y='632'/>
        <rect height='2' width='1' y='636'/>
        <rect height='2' width='1' y='640'/>
        <rect height='2' width='1' y='644'/>
        <rect height='2' width='1' y='648'/>
        <rect height='2' width='1' y='652'/>
        <rect height='2' width='1' y='656'/>
        <rect height='2' width='1' y='660'/>
        <rect height='2' width='1' y='664'/>
        <rect height='2' width='1' y='668'/>
        <rect height='2' width='1' y='672'/>
        <rect height='2' width='1' y='676'/>
        <rect height='2' width='1' y='680'/>
        <rect height='2' width='1' y='684'/>
        <rect height='2' width='1' y='688'/>
        <rect height='2' width='1' y='692'/>
        <rect height='2' width='1' y='696'/>
        <rect height='2' width='1' y='700'/>
        <rect height='2' width='1' y='704'/>
        <rect height='2' width='1' y='708'/>
        <rect height='2' width='1' y='712'/>
        <rect height='2' width='1' y='716'/>
        <rect height='2' width='1' y='720'/>
        <rect height='2' width='1' y='724'/>
        <rect height='2' width='1' y='728'/>
        <rect height='2' width='1' y='732'/>
        <rect height='2' width='1' y='736'/>
        <rect height='2' width='1' y='740'/>
        <rect height='2' width='1' y='744'/>
        <rect height='2' width='1' y='748'/>
        <rect height='2' width='1' y='752'/>
        <rect height='2' width='1' y='756'/>
        <rect height='2' width='1' y='760'/>
        <rect height='2' width='1' y='764'/>
        <rect height='2' width='1' y='768'/>
        <rect height='2' width='1' y='772'/>
        <rect height='2' width='1' y='776'/>
        <rect height='2' width='1' y='780'/>
        <rect height='2' width='1' y='784'/>
        <rect height='2' width='1' y='788'/>
        <rect height='2' width='1' y='792'/>
        <rect height='2' width='1' y='796'/>
      </g>
    </g>
    <g id='bullet' transform='translate(0, -20)'>
      <path style='stroke:white; stroke-width:2; fill:none' d='M0.436,1.418C7.853-1.088,16.396,1.706,19.52,7.658c2.498,4.762-0.287,10.248-6.22,12.252c-4.747,1.604-10.215-0.184-12.213-3.993c-1.599-3.048,0.183-6.559,3.981-7.842c3.038-1.026,6.538,0.118,7.816,2.556   c1.024,1.951-0.117,4.198-2.547,5.019c-1.945,0.657-4.185-0.076-5.003-1.636c-0.655-1.248,0.075-2.686,1.63-3.212c1.245-0.42,2.678,0.048,3.202,1.047'/>
    </g>
            </defs>




            <g id='slideBackground' class='slideBackground'>
    <rect height='768' style='fill:black' width='1024' x='0' y='0'/>
    <rect height='668' style='fill:url(#menuBarPaint)' width='210' x='0' y='100'/>
    <rect height='100' style='fill:url(#slideBackgroundHeaderPaint)' width='1024' x='0' y='0'/>
    <use xlink:href='#stripePattern' transform='scale(1024, 1)'/>
    <rect height='5' style='fill:url(#slideTitleSeparatorPaint)' width='1024' x='0' y='100'/>
  </g>





            <g id='navigationGroup' style='fill:white' transform='translate(984, 45) scale(2, 2)'>
    <polygon id='prevSlideControl' onclick='onPrevSlide(evt)' onmouseover="onSetFill(evt, 'prevSlideControl', 'rgb(176, 22, 40)')" points='1 10 10 0 1 -10 1 10' onmouseout="onSetFill(evt, 'prevSlideControl', 'white')" transform='rotate(180)'/>
    <polygon id='nextSlideControl' onclick='onNextSlide(evt)' onmouseover="onSetFill(evt, 'nextSlideControl', 'rgb(176, 22, 40)')" points='1 10 10 0 1 -10 1 10' onmouseout="onSetFill(evt, 'nextSlideControl', 'white')"/>
  </g>









            <g id='slideMenu' transform='translate(15, 130)'>
                <text onclick='onMenuItemSelected(evt, 1)' class='slidesetMenuHeader' x='0' y='0'>Background and Motivation</text>
    <g style='visibility:visible'>
      <rect height='5' id='Expand1' x='-10' y='-5' onclick="onExpand(evt, 'slideSetSubmenu1')" style='fill:white' width='5'/>
      <rect height='5' id='Collapse1' x='-10' y='-5' onclick="onCollapse(evt, 'slideSetSubmenu1')" style='fill:red; visibility:hidden' width='5'>
        <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='hidden' begin='Collapse1.click'/>
        <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='visible' begin='Expand1.click'/>
      </rect>
      <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='visible' begin='Collapse1.click'/>
      <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='hidden' begin='Expand1.click'/>
    </g>
    <g style='visibility:hidden' id='slideSetSubmenu1'>
      <text id='slide1-1MenuItem' x='10' y='20' onmouseout="onHighlightMenuItem(evt, 'false', 'slide1-1MenuItem')" onclick='onMenuItemSelected(evt, 2)' onmouseover="onHighlightMenuItem(evt, 'true', 'slide1-1MenuItem')" class='slideMenuItem'>Why Yet Another Grap...</text>
    </g>
    <g transform='translate(0, 20)'>
      <g>
        <text onclick='onMenuItemSelected(evt, 3)' class='slidesetMenuHeader' x='0' y='0'>The ABCs of SVG</text>
        <g style='visibility:visible'>
          <rect height='5' id='Expand2' x='-10' y='-5' onclick="onExpand(evt, 'slideSetSubmenu2')" style='fill:white' width='5'/>
          <rect height='5' id='Collapse2' x='-10' y='-5' onclick="onCollapse(evt, 'slideSetSubmenu2')" style='fill:red; visibility:hidden' width='5'>
            <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='hidden' begin='Collapse2.click'/>
            <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='visible' begin='Expand2.click'/>
          </rect>
          <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='visible' begin='Collapse2.click'/>
          <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='hidden' begin='Expand2.click'/>
        </g>
        <g style='visibility:hidden' id='slideSetSubmenu2'>
          <text id='slide2-1MenuItem' x='10' y='20' onmouseout="onHighlightMenuItem(evt, 'false', 'slide2-1MenuItem')" onclick='onMenuItemSelected(evt, 4)' onmouseover="onHighlightMenuItem(evt, 'true', 'slide2-1MenuItem')" class='slideMenuItem'>SVG Features</text>
          <text id='slide2-2MenuItem' x='10' y='40' onmouseout="onHighlightMenuItem(evt, 'false', 'slide2-2MenuItem')" onclick='onMenuItemSelected(evt, 5)' onmouseover="onHighlightMenuItem(evt, 'true', 'slide2-2MenuItem')" class='slideMenuItem'>SVG Sample Source</text>
          <text id='slide2-3MenuItem' x='10' y='60' onmouseout="onHighlightMenuItem(evt, 'false', 'slide2-3MenuItem')" onclick='onMenuItemSelected(evt, 6)' onmouseover="onHighlightMenuItem(evt, 'true', 'slide2-3MenuItem')" class='slideMenuItem'>SVG Sample Output</text>
        </g>
        <g transform='translate(0, 20)'>
          <g>
            <text onclick='onMenuItemSelected(evt, 7)' class='slidesetMenuHeader' x='0' y='0'>The SVG Community</text>
            <g style='visibility:visible'>
              <rect height='5' id='Expand3' x='-10' y='-5' onclick="onExpand(evt, 'slideSetSubmenu3')" style='fill:white' width='5'/>
              <rect height='5' id='Collapse3' x='-10' y='-5' onclick="onCollapse(evt, 'slideSetSubmenu3')" style='fill:red; visibility:hidden' width='5'>
                <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='hidden' begin='Collapse3.click'/>
                <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='visible' begin='Expand3.click'/>
              </rect>
              <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='visible' begin='Collapse3.click'/>
              <set fill='freeze' attributeType='CSS' attributeName='visibility' dur='0s' to='hidden' begin='Expand3.click'/>
            </g>
            <g style='visibility:hidden' id='slideSetSubmenu3'>
              <text id='slide3-1MenuItem' x='10' y='20' onmouseout="onHighlightMenuItem(evt, 'false', 'slide3-1MenuItem')" onclick='onMenuItemSelected(evt, 8)' onmouseover="onHighlightMenuItem(evt, 'true', 'slide3-1MenuItem')" class='slideMenuItem'>Some SVG Resources</text>
              <text id='slide3-2MenuItem' x='10' y='40' onmouseout="onHighlightMenuItem(evt, 'false', 'slide3-2MenuItem')" onclick='onMenuItemSelected(evt, 9)' onmouseover="onHighlightMenuItem(evt, 'true', 'slide3-2MenuItem')" class='slideMenuItem'>Quote Them on it</text>
            </g>
            <animateTransform fill='freeze' id='translator' type='translate' from='0, 0' dur='1s' accumulate='none' attributeName='transform' attributeType='XML' additive='replace' begin='Expand2.click' to='0, 60'/>
            <animateTransform fill='freeze' id='translator2' type='translate' from='0, 0' dur='1s' accumulate='sum' attributeName='transform' attributeType='XML' additive='sum' begin='Collapse2.click' to='0, -60'/>
          </g>
        </g>
        <animateTransform fill='freeze' id='translator' type='translate' from='0, 0' dur='1s' accumulate='none' attributeName='transform' attributeType='XML' additive='replace' begin='Expand1.click' to='0, 20'/>
        <animateTransform fill='freeze' id='translator2' type='translate' from='0, 0' dur='1s' accumulate='sum' attributeName='transform' attributeType='XML' additive='sum' begin='Collapse1.click' to='0, -20'/>
      </g>
    </g>
            </g>




            <g onclick='onNextSlide(evt)' style='visibility:hidden' id='slideShowCover'>
                <defs>
      <linearGradient spreadMethod='pad' id='backgroundPaint' x1='0' y2='768' x2='0' y1='0' gradientUnits='userSpaceOnUse'>
        <stop offset='0%' style='stop-color:black; stop-opacity:1;'/>
        <stop offset='25%' style='stop-color:rgb(103, 103, 157); stop-opacity:1;'/>
        <stop offset='50%' style='stop-color:white; stop-opacity:1;'/>
        <stop offset='75%' style='stop-color:rgb(103, 103, 157); stop-opacity:1;'/>
        <stop offset='100%' style='stop-color:black; stop-opacity:1;'/>
      </linearGradient>
      <filter height='105%' id='dropShadow' filterUnits='objectBoundingBox' x='0%' width='105%' y='0%'>
        <feGaussianBlur in='SourceAlpha' result='blur' stdDeviation='4'/>
        <feOffset dy='4' dx='4' result='offsetBlur' in='blur'/>
        <feFlood style='flood-color:black' result='solidBlack'/>
        <feComposite in='solidBlack' in2='SourceAlpha' result='separation' operator='in'/>
        <feOffset dy='-1' dx='-1' result='offsetSeparation' in='separation'/>
        <feMerge>
          <feMergeNode in='offsetBlur'/>
          <feMergeNode in='offsetSeparation'/>
          <feMergeNode in='SourceGraphic'/>
        </feMerge>
      </filter>
    </defs>
    <rect height='768' style='fill:url(#backgroundPaint)' width='1024'/>
    <use xlink:href='#stripePattern' transform='scale(1024, 1)'/>
    <g style='filter:url(#dropShadow)'>
      <text class='slideCoverTitle' style='text-anchor:middle' x='512' y='300'>Introduction to SVG</text>
      <g transform='translate(512, 490)' id='metadata' style='text-anchor:middle;'>
        <text x='0' class='slideCoverSubTitle' y='0'>Uche Ogbuji</text>
        <text x='0' class='slideCoverSubTitle' y='50'>Principal Consultant</text>
        <text x='0' class='slideCoverSubTitle' y='100'>Fourthought Inc.</text>
        <text x='0' class='slideCoverSubTitle' y='150'>Front Range XML Keiretsu</text>
      </g>
    </g>
            </g>





                <g onclick='onNextSlide(evt)' style='visibility:hidden' id='slidesetCover1'>
                    <rect height='768' style='fill:black' width='1024' x='0' y='0'/>
    <rect height='768' style='fill:url(#menuBarPaint)' width='210' x='0' y='0'/>
    <g transform='scale(210, 1)'>
      <use xlink:href='#stripePattern'/>
    </g>
    <text x='240' class='slidesetCoverTitle' y='200'>Background and Motivation</text>
                </g>

                <g onclick='onNextSlide(evt)' style='visibility:hidden' id='slidesetCover2'>
                    <rect height='768' style='fill:black' width='1024' x='0' y='0'/>
    <rect height='768' style='fill:url(#menuBarPaint)' width='210' x='0' y='0'/>
    <g transform='scale(210, 1)'>
      <use xlink:href='#stripePattern'/>
    </g>
    <text x='240' class='slidesetCoverTitle' y='200'>The ABCs of SVG</text>
                </g>

                <g onclick='onNextSlide(evt)' style='visibility:hidden' id='slidesetCover3'>
                    <rect height='768' style='fill:black' width='1024' x='0' y='0'/>
    <rect height='768' style='fill:url(#menuBarPaint)' width='210' x='0' y='0'/>
    <g transform='scale(210, 1)'>
      <use xlink:href='#stripePattern'/>
    </g>
    <text x='240' class='slidesetCoverTitle' y='200'>The SVG Community</text>
                </g>





            <g id='slide1-1' style='visibility:hidden' class='slide'>
    <text class='slideTitle' x='30' y='60'>Why Yet Another Graphics Format?</text>
    <g><text x="240" y="150" class="itemClass">Leveraging the existing XML technology base</text></g>
    <g><text x="240" y="185" class="itemClass">Integrating graphics into the semantic Web</text></g>
    <g><text x="240" y="220" class="itemClass">Giving browsers access to image <tspan class='emphasis'>internals</tspan></text></g>
    <g><text x="240" y="255" class="itemClass">Supporting the next generation of browsers</text></g>
  </g>
  <g id='slide2-1' style='visibility:hidden' class='slide'>
    <text class='slideTitle' x='30' y='60'>SVG Features</text>
    <text x='240' class='headingInline' y='150'>Basic Features</text>
    <use class='listBullet' xlink:href='#bullet' x='240' y='185'/>
    <g><text x="270" y="185" class="itemClass">Coordinate spaces and transforms</text></g>
    <use class='listBullet' xlink:href='#bullet' x='240' y='220'/>
    <g><text x="270" y="220" class="itemClass">Graphics primitives: ellipses, polygons, polylines, curves, etc.</text></g>
    <use class='listBullet' xlink:href='#bullet' x='240' y='255'/>
    <g><text x="270" y="255" class="itemClass">Stylesheets: CSS, XSL, etc.</text></g>
    <text x='240' class='headingInline' y='290'>Advanced Features</text>
    <use class='listBullet' xlink:href='#bullet' x='240' y='325'/>
    <g><text x="270" y="325" class="itemClass">Raster filter effects</text></g>
    <use class='listBullet' xlink:href='#bullet' x='240' y='360'/>
    <g><text x="270" y="360" class="itemClass">Alpha masking</text></g>
    <use class='listBullet' xlink:href='#bullet' x='240' y='395'/>
    <g><text x="270" y="395" class="itemClass">Animation</text></g>
    <use class='listBullet' xlink:href='#bullet' x='240' y='430'/>
    <g><text x="270" y="430" class="itemClass">Zooming and Panning</text></g>
    <use class='listBullet' xlink:href='#bullet' x='240' y='465'/>
    <g><text x="270" y="465" class="itemClass">Scripting and extensibility</text></g>
  </g>
  <g id='slide2-2' style='visibility:hidden' class='slide'>
    <text class='slideTitle' x='30' y='60'>SVG Sample Source</text>
    <text x='240' class='preformattedInline' y='135'>

&lt;?xml version="1.0"?>
&lt;!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20000802//EN"
 "http://www.w3.org/TR/2000/CR-SVG-20000802/DTD/svg-20000802.dtd"
>
&lt;svg width="800" height="800">
  &lt;desc>SVG Sample for SunWorld Article&lt;/desc>

  &lt;style type="text/css">
    .Lagos { fill: white; stroke: green; stroke-width: 30 }
    .ViaAppia { fill: none; stroke: black; stroke-width: 10 }
    .OrthoLogos { font-size: 32; font-family: helvetica }
  &lt;/style>

  &lt;ellipse transform="translate(500 200)" rx="250" ry="100"
           style="fill: brown; stroke: yellow; stroke-width: 10"/>

  &lt;polygon transform="translate(100 200) rotate(45)"
           class="Lagos"
           points="350,75 379,161 469,161 397,215 423,301 350,250 277,
                   301 303,215 231,161 321,161"/>

  &lt;text class="OrthoLogos" x="400" y="400">TO KALON&lt;/text>

  &lt;path class="ViaAppia" d="M500,600 C500,500 650,500 650,600
                            S800,700 800,600"/>
&lt;/svg>

        </text>
  </g>
  <g id='slide2-3' style='visibility:hidden' class='slide'>
    <text class='slideTitle' x='30' y='60'>SVG Sample Output</text>
    <g transform='translate(240, 135)'>
      <svg height='10cm' width='10cm' viewBox='0 0 200 200'>
  <desc>SVG Sample for SunWorld Article</desc>

  <style type='text/css'>
    .Lagos { fill: white; stroke: green; stroke-width: 30 }
    .ViaAppia { fill: none; stroke: white; stroke-width: 10 }
    .OrthoLogos { font-size: 32; font-family: helvetica; fill:white }
  </style>

  <ellipse transform='translate(500 200)' ry='100' rx='250' style='fill: brown; stroke: yellow; stroke-width: 10'/>

  <polygon points='350,75 379,161 469,161 397,215 423,301 350,250 277,                    301 303,215 231,161 321,161' transform='translate(100 200) rotate(45)' class='Lagos'/>

  <text class='OrthoLogos' x='400' y='400'>TO KALON</text>

  <path class='ViaAppia' d='M500,600 C500,500 650,500 650,600                             S800,700 800,600'/>
</svg>
    </g>
  </g>
  <g id='slide3-1' style='visibility:hidden' class='slide'>
    <text class='slideTitle' x='30' y='60'>Some SVG Resources</text>
    <g><text x="240" y="150" class="itemClass"><tspan class='linkStyle'>The W3C's SVG Page</tspan></text></g>
    <g><text x="240" y="185" class="itemClass"><tspan class='linkStyle'>OpenDirectory SVG Links</tspan></text></g>
    <g><text x="240" y="220" class="itemClass"><tspan class='linkStyle'>How to make slides like these</tspan></text></g>
  </g>
  <g id='slide3-2' style='visibility:hidden' class='slide'>
    <text class='slideTitle' x='30' y='60'>Quote Them on it</text>
    <text x='240' class='paraInline' y='150'>"Over twenty organizations, including Sun Microsystems, Adobe, Apple, IBM, and Kodak, have been involved in defining SVG."<tspan class='emphasis'> -- Vincent J. Hardy, Sun</tspan>
    </text>
    <text x='240' class='paraInline' y='185'>"I have been working with computer graphics for
over 25 years and split an immense amount of blood on the floor at
midnight. With SVG I can now do almost anything I want [except for 3D - in
which I also have a molecular interest]. And I suspect that I can stick
with it for the foreseeable future." <tspan class='emphasis'>-- Peter Murray-Rust, XML-DEV Founder</tspan>
    </text>
    <text x='240' class='paraInline' y='220'>"I envision a day where we have XHTML Web pages with SVG as the "chrome" of our interfaces--defining the buttons, the layers, the coloring, and the grid--where we can actually use a language that's XML-based rather than theses separate GIF files that can take so long to download. That's certainly one vision; that vision not just extending on the Web, on a monitor, but wireless onto my Palm Pilot or to print and other output as well." <tspan class='emphasis'>-- Steve Mulder, Razorfish</tspan>
    </text>
  </g>

        </svg>"""

#"'

expected_1="""
<svg/>"""

def Test(tester):
    tester.startTest("Checking for SVG stylesheets")
    try:
        import urllib
        for uri in (sheet_1_uri, sheet_2_uri, sheet_3_uri):
            fd = urllib.urlopen(uri)
            fd.close()
        tester.testDone()
    except (IOError, OSError):
        tester.warning(
            "You must have 'svgslides.xsl', 'svgslides_custom.xsl' and\n"
            "'slidescript.xsl' from Sun's SVG toolkit to run this test.\n"
            "See http://www.sun.com/software/xml/developers/svg-slidetoolkit/\n"
            "or ftp://ftp.fourthought.com/pub/third-party/test-material/\n"
            "It's enough to copy *.xsl from that package to the\n"
            "'%s' directory." % os.path.dirname(__file__))
        tester.testDone()
    else:
        source = test_harness.FileInfo(uri=source_1_uri)
        sheet = test_harness.FileInfo(uri=sheet_1_uri)
        test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
