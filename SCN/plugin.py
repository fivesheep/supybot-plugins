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

    def _search(self,qstrs,cat=None,limit=5):
        url=SCN.BASE_URL
        results=[]
        if len(qstrs)!=0:
            url+='+'.join(qstrs)
        if cat != None and cat in SCN.CATALOGS:
            url+='&cat='+cat
        resp=self._urlopen(url)
        while(1):
            line=resp.readline()
            if line=='':
                # reach the end of the remote data.
                break    
            if line.startswith('<table>') and line.find('</table>') == -1:
                # begin to read releases data
                for i in range(limit):
                    release_info=resp.readline().rstrip('\n')
                    m=SCN.DATA_PATTERN.match(release_info)
                    if m:
                        result={}
                        result['date']=m.group(1)
                        result['catalog']=m.group(2)
                        result['name']=m.group(3).split(' ')[0]
                        if m.group(5)!=None and len(m.group(5))>5:
                            result['nfo']=SCN.NFO_URL_PATTERN.findall(m.group(5))[0]
                        else:
                            result['nfo']=''
                        results.append(result)
                break
                                                
        resp.close()
        return results

    def _print_result(self,irc,results):
        if len(results)==0:
            irc.reply('Sorry, Nothing Found!')
        else:
            for i in results:
                irc.reply('[%s] %s %s | NFO: %s'%(i['date'],i['catalog'],i['name'],i['nfo']))

    def pre(self,irc,msg,args,options,qstrs):
        """[OPTION]... [keyword]...
        
        Search Scene releases via pre.scnsrc.net. Searching options including: 
        --limit the max num of the returning results, it's 5 by default; 
        --cat the catalog of the releases, it's value could be one of the 
              following: xvid,dvdr,x264,bluray,tv,xxx, mp3, 0day, apps, games, 
                       console, handheld, mvid, ebook, dox, psp, nds, pda..
        """
        cat=None
        options=dict(options)
        if options.has_key('cat'):
            cat=options['cat'].upper()
        if options.has_key('limit'):
            limit=options['limit']
        else:
            limit=SCN.NUM_OF_RESULTS
        
        results=self._search(qstrs,cat,limit)

        self._print_result(irc,results)

    pre=wrap(pre,[getopts({'cat':'something', 'limit':'int'}),any('something')])

    def zday(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for 0day releases.
        """
        results=self._search(qstrs,'0DAY')
        self._print_result(irc,results)
    zday=wrap(zday,[any('something')])

    def apps(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released apps.
        """
        results=self._search(qstrs,'APPS')
        self._print_result(irc,results)
    apps=wrap(apps,[any('something')])

    def movie(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released movies(xvid).
        """
        results=self._search(qstrs,'XVID')
        self._print_result(irc,results)
    movie=wrap(movie,[any('something')])
    
    def mp3(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released mp3s.
        """
        results=self._search(qstrs,'MP3')
        self._print_result(irc,results)
    mp3=wrap(mp3,[any('something')])

    def ebook(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released ebooks.
        """
        results=self._search(qstrs,'EBOOK')
        self._print_result(irc,results)
    ebook=wrap(ebook,[any('something')])

    def nds(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released nds roms.
        """
        results=self._search(qstrs,'NDS')
        self._print_result(irc,results)
    nds=wrap(nds,[any('something')])

    def psp(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released psp roms.
        """
        results=self._search(qstrs,'PSP')
        self._print_result(irc,results)
    psp=wrap(psp,[any('something')])

    def pda(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released pda softwares including iphone, ipod apps.
        """
        results=self._search(qstrs,'PDA')
        self._print_result(irc,results)
    pda=wrap(pda,[any('something')])

    def games(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released pc games.
        """
        results=self._search(qstrs,'GAMES')
        self._print_result(irc,results)
    games=wrap(games,[any('something')])

    def console(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released console games (including ps2, ps3, xbox, wii....).
        """
        results=self._search(qstrs,'CONSOLE')
        self._print_result(irc,results)
    console=wrap(console,[any('something')])

Class = SCN


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=179:
