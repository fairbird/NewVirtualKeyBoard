import os
from enigma import addFont
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import *
try:
	FONTSSIZE = config.NewVirtualKeyBoard.fontssize.value
except:
	FONTSSIZE = 0

FONT0 = FONTSSIZE + 24
FONT1 = FONTSSIZE + 14
FONT2 = FONTSSIZE + 18
FONT3 = FONTSSIZE + 1
FONT4 = FONTSSIZE + 10

#<?xml version="1.0" encoding="UTF-8"?>
#<skin>
Skin_NewVirtualKeyBoard = '''
    <screen name="NewVirtualKeyBoard" position="center,317" size="1280,420" title="E2iStream virtual keyboard" backgroundColor="#34000000" flags="wfNoBorder">
        
        <eLabel position="300,14" size="680,48" backgroundColor="#3f434f" transparent="0"/>
        
        <!-- title -->
        <widget name="header" zPosition="2" position="314,14" size="650,48" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#3f434f" transparent="1" noWrap="1" valign="center" halign="center" />
        
        <!-- text input-->
        <widget name="0" position="320,76" size="685,46" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="text" position="325,80" size="630,40" font="Regular;{0}" noWrap="1" valign="center" halign="right" transparent="1" zPosition="2" />

        <!-- select highlights -->
        <widget name="vkey_text_sel" position="0,0" size="685,46" alphatest="blend" transparent="1" zPosition="5" />
        <widget name="vkey_text_sel" position="0,0" size="1020,46" alphatest="blend" transparent="1" zPosition="5" />
        <widget name="vkey_single_sel" position="0,0" size="45,45" alphatest="blend" transparent="1"  zPosition="5" />
        <widget name="vkey_double_sel" position="0,0" size="93,46" alphatest="blend" transparent="1" zPosition="5" />
        <widget name="vkey_space_sel" position="0,0" size="373,46" alphatest="blend" transparent="1" zPosition="5" />
        
        <!-- keyboard -->
        <widget name="1" position="300,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_1" position="300,138" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="2" position="345,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_2" position="345,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        

        <widget name="3" position="390,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_3" position="390,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="4" position="435,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_4" position="435,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="5" position="480,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_5" position="480,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="6" position="525,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_6" position="525,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="7" position="570,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_7" position="570,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="8" position="615,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_8" position="615,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        

        <widget name="9" position="660,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_9" position="660,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="10" position="705,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_10" position="705,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="11" position="750,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_11" position="750,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="12" position="795,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_12" position="795,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
                
        <widget name="13" position="840,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_13" position="840,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
  
        <widget name="14" position="885,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_14" position="885,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
  
        <widget name="15" position="930,138" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_15" position="930,138" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
       <widget name="vkey_backspace" position="930,138" size="45,45" alphatest="blend" transparent="1" zPosition="3" /> 
        
        <!-- backspace red bar -->
        <widget name="m_0" position="936,175" size="33,2" font="Regular;{3}" foregroundColor="#ed1c24" backgroundColor="#ed1c24" noWrap="1" valign="center" halign="center" zPosition="2" />   
        
        <!-- row 2 -->
        <widget name="16" position="300,183" size="90,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_16" position="300,183" size="90,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="17" position="390,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_17" position="390,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="18" position="435,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_18" position="435,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="19" position="480,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_19" position="480,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="20" position="525,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_20" position="525,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="21" position="570,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_21" position="570,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="22" position="615,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_22" position="615,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        

        <widget name="23" position="660,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_23" position="660,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="24" position="705,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_24" position="705,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="25" position="750,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_25" position="750,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="26" position="795,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_26" position="795,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
                
        <widget name="27" position="840,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_27" position="840,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
  
        <widget name="28" position="885,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_28" position="885,183" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
  
        <widget name="29" position="930,183" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_29" position="930,183" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="vkey_delete" position="934,183" size="45,45" alphatest="blend" transparent="1" zPosition="3" /> 
        
        <!-- row 3 -->
        <widget name="30" position="300,228" size="90,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_30" position="300,228" size="90,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="31" position="390,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_31" position="390,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="32" position="435,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_32" position="435,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="33" position="480,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_33" position="480,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="34" position="525,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_34" position="525,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="35" position="570,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_35" position="570,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="36" position="615,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_36" position="615,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        

        <widget name="37" position="660,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_37" position="660,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="38" position="705,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_38" position="705,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="39" position="750,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_39" position="750,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="40" position="795,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_40" position="795,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
                
        <widget name="41" position="840,228" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_41" position="840,228" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
  
        <widget name="42" position="885,228" size="90,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_42" position="885,228" size="90,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
  
        <!-- enter green bar -->
        <widget name="m_1" position="891,266" size="78,2" font="Regular;{3}" foregroundColor="#22b14c" backgroundColor="#22b14c"   noWrap="1"  valign="center" halign="center" zPosition="2"/>  
        
        <!-- row 4 -->
        <widget name="43" position="300,273" size="90,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_43" position="300,273" size="90,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="44" position="390,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_44" position="390,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="45" position="435,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_45" position="435,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="46" position="480,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_46" position="480,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="47" position="525,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_47" position="525,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="48" position="570,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_48" position="570,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
        
        <widget name="49" position="615,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_49" position="615,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        

        <widget name="50" position="660,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_50" position="660,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="51" position="705,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_51" position="705,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="52" position="750,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_52" position="750,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />      
        
        <widget name="53" position="795,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_53" position="795,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
                
        <widget name="54" position="840,273" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_54" position="840,273" size="45,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
  
        <widget name="55" position="885,273" size="90,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_55" position="885,273" size="90,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
         
        <!-- row 5 -->
        <widget name="vkey_country" position="345,319" size="45,45" transparent="1" alphatest="blend"  zPosition="1" />
        
        <widget name="56" position="300,318" size="90,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_56" position="345,318" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />
    
        <widget name="flag" position="307,327" size="40,26" transparent="1" zPosition="2"/>
        
        <!-- country yellow bar -->
        <widget name="m_2" position="306,356" size="78,2" font="Regular;{3}" foregroundColor="#fff200" backgroundColor="#fff200"   noWrap="1"  valign="center" halign="center" zPosition="2"/>  
   
        <widget name="57" position="390,318" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_57" position="390,318" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />       

        <widget name="58" position="435,318" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_58" position="435,318" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <!-- space bar -->
        <widget name="59" position="480,318" size="362,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_59" position="480,318" size="362,45" font="Regular;{2}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="60" position="840,318" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_60" position="840,318" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="61" position="885,318" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_61" position="885,318" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="vkey_left" position="885,318" size="45,45" alphatest="blend" transparent="1" zPosition="3" /> 
          
        <widget name="62" position="930,318" size="45,45" alphatest="blend" transparent="1" zPosition="1" />
        <widget name="_62" position="930,318" size="45,45" font="Regular;{1}" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />        
  
        <widget name="vkey_right" position="930,318" size="45,45" alphatest="blend" transparent="1" zPosition="3" /> 
        <!-- info button -->
        <ePixmap position="922,364" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard/skins/icons/nvk/key_info.png" alphatest="blend" zPosition="3" />

        <!-- menu button -->
        <ePixmap position="954,364" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard/skins/icons/nvk/key_menu.png" alphatest="blend" zPosition="3" />
       
        <widget name="historyheader" position="60,14" size="226,48" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#3f434f" noWrap="1" valign="center" halign="center"  transparent="0" zPosition="2" />
        <widget name="historyList" position="60,76" size="226,286" backgroundColor="#3f434f" enableWrapAround="1" scrollbarMode="showOnDemand" transparent="0" zPosition="2" />
          
        <widget name="suggestionheader" position="994,14" size="226,48" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#3f434f"  noWrap="1" valign="center" halign="center" transparent="0" zPosition="2" />
        <widget name="suggestionList" position="994,76" size="226,286" backgroundColor="#3f434f" enableWrapAround="1" scrollbarMode="showOnDemand" transparent="0" zPosition="1" />
       
        <eLabel position="300,364" size="588,25" font="Regular;{4}" text="New Virtual Keyboard - Original SamSamSam (e2iplayer). Contributors: mfaraj57 (tsmedia) and Fairbird, madmax88 (linuxsat-support). Skin: KiddaC" 
        foregroundColor="#ffffff" backgroundColor="#000000" valign="center" transparent="1" />
    </screen>'''.format(FONT0, FONT1, FONT2, FONT3, FONT4)

Skin_LanguageListScreen =  '''
    <screen name="LanguageListScreen" position="center,center" size="600,506" backgroundColor="#16000000" transparent="0" title="Select Language">
        <widget name="languageList" position="0,0" size="600,466" backgroundColor="#3f4450" transparent="0" scrollbarMode="showOnDemand" />
        <widget name="info" zPosition="2" position="center,473" size="600,26" transparent="0" noWrap="1" font="Regular;20" valign="center" halign="center" foregroundColor="#ffffff" backgroundColor="#0f64b2" />
    </screen>'''

Skin_vkOptionsScreen =  '''
    <screen name="vkOptionsScreen" position="center,center" size="600,480" backgroundColor="#16000000" transparent="0" title="Addkey">
        <widget name="menu" position="3,3" size="600,480" backgroundColor="#3f4450" transparent="0" />
    </screen>'''    
#</skin>
