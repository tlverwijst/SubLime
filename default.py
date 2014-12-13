#!/usr/bin/python

"""
Sublime for Kodi
Author: Tommie82
"""

import os
import re
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')

################
# PATHS
__cwd__         = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__resource__    = os.path.join(__cwd__, 'resources')
__data__        = os.path.join(__resource__, 'data')

supported = ['.srt']

################
# REGEX

#including start & end in different lines
paren = re.compile('(\((.+)?\)|\((.+)?|^(.+)?\))')
brace = re.compile('(\[(.+)?\]|\[(.+)?|^(.+)?\])')

# interpunction -> non alphanumeric leftovers
punct = re.compile('^[\W]+$')

# tags
font_tags = re.compile('(<font[^>]*>)|(<\/font>)')

#specials
colon_prefix = re.compile('^[=\*=\*=\*=[\s]*]*[A-z]+[A-z0-9\s]*:[\s]*') #starting with any word and colon
colon_prefix_capped = re.compile('^[=\*=\*=\*=[\s]*]*[A-Z]+[A-Z0-9\s]*:[\s]*') #starting with capitalized word and colon
dash_start  = re.compile('^[\-]+[\s]*') #lines starting with a dash (-)

replace_tag = re.compile('=\*=\*=\*=[\s]*')

#global functions
def log(msg):
    try:
        message = '%s: %s' % (__addonname__, str(msg) )
    except UnicodeEncodeError:
        message = '%s: %s' % (__addonname__, str(msg.encode('utf-8', 'ignore')) )

    print message

def notify(msg):
    dialog = xbmcgui.Dialog()
    dialog.notification(__addonname__, str(msg) , xbmcgui.NOTIFICATION_INFO, 5000)

def confirm(line1, line2="", line3=""):
    dialog = xbmcgui.Dialog()
    return dialog.yesno(__addonname__, str(line1), str(line2), str(line3))

# class start
class Sublime(xbmc.Player):

    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.init_properties()

    def getSetting(self, setting, boolean=False):

        if boolean == True:
            return __addon__.getSetting(setting) == 'true'
        else:
            return __addon__.getSetting(setting)

    def init_properties(self):
        self.debug          = self.getSetting("debug",True)
        self.__replace__    = "=*=*=*="

        # general
        if self.debug == True:
            self.sublime_extension   = ".sublime.debug"
            self.keep_source         = True
        else:
            self.sublime_extension   = ".sublime.original"
            self.keep_source         = self.getSetting("keep_source",True)

        self.show_notifications = self.getSetting("show_notifications",True)
        self.auto_start         = self.getSetting("auto_start",True)

        # filter settings
        self.flt_brace      = self.getSetting("flt_brace",True)
        self.flt_paren      = self.getSetting("flt_paren",True)
        self.flt_dash       = self.getSetting("flt_dash_pr",True)
        self.flt_colon_pr   = self.getSetting("flt_colon_pr",True)
        self.flt_colon_capped_pr = self.getSetting("flt_colon_capped_pr",True)

        self.flt_font_tags  = True
        self.wait = False

        self.externalAddons = []
        if xbmc.getCondVisibility('System.HasAddon(service.autosubs)'):
            self.externalAddons.append('autosubs')
        if xbmc.getCondVisibility('System.HasAddon(script.service.checkpreviousepisode)'):
            self.externalAddons.append('checkpreviousepisode')

        # get blacklist file
        f = xbmcvfs.File(os.path.join(__data__,'blacklist.txt'))
        b = f.read()
        f.close()
        self.blacklist = b.split('\n')

    def cleanReplacedTags(self, line):
        try:
            line = re.sub(replace_tag,'', line)
        except:
            pass
        return line

    def simpleClean(self, line, regex):
        try:
            line = re.sub(regex, self.__replace__, line)
        except:
            pass
        return line

    def cleanBlacklisted(self, line):

        for x in self.blacklist:
            bl = x.strip()
            if bl in line.strip():
                log("found blacklisted item")
                line = re.sub(bl, self.__replace__, line)

        return line

    def getPercentage(self, num, total_files, current_count):

        max_p = float(current_count)/total_files * 100

        try:
            offset = float(current_count-1)/total_files * 100
        except:
            offset = 0

        percentage = offset +  float(num)/100 * (max_p-offset)

        return int(percentage)

    def findSubs(self, path):

        count = 0
        sub_files = []

        log('Checking for subs in ' + path);

        # get all the files in the path
        file_list = xbmcvfs.listdir(path)[1]

        for f in file_list:

            full_file_path = os.path.join(path,f)

            # is this file a suppported subtitle
            if os.path.splitext(f)[1] in supported:

                #is there a debug file and debug mode is enabled?
                if self.debug == True:
                    # is there a backup file?
                    debug_check = xbmcvfs.exists( full_file_path +'.sublime.debug')
                else:
                    debug_check = False

                backup_file = xbmcvfs.exists( full_file_path  +'.sublime.original') #+ self.sublime_extension)
                # ignore this file?
                ignore_file = xbmcvfs.exists(full_file_path+'.sublime.ignore')

                if not backup_file and not debug_check and not ignore_file:
                    count = count+1
                    sub_files.append( f )
                    log("Found unprocessed subtitle:" + str(full_file_path) )

        return {'count': count, 'files':sub_files}

    def clean(self, __original_file__,__path__, total_files=1, current_count=1):

        progressDialog = xbmcgui.DialogProgress()
        progressDialog.create(__addonname__, "Cleaning file "+ str(current_count)+" of "+str(total_files), __original_file__ )

        # empty list for cleaned lined
        cleanlines = []

        progress = 0
        nr = 0

        # set full path for file
        full_file_path = os.path.join(__path__,__original_file__)

        # open file and load into buffer
        f = xbmcvfs.File(full_file_path)
        b = f.read()
        f.close()

        # split lines into list
        data = b.split('\n')

        # number of lines in the file
        total_lines = len(data)

        # loop through lines
        for line in data:

            if progressDialog.iscanceled():
                log("Cancelled by user")
                return False

            #  strip outer whitespace characters
            line = line.strip()

            nr=nr+1

            dirty = True
            if dirty == True:

                if self.flt_paren == True:
                    line = self.simpleClean(line, paren)
                if self.flt_brace == True:
                    line = self.simpleClean(line, brace)
                if self.flt_dash == True:
                    line = self.simpleClean(line, dash_start)

                if self.flt_colon_pr == True:
                    if self.flt_colon_capped_pr == True:
                        line = self.simpleClean(line, colon_prefix_capped)
                    else:
                        line = self.simpleClean(line, colon_prefix)

                line = self.simpleClean(line, font_tags)
                line = self.cleanBlacklisted(line)

                # if the line is empty here, it means it was always empty, so just add it
                if len(line)==0:
                    cleanlines.append(line+'\n')

                # remove leftover particles (., etc)
                line = self.simpleClean(line, punct)

                # clean replacement tags if we 're not in debug mode
                if self.debug == False:
                    line = self.cleanReplacedTags(line)

            # add line if is not empty
            if len(line)>0:
                # add line to cleanlines list
                cleanlines.append(line+'\n')

            progress = progress+1
            percentage = (float(progress)/total_lines)*90
            progressDialog.update(self.getPercentage(percentage, total_files, current_count))

        # time to write the new file
        # remove the tempfile if it exists (from a failed rename maybe) otherwise the new content just gets append to it

        __temp_file__       = os.path.join(__path__, 'cleaned.tmp');

        if xbmcvfs.exists(__temp_file__):
            log("temp file exists, removing")
            xbmcvfs.delete(__temp_file__)

        progressDialog.update(self.getPercentage(92, total_files, current_count), "Creating temp file...")

        f = xbmcvfs.File(__temp_file__, 'w')

        progressDialog.update(self.getPercentage(93, total_files, current_count), "Writing to temp file...")

        # write clean list to temp file first just to be safe, and then close it
        f.write(''.join(cleanlines))
        f.close()

        log('original exists?')
        log(xbmcvfs.exists(full_file_path+self.sublime_extension))

        if self.keep_source == True:
            if self.debug == False and xbmcvfs.exists(full_file_path+'.sublime.debug') == True:
                log('renaming .debug-file to '+ self.sublime_extension + '-file')
                xbmcvfs.rename(full_file_path+'.sublime.debug',full_file_path+self.sublime_extension);

                log("Removing original file")
                xbmcvfs.delete(full_file_path)
            elif xbmcvfs.exists(full_file_path+self.sublime_extension) == True:
                # remove the original file
                log("backup exists, skipping backup...")
                log("removing original file")
                xbmcvfs.delete(full_file_path)
            else:
                progressDialog.update(self.getPercentage(96, total_files, current_count), "Backing up original file...")
                # rename the original file [filename].srt.bak
                log("Renaming original file")
                xbmcvfs.rename(full_file_path,full_file_path+self.sublime_extension);
        else:
            log('Not backing up file')
            # remove the original file
            log("Removing orginal file")
            xbmcvfs.delete(full_file_path)
            if xbmcvfs.exists(full_file_path+'.sublime.debug') == True:
                log("Removing debug file")
                xbmcvfs.delete(full_file_path+'.sublime.debug')
            # open file and load into buffer
            f = xbmcvfs.File(full_file_path+'.sublime.ignore','w')
            f.close()

        # rename tempfile to original filename
        progressDialog.update(self.getPercentage(98, total_files, current_count), "Writing new file...")
        xbmcvfs.rename(__temp_file__, full_file_path);

        if current_count==total_files:
            progressDialog.update(self.getPercentage(100, total_files, current_count), "Done")
            xbmc.sleep(500)

        return True

    def onPlayBackResumed(self):
        self.wait = False

    def onPlayBackStopped(self):
        self.wait = False

    def onPlayBackEnded(self):
        self.wait = False

    def onPlayBackStarted(self):
        self.init_properties()

        if len(self.externalAddons) > 0:
            log('Found conflicting addons:' + str(self.externalAddons))
            xbmc.sleep(2500)

            # addons like autosubs or check_previous_episode will pause the player
            if xbmc.getCondVisibility('Player.Paused') == True:
                log("Will wait for playback to continue")
                self.wait = True

        # sleep until playback resumes
        while self.wait == True:
            xbmc.sleep(500)

        #get file being played
        playing = xbmc.Player().getPlayingFile()
        xbmc.sleep(1000)
        path = os.path.split(playing)[0]

        subsFound = self.findSubs(path)
        sub_file_count = subsFound['count']

        if sub_file_count >0:

            log('pausing playback')
            #pause playback
            if self.wait == False:
                xbmc.Player().pause()

            if self.auto_start == True:
                confirmed = True
                log("Auto clean is enabled")
            else:
                confirmed = confirm("%s Subtitles found " % (sub_file_count), "Do you want to clean them now?")

            if confirmed == True:
                files_to_process = sub_file_count
                count = 0
                for f in subsFound['files']:
                    count = count+1

                    if os.path.splitext(f)[1] in supported:
                        log("start cleaning file %s of %s \n: %s" % ( count, sub_file_count, f ) )
                        cleaning = self.clean(f, path, files_to_process, count)
                        sub_file_count = sub_file_count - count

                        if cleaning == False:
                            xbmc.Player().pause()
                            log("User cancelled during cleaning of files")
                            return

                # stop & start player to refresh the subtitle stream
                log("Resuming" + str(playing))
                full_file_path = os.path.join(path,f)
                self.disableSubtitles()
                self.setSubtitles(full_file_path)
                # jump back to start
                xbmc.Player().seekTime(0)
                xbmc.Player().pause()

            else:
                log("User denied cleaning of files")
                if self.wait == False:
                    xbmc.Player().pause()

        else:
            log("Nothing to do")

monitor = Sublime()

log("Loading '%s' version '%s'" % (__addonname__, __addonversion__))

while not xbmc.abortRequested:
    xbmc.sleep(1000)

del monitor