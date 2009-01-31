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

import re
import urllib
import urllib2

import socket
socket.setdefaulttimeout(15)

class SCN(callbacks.Plugin):
    """This plugin is for searching 0day stuffs.
    This should describe *how* to use this plugin."""
    threaded = True
    CATALOGS=['0DAY','XVID','DVDR','X264','BLURAY','TV','XXX','MP3','APPS','GAMES',
              'CONSOLE','HANDHELD','MVID','EBOOK','DOX','UNKNOWN','PSP','NDS','PDA']
    BASE_URL=r'http://pre.scnsrc.net/index.php?search='
    DATA_PATTERN=re.compile(r'<tr><td width="180"> (....-..-..) ..:..:.. </td><td class=".*?"> (.*?) </td><td>(.*?)(</img>| )?(<a.*?</a>)?</td></tr>')
    NFO_URL_PATTERN=re.compile(r'href="(http.*?)"')
    NUM_OF_RESULTS=5

    def __init__(self,irc):
        self.__parent=super(SCN,self)
        self.__parent.__init__(irc)

    def _urlopen(self,url):
        req=urllib2.Request(url,None,{'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'})
        return urllib2.urlopen(req)

    def _search(self,qstrs,cat=None):
        url=SCN.BASE_URL+'+'.join(qstrs)
        if cat != None and cat in SCN.CATALOGS:
            url=url+'&cat='+cat
        resp=self._urlopen(url)
        data=resp.read()
        resp.close()
        iter=SCN.DATA_PATTERN.finditer(data)
        results=[]
        for i in iter:
            if len(results) >= SCN.NUM_OF_RESULTS:
                break

            result={}
            result['date']=i.group(1)
            result['catalog']=i.group(2)
            result['name']=i.group(3).split(' ')[0]
            if i.group(5)!=None and len(i.group(5))>5:
                result['nfo']=SCN.NFO_URL_PATTERN.findall(i.group(5))[0]
            else:
                result['nfo']=''
            results.append(result)

        return results

    def _print_result(self,irc,results):
        if len(results)==0:
            irc.reply('Sorry, Nothing Found!')
        else:
            for i in results:
                irc.reply('[%s] %s %s [ NFO: %s ]'%(i['date'],i['catalog'],i['name'],i['nfo']))


    def pre(self,irc,msg,args,options,qstrs):
        cat=None
        options=dict(options)
        if options.has_key('cat'):
            cat=options['cat'].upper()
        
        results=self._search(qstrs,cat)

        self._print_result(irc,results)

    pre=wrap(pre,[getopts({'cat':'something'}),many('something')])

    def zd(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'0DAY')
        self._print_result(irc,results)
    zd=wrap(zd,[many('something')])

    def apps(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'APPS')
        self._print_result(irc,results)
    apps=wrap(apps,[many('something')])

    def movie(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'XVID')
        self._print_result(irc,results)
    movie=wrap(movie,[many('something')])
    
    def mp3(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'MP3')
        self._print_result(irc,results)
    mp3=wrap(mp3,[many('something')])

    def ebook(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'EBOOK')
        self._print_result(irc,results)
    ebook=wrap(ebook,[many('something')])

    def nds(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'NDS')
        self._print_result(irc,results)
    nds=wrap(nds,[many('something')])

    def psp(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'PSP')
        self._print_result(irc,results)
    psp=wrap(psp,[many('something')])

    def pda(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'PDA')
        self._print_result(irc,results)
    pda=wrap(pda,[many('something')])

    def games(self,irc,msg,args,qstrs):
        results=self._search(qstrs,'GAMES')
        self._print_result(irc,results)
    games=wrap(games,[many('something')])


Class = SCN


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=179:
