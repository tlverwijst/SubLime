# SubLime #
A subtitle cleaning service for Kodi

Current version: 1.6

Licensed under the [GNU General Public License, version 2](http://www.gnu.org/licenses/gpl-2.0.html "http://www.gnu.org/licenses/gpl-2.0.html")

## Description ##
So you got your Kodi entertainment center set up, probably one or more media downloaders like CouchPotato or Flexget that will also automatically get subtitles, or maybe you use Subliminal for this. Maximum enjoyment with minium effort, right? Well, not always.

Subtitles come in a lot of formats and markups, using  captions for the hearing impaired,  forced font colors,ALL CAPS and noawadays some even got advertisements in them. Not all of these are equally bad, but they can be annoying. And sometimes, there just isn't a clean sub available.

SubLime lets you choose which markup you want to keep, and which you want to filter out.


## Installation ##


- Select a file from the [releases page](https://github.com/tlverwijst/SubLime/releases "https://github.com/tlverwijst/SubLime/releases"),
- Install from zip:[How To..](http://kodi.wiki/view/How_to_install_an_Add-on_from_a_zip_file "http://kodi.wiki/view/How_to_install_an_Add-on_from_a_zip_file")

## Features ##

 - Automatically looks for uncleaned subs on playback start
 - Automatically start cleaning process when playback starts *
 - Automatically save a backup of the original file *
 - Remove Hearing Impaired (HI) tags *
 - Remove line prefixes (dashes & text before colon) *
 - Remove font tags 
 - Remove some advertising lines (adjustable via textfile)
 
> \* can be toggled via the settings menu

## Settings ##

**General**

- **Start cleaning automatically** [true]:Don't wait for user confirmation
- **Only clean subs for current video** [true]: When set to false, Sublime will look for all subs in the folder
- **Back up original file** [true]: Save a copy of the subtitle before cleaning

**Filters**

- **Text in square braces** [true]: `eg [Door closes]`
- **Text in parenthesis** [true]: `eg (Door closes)`
- **Text in music symbols** [true]: `eg ♪ La la la la ♪`
- **Line starts with dash** [true]: Remove dashes from the front of the line. `eg -Let's go`
- **Prefixed with colon** [true]: Clean texts from the beginning of the line prefixed with a colon. `eg Policeofficer: Please step back!`
	- **Only if all caps** [true]: Only clean text prefixed with a colon, when the entire prefix text is in capitals `eg POLICEOFFICER: Please step back!`

**Debug**

- **Debugging on** [false]: Running SubLime in debug mode will leave the replacement marker `(=*=*=*=)` in the file after cleaning, so you can see where one or more elements got replaced. Once debug mode is disabled, the replacement markers will also be removed (upon next playback). 

 
##Supported subtitle formats:##
 
Currently only the SubRip (.srt) format is supported.*


> \* More text based formats are planned for a future release 


## Compatibility ##
Tested on:

- v13.1 (Gotham) - Windows 8.1 & RaspBMC 
- v14 (Helix 24/12) - RaspBMC



## Known Issues ##

See the wiki: [https://github.com/tlverwijst/SubLime/wiki/Known-Issues](https://github.com/tlverwijst/SubLime/wiki/Known-Issues "https://github.com/tlverwijst/SubLime/wiki/Known-Issues")