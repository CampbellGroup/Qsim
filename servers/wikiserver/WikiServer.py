"""
### BEGIN NODE INFO
[info]
name = Wiki Server
version = 1.0
description = 
instancename = WikiServer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import os, re, sys
import labrad
import datetime
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

class WikiServer(LabradServer):
    """
    WikiServer for pushing data to wiki
    """
    name = 'WikiServer'
    
    @inlineCallbacks
    def initServer(self):
        try:
            yield self.client.registry.cd(['','Servers', 'wikiserver'])
        except:
            try:
                print 'Could not load repository location from registry.'
                print 'Please enter Wiki directory or hit enter to use the current directory:'
                WIKIDIR = raw_input( '>>>' )
                if WIKIDIR == '':
                    WIKIDIR = os.path.join( os.path.split( __file__ )[0], '__wiki__' )
                if not os.path.exists( WIKIDIR ):
                    os.makedirs( WIKIDIR )
                # set as default and for this node
                print WIKIDIR, "is being used",
                print "as the wiki location."
                print "To permanently set this, stop this server,"
                print "edit the registry keys"
                print "and then restart."
            except Exception, E:
                print
                print E
                print
                print "Press [Enter] to continue..."
                raw_input()
                sys.exit()
        self.maindir = yield self.client.registry.get('wikipath')
        self.maindir = self.maindir[0]
        self.homefile = self.maindir + '/Wiki-Log.md'
        yield os.chdir(self.maindir)

    @setting(21, 'Update Wiki', returns='')
    def update_wiki(self, c ):

        yield os.system("git add . -A")
        yield os.system('git commit -am "added line from wiki server"')

    @setting(22,'Add line to file', line='s', returns='')
    def add_line(self, c, line):
        
        self.date = datetime.datetime.now()
        
        self.year = self.date.strftime("%G") 
        self.yearfile = self.year + '.md' 
        
        self.month = self.date.strftime("%B")
        self.monthfile = self.month + ' ' + self.year + '.md'
        
        if os.path.isfile(self.yearfile) and os.path.isfile(self.monthfile):   
            
            self.prepend(self.monthfile, line)
            
        elif os.path.isfile(self.yearfile):
            self.prepend(self.yearfile, '[[' + self.month + ']]')
            yield open(self.monthfile, 'a').close()
            self.prepend(self.monthfile, line)
            
        else:
            
            self.prepend(self.homefile, '[[' + self.year + ']]')
            yield open(self.yearfile, 'a').close()
            self.prepend(self.yearfile, '[[' + self.month + ' ' + self.year + ']]')
            yield open(self.monthfile, 'a').close()
            self.prepend(self.monthfile, line)
            
            
    @inlineCallbacks    
    def prepend(self, document, line):
            self.original = yield open(document, 'r')
            self.oldfile = yield self.original.read()
            self.original.close()
            self.newfile = yield open(document, 'w') 
            self.newfile.write(line + '\n\n' + self.oldfile)
            yield self.newfile.flush()
            yield self.newfile.close()

if __name__ == "__main__":
    from labrad import util
    util.runServer(WikiServer())