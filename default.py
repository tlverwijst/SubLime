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

sublime_extension = 'original'
supported = ['.srt']

################
# REGEX

#including start & end in different lines
paren_m = re.compile('(\((.+)?\)|\((.+)?|^(.+)?\))')
brace_m = re.compile('(\[(.+)?\]|\[(.+)?|^(.+)?\])')

# interpunction -> non alphanumeric leftovers
punct = re.compile('^[\W]+$')

# tags
font_tags = re.compile('(<font[^>]*>)|(<\/font>)')


#specials
capital_start = re.compile('^[A-Z]*[\s]*:[\s]*') #starting with capitalized word and colon
dash_start  = re.compile('^[\-]+[\s]*') #lines starting with a dash (-)

replace_tag = re.compile('=\*=\*=\*=[\s]*')

#global functions
def log(msg):
    try:
        message = '%s: %s' % (__addonname__, str(msg) )
    except UnicodeEncodeError:
        message = '%s: %s' % (__addonname__, str(msg.encode('utf-8', 'ignore')) )

    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

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


    def init_properties(self):
        self.debug = __addon__.getSetting("debug") == 'true'
        self.show_notifications = __addon__.getSetting("show_notifications") == 'true'
        self.keep_source    = True
        self.autoclean      = False
        self.__replace__    = "=*=*=*="

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
            bl = "%s" % (x.strip())
            if bl in line.strip():
                log("found blacklist item")
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


        # get the path of the playing file
        log('checking for subs in ' + path);

        # get all the files in the path
        file_list = xbmcvfs.listdir(path)[1]

        for f in file_list:
            full_file_path = os.path.join(path,f)

            # check if any of them are supported subtitle files
            if os.path.splitext(f)[1] in supported:

                # if so, is there a already a backup file present?
                if xbmcvfs.exists( full_file_path +'.'+sublime_extension ) == False:
                    count = count+1
                    sub_files.append( f )
                    log("found unprocessed subtitle:" + str(full_file_path) )

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

                line = self.simpleClean(line, paren_m)
                line = self.simpleClean(line, brace_m)
                line = self.simpleClean(line, capital_start)
                line = self.simpleClean(line, dash_start)
                line = self.simpleClean(line, font_tags)

                line = self.cleanBlacklisted(line)

                # if the line is empty here, it means it was always empty, so just add it
                if len(line)==0:
                    # print 'adding empty line'
                    cleanlines.append(line+'\n')

                # remove leftover particles (., etc)
                line = self.simpleClean(line, punct)

                # clean replacement tags if we 're not in debug mode
                if self.debug == False:
                    log('removing debug tags')
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
        log(xbmcvfs.exists(full_file_path+'.original'))

        if self.keep_source == True:

            if xbmcvfs.exists(full_file_path+'.original') == True:
                # remove the original file
                log("backup exists, skipping backup...")
                log("removing original file")
                xbmcvfs.delete(full_file_path)
            else:
                progressDialog.update(self.getPercentage(96, total_files, current_count), "Backing up original file...")
                # rename the original file [filename].srt.bak
                print "rename original file"
                xbmcvfs.rename(full_file_path,full_file_path+'.original');
        else:

            # remove the original file
            log("removing orginal file")
            xbmcvfs.delete(full_file_path)

        # rename tempfile to original filename
        progressDialog.update(self.getPercentage(98, total_files, current_count), "Writing new file...")
        xbmcvfs.rename(__temp_file__, full_file_path);

        if current_count==total_files:
            progressDialog.update(self.getPercentage(100, total_files, current_count), "Done, reloading video")
            xbmc.sleep(500)

        return True

    def onPlayBackStarted(self):
        self.init_properties()
        playing = xbmc.Player().getPlayingFile()
        path = os.path.split(playing)[0]
        subsFound = self.findSubs(path)

        sub_file_count = subsFound['count']

        if sub_file_count >0:

            log('pausing playback')
            #pause playback
            xbmc.Player().pause()

            if self.autoclean == True:
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
                        sub_path = os.path.join(path, f)
                        log("start cleaning file "+ str(count)+" of "+str(sub_file_count)+" \n:" +str(f) )
                        cleaning = self.clean(f, path, files_to_process, count)
                        sub_file_count = sub_file_count - count

                        if cleaning == False:
                            xbmc.Player().pause()
                            log("User cancelled during cleaning of files")
                            return

                # get the current playing item
                current_vdo = xbmc.Player().getPlayingFile()

                # stop & start player to refresh the subtitle stream
                log("resuming" + str(current_vdo))
                xbmc.Player().stop()
                xbmc.sleep(1000)
                xbmc.Player().play(current_vdo)

            else:
                xbmc.Player().pause()
                log("User denied cleaning of files")

        else:
            log("Nothing to do")

monitor = Sublime()

log("Loading '%s' version '%s'" % (__addonname__, __addonversion__))

while not xbmc.abortRequested:
    xbmc.sleep(1000)

del monitor