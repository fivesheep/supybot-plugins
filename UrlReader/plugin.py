###
# Copyright (c) 2009, Young Ng
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import supybot.ircmsgs as ircmsgs

import re
import urllib
import urllib2
import bsddb
import pickle
import socket

import traceback

socket.setdefaulttimeout(10)

class UrlReader(callbacks.Plugin):
    """Add the help for "@plugin help UrlReader" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    databases={}
    URL_PATTERN=re.compile(r'https?:\/\/[^ ]+',re.I)
    TITLE_PATTERN=re.compile(r'<title.*?>(.*?)<\/title>',re.I)
    CHAR_PATTERN=re.compile(r'charset=([a-z0-9_-]+)',re.I)

    def doPrivmsg(self, irc, msg):
        if irc.isChannel(msg.args[0]):
            nick=msg.nick
            channel=msg.args[0]
            message=msg.args[1]
            urls=UrlReader.URL_PATTERN.findall(message)
            for url in urls:
                self._handleUrl(irc,channel,nick,url)
    
    def _handleUrl(self,irc,channel,nick,url):
        # 1 lookup from the db
        scname='%s_%s'%(irc.network,channel)

        if not UrlReader.databases.has_key(scname):
            # new db
            dbpath=plugins.makeChannelFilename('%s.db'%scname ,'urldata')
            UrlReader.databases[scname]=bsddb.btopen(dbpath,'c')

        urldb = UrlReader.databases[scname]

        if urldb.has_key(url):
            poster,title=pickle.loads(urldb[url])
            msg='%s has already posted it: %s'%(poster,title)
            irc.reply(msg.encode('utf-8'))
        else:

            try:
                title=self._getTitle(url)
                if title != None:
                    urldb[url]=pickle.dumps([nick,title])
                    irc.reply(title.encode('utf-8'))
            except:
                traceback.print_exc()
                irc.reply('No Title')
    

    def _getTitle(self,url):
        title=None
        req=urllib2.Request(url,None,{'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'})
        handler=urllib2.urlopen(req)
        if handler.headers['Content-Type'].find('html')>-1:
            # read the first 4096 bytes
            text=handler.read(4096)
            handler.close()
            tm=UrlReader.TITLE_PATTERN.search(text)
            cm=UrlReader.CHAR_PATTERN.search(text)
            if tm:
                title=tm.groups()[0]
                if cm:
                    encoding=cm.groups()[0]
                else:
                    # use 'gbk' as default encoding
                    encoding='gbk'
                title=title.decode(encoding)

                return title

        else:
            return None


Class = UrlReader


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
