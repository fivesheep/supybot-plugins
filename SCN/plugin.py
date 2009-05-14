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
import time

import socket
socket.setdefaulttimeout(15)

def generate_date_str(dst):
    sec=time.mktime(time.localtime())-dst*24*60*60
    return time.strftime('%Y-%m-%d',time.localtime(sec))

class SCN(callbacks.Plugin):
    """This plugin is for searching 0day stuffs.
    This should describe *how* to use this plugin."""
    threaded = True
    BASE_URL=r'http://www.doopes.com/?num=2&mode=0&opt=0'
    PATTERN=re.compile(r'<tr.*?><td>(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}<td>(.*?)<td>([^< \n]*)', re.I)
    
    CATALOGS={
        "ISO" : 512,
        "0DAY" : 2,
        "PDA" : 8192,
        "EBOOK" : 128,
        "IMAGESET" : 256,
        "CONSOLE" : 16,
        "VCD" : 131072,
        "SVCD" : 16384,
        "DIVX" : 32,
        "DVDR" : 64,
        "ANIME" : 4,
        "TV" : 32768,
        "XXX" : 262144,
        "MP3" : 2048,
        "MV" : 1
    }

    def __init__(self,irc):
        self.__parent=super(SCN,self)
        self.__parent.__init__(irc)

    def _urlopen(self,url):
        req=urllib2.Request(url,None,{'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'})
        return urllib2.urlopen(req)

    def _search(self,qstrs,cat,start,end,exclude,lang):
        results=[]
        url=SCN.BASE_URL
        url+='&cat=%d&lang=%d&from=%s&to=%s&inc=%s&exc=%s'%(cat,lang,start,end,'+'.join(qstrs),exclude)

        try:
            resp=self._urlopen(url)
            data=resp.read()
            results=SCN.PATTERN.findall(data)
            results.reverse()
            self._print_result(results)
        except:
            irc.reply('Unable to connect to remote server or connection timeout, please retry later.')
        finally:
            resp.close()

        return results

    def _print_result(self,irc,results):
        if len(results)==0:
            irc.reply('Sorry, No results were found!')
        else:
            count=5
            for i in results:
                irc.reply('[%s] %s %s'%i)
                count-=1
                if count == 0:
                    break

    def pre(self,irc,msg,args,options,qstrs):
        """[OPTION]... [keyword]...
        
        Search Scene releases via pre.scnsrc.net. Searching options including: 
        --cat the catalog of the releases, it's value could be one of the 
              following: iso, 0day, pda, ebook, imageset, console, divx, dvdr, 
              anime, tv, xxx, mp3, mv
        --start the start date which format is YYYY-MM-DD.
        --end the end date which format is YYYY-MM-DD.
        --exclude exclude the items with the given keyword. 
        --all-lang by default, it searches english items only.
        """
        options=dict(options)

        if options.has_key('cat') and SCN.CATALOGS.has_key(options.has_key('cat').upper()):
            cat=SCN.CATALOGS.has_key(options.has_key('cat').upper())
        else:
            cat=2 #0day

        if options.has_key('start'):
            d=options['start']
            if re.match(r'^\d{4}-\d{2}-\d{2}$',d):
                start=d
            else:
                irc.reply('Date must be in the format of YYYY-MM-DD')
                return
        else:
            start=generate_date_str(30)
        
        if options.has_key('end'):
            d=options['end']
            if re.match(r'^\d{4}-\d{2}-\d{2}$',d):
                end=d
            else:
                irc.reply('Date must be in the format of YYYY-MM-DD')
                return
        else:
            end=time.strftime('%Y-%m-%d')

        if options.has_key('exclude'):
            exclude=options['exclude']
        else:
            exclude=''

        if options.has_key('all-lang'):
            lang=0
        else:
            lang=1

        self._search(qstrs,cat,start,end,exclude,lang)

    pre=wrap(pre,[getopts({'cat':'something', 'start':'something', 'end':'something', 'exclude':'something', 'all-lang':''}),any('something')])

    def zday(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for 0day releases.
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(90)
        self._search(qstrs,SCN.CATALOGS['0DAY'],start,time.strftime('%Y-%m-%d'),'',0)
    zday=wrap(zday,[any('something')])

    def apps(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released apps.
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(90)
        self._search(qstrs,SCN.CATALOGS['ISO'],start,time.strftime('%Y-%m-%d'),'',0)
    apps=wrap(apps,[any('something')])

    def movie(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released movies(xvid).
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(30)
        self._search(qstrs,SCN.CATALOGS['DIVX']+SCN.CATALOGS['DVDR'],start,time.strftime('%Y-%m-%d'),'',0)
    movie=wrap(movie,[any('something')])
    
    def mp3(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released mp3s.
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(30)
        self._search(qstrs,SCN.CATALOGS['MP3'],start,time.strftime('%Y-%m-%d'),'',0)
    mp3=wrap(mp3,[any('something')])

    def ebook(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released ebooks.
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(90)
        self._search(qstrs,SCN.CATALOGS['EBOOK'],start,time.strftime('%Y-%m-%d'),'',0)
    ebook=wrap(ebook,[any('something')])

    def pda(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released pda softwares including iphone, ipod apps.
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(90)
        self._search(qstrs,SCN.CATALOGS['PDA'],start,time.strftime('%Y-%m-%d'),'',0)
    pda=wrap(pda,[any('something')])

    def ustv(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released tv programs.
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(30)
        self._search(qstrs,SCN.CATALOGS['TV'],start,time.strftime('%Y-%m-%d'),'',0)
    ustv=wrap(ustv,[any('something')])

    def console(self,irc,msg,args,qstrs):
        """[keyword]...
        
        Search for released console games (including ps2, ps3, xbox, wii....).
        """
        if len(qstrs)==0:
            start=generate_date_str(1)
        else:
            start=generate_date_str(90)
        self._search(qstrs,SCN.CATALOGS['CONSOLE'],start,time.strftime('%Y-%m-%d'),'',0)
    console=wrap(console,[any('something')])

Class = SCN


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=179:
