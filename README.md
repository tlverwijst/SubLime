# SubLime #
A subtitle cleaning service for Kodi (formerly known as XBMC)

Current version: 1.5

Licensed under the [GNU General Public License, version 2](http://www.gnu.org/licenses/gpl-2.0.html "http://www.gnu.org/licenses/gpl-2.0.html")

## Description ##
So you got your Kodi entertainment center set up, probably one or more media downloaders like CouchPotato or Flexget that will also automatically get subtitles, or maybe you use Subliminal for this. Maximum enjoyment with minium effort, right? Well, not always.

Subtitles come in a lot of formats and markups, using  captions for the hearing impaired,  forced font colors,ALL CAPS and noawadays some even got advertisements* in them. Not all of these are equally bad, but they can be annoying. And sometimes, there just isn't a clean sub available.

SubLime lets you choose which markup you want to keep, and which you want to filter out.

> \* Even though in some cases you can avoid these with a paid subscription or donation (and you should!), this doesn't work with all providers / subtitle grabbers.


## Installation ##


- Select a file from the [releases page](https://github.com/tlverwijst/SubLime/releases "https://github.com/tlverwijst/SubLime/releases"),
- Install from zip:[How To..](http://kodi.wiki/view/How_to_install_an_Add-on_from_a_zip_file "http://kodi.wiki/view/How_to_install_an_Add-on_from_a_zip_file")


## Features ##

 - Automatically looks for uncleaned subs on playback start
 - Automatically start cleaning process when playback starts *
 - Automatically save a backup of the original file *
 - Remove Hearing Impaired (HI) tags *
 - Remove Line prefixes (dashes & text before colon) *
 - Remove font tags 
 - Remove some advertising lines for files from opensubtitles.org
 
> \* can be toggled via the settings menu

## Settings ##

**General**

- **Start cleaning automatically** [true]:Don't wait for user confirmation
- **Back up original file** [true]: Save a copy of the subtitle before cleaning

**Filters**

- **Text in square brackets** [true]: `eg [Door closes]`
- **Text in parenthesis** [true]: `eg (Door closes)`
- **Line starts with dash** [true]: Remove dashes from the front of the line. `eg -Let's go`
- **Prefixed with colon** [true]: Clean texts from the beginning of the line prefixed with a colon. `eg Policeofficer: Please step back!`
	- **Only if all caps** [true]: Only clean text prefixed with a colon, when the entire prefix text is in capitals `eg POLICEOFFICER: Please step back!`

**Debug**

- **Debugging on** [false]: Running SubLime in debug mode will leave the replacement marker `(=*=*=*=)` in the file after cleaning, so you can see where one or more elements got replaced. Once debug mode is disabled, the replacement markers will also be removed (upon next playback). 

 
##Supported subtitle formats:##
 
Currently only the SubRip (.srt) format is supported.*


> \* More text based formats are planned for a future release 


## Compatibility ##
Tested on Gotham 13.1 (Windows 8.1 & RaspBMC )


## Known Issues ##

- Dash- and colon filters dont work when line is inside a  markup tag  
`eg <i>-Let's go </i>, <font>Policeofficer: Please step back!</font>`
- Processes all (unprocessed) subtitles in folder, even if current video doesn't has a subtitle (option for only current playing video coming in future release)
- Only looks for subtitles in same folder as playing video
- Doesn't wait for other addons (support for [AutoSubs](http://kodi.wiki/view/Add-on:AutoSubs "http://kodi.wiki/view/Add-on:AutoSubs") and [Check Previous Episode](http://kodi.wiki/view/Add-on:XBMC_Check_Previous_Episode "http://kodi.wiki/view/Add-on:XBMC_Check_Previous_Episode") addons are planned for future releases)
- No option for manual start (planned for future release)
