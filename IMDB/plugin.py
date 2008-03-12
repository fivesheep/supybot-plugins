###
# Copyright (c) 2007, Young Ng
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
# import imdb as pyimdb
import re
#import urllib
import urllib2
import traceback

# engine=pyimdb.IMDb()


class IMDB(callbacks.Plugin):
    """Add the help for "@plugin help IMDB" here
    This should describe *how* to use this plugin."""
    threaded = True
    def __init__(self,irc):
        self.__parent=super(IMDB,self)
        self.__parent.__init__(irc)
        
        split_keys=['dvdrip','repack','rerip','dvdscr',
                    'retail','subbed','proper','xvid',
                    'divx','hd','x264','unrated','limited',
                    'hdtvrip']
        self.regex=re.compile(r'^(.*?)(\.\d{4})?\.('+'|'.join(split_keys)+')\..*?-.*?$',re.I)
        self.regex_limited=re.compile(r'<tr><td><b><a href="/Recent/USA">USA</a></b></td>\r?\n    <td align="right"><a href=".*?">(.*?)</a> <a href=".*?">(\d{4})</a></td>\r?\n    <td> \(limited\)</td></tr>',re.MULTILINE)
        self.regex_screens=re.compile(r'\d+ \((USA|UK)\) \(<a.*?a>\) \(([0-9,]+) Screens?\)',re.I)
        self.rx_tt=re.compile(r'tt\d{4,}',re.I)
        self.rx_title=re.compile(r'<title>(.*?) \((\d{4})\)</title>', re.I)
        self.rx_rating=re.compile(r'<b>(\d\.\d)/10</b>.*\(<a href="ratings">([0-9,]+) votes</a>\)',re.I)
        
        self.rx_h5=re.compile(r'<h5>(Genre|Runtime|Language|Country):</h5>',re.I)
        self.h5_rxs={
                     'Genre':re.compile(r'\/Sections\/Genres\/.*?\/">(.*?)</a>',re.I),
                     'Runtime':re.compile(r'\d+ min',re.I),
                     'Language':re.compile(r'\/Sections\/Languages\/.*?\/">(.*?)</a>',re.I),
                     'Country':re.compile(r'\/Sections\/Countries\/.*?\/">(.*?)</a>',re.I)
                    }

    # def imdb(self,irc,msg,args,movie):
        # global engine
        # groups=self.regex.findall(movie)
        # if len(groups)>0:
            # keyword=groups[0]
        # else:
            # keyword=movie
        # results=engine.search_movie(keyword)
        # num_results=len(results)
        # if num_results==0:
            # irc.reply("Sorry, nothing found for: %s"%movie)
        # else:
            # item=results[0]
            # engine.update(item)
            # title,year,genres,countries,runtimes,rating,limited='','','','','','','N/A'
            # title=item['long imdb canonical title']
            # if item.has_key('year'): year=item['year']
            # if item.has_key('genres'): genres='|'.join(item['genres'])
            # if item.has_key('countries'): countries='|'.join(item['countries'])
            # if item.has_key('runtimes'): runtimes="%s min"%('|'.join(item['runtimes']))
            # if item.has_key('rating'): rating="%s/10 of %s votes" % (item['rating'], item['votes'])
            # url=r'http://www.imdb.com/title/tt%s'%item.movieID

            # # for limited info
            # releaseinfo=urllib.urlopen(url+'/releaseinfo').read()
            # limitedinfo=self.regex_limited.findall(releaseinfo)
            # if len(limitedinfo)>0:
                # limited=" USA %s %s (limited)"%limitedinfo[0]
            
            # # for screens info
            # bussiness_data=urllib.urlopen(url+'/business').read()
            # ow_start=bussiness_data.find(r'<h5>Opening Weekend</h5>')+len(r'<h5>Opening Weekend</h5>')
            # ow_end=bussiness_data.find('<h5>',ow_start)
            # ow=bussiness_data[ow_start:ow_end]
            # screen_infos=self.regex_screens.findall(ow)
            # screen_usa,screen_uk=0,0
            # for country,screens in screen_infos:
                # screens=int(screens.replace(',',''))
                # if country=='USA':
                    # screen_usa+=screens
                # else:
                    # screen_uk+=screens

            # irc.reply("07[Name: %s] [Year: %s] [Countries: %s] [Genres: %s] [Runtimes: %s] [Rating: %s] [Limited: %s] [Screens: USA %d | UK %d]" %
                        # (title,year,countries,genres,runtimes, rating, limited,screen_usa,screen_uk))
            # irc.reply("12[URL: %s ]"%url)

    # imdb=wrap(imdb,['text'])
    
    
    def _urlopen(self,url):
        req=urllib2.Request(url, None,
                {'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'})
        return urllib2.urlopen(req)
    
    def _get_base_info(self,ttid):
        """
            Fetch the movie infos by the ttid.
            Including: Title,Year,Rating,Genre,Country,Runtime
        """
        url=r'http://www.imdb.com/title/%s'%ttid
        movie=self._urlopen(url)
        result={ }
           
        # parsing the html
        while(1):
            rawline=movie.readline()
            line=rawline.rstrip('\n')
                
            if not result.has_key('Title') and line.startswith('<title>'):
                m=self.rx_title.match(line)
                if m!=None:
                    result['Title']=m.group(1)
                    result['Year']=m.group(2)
                    title=m.group(1)
                    year=m.group(2)
            elif not result.has_key('Rating') and line.startswith('<b>User Rating:'):
                data=movie.readline().rstrip('\n')
                data+=movie.readline().rstrip('\n')
                m=self.rx_rating.match(data)
                if m!=None:
                    result['Rating']="%s/10 of %s votes"%(m.group(1),m.group(2))
                else:
                    result['Rating']=None
            elif line.startswith('<h5>'):
                m=self.rx_h5.match(line)
                if m!=None:
                    h5_type=m.group(1)
                    data=movie.readline()
                    result[h5_type]='/'.join(self.h5_rxs[h5_type].findall(data))
            else:
                # Break, if "Title,Year,Rating,Genre,Country,Runtime" are in the result,
                # or end of the file reached
                if len(result)==7 or rawline=='':
                    movie.close()
                    break
        
        return result
    
    def _get_limited_info(self,ttid):
        # for limited info
        url=r'http://www.imdb.com/title/%s/reaseinfo'%ttid
        try:
            input=self._urlopen(url)
        except:
            return ""
        data=input.read()
        input.close()
        limitedinfo=self.regex_limited.findall(data)
        if len(limitedinfo)>0:
            limited=" USA %s %s (limited)"%limitedinfo[0]
        else:
            limited=''
        return limited
        
    def _get_screen_info(self,ttid):
        url=r'http://www.imdb.com/title/%s/business'%ttid
        try:
            input=self._urlopen(url)
        except:
            return ""
        bussiness_data=input.read()
        ow_start=bussiness_data.find(r'<h5>Opening Weekend</h5>')+len(r'<h5>Opening Weekend</h5>')
        ow_end=bussiness_data.find('<h5>',ow_start)
        ow=bussiness_data[ow_start:ow_end]
        screen_infos=self.regex_screens.findall(ow)
        screen_usa,screen_uk=0,0
        for country,screens in screen_infos:
            screens=int(screens.replace(',',''))
            if country=='USA':
                screen_usa+=screens
            else:
                screen_uk+=screens
        
        limited='No'
        if screen_usa<500 or screen_uk<250:
            limited='Yes'
                
        return "USA %d / UK %d / %s"%(screen_usa,screen_uk,limited)

    def imdbtt(self,irc,msg,args,ttid):
        # check if the given ttid is in the proper format
        if not self.rx_tt.match(ttid):
            irc.reply('Sorry, you must input a ttid for querying.')
            return
        
        try:
            base=self._get_base_info(ttid)
            screens=self._get_screen_info(ttid)
            #limited=self._get_limited_info(ttid)
            irc.reply("07[Name: %s] [Year: %s] [Countries: %s] [Languages: %s] [Genres: %s] [Runtimes: %s] [Rating: %s] [Screens: %s ]" %
                        (base['Title'],base['Year'],base['Country'],base['Language'],base['Genre'],base['Runtime'], base['Rating'], screens)) 
            irc.reply("12[URL: http://www.imdb.com/title/%s ]"%ttid  )         
        except:
            irc.reply('Error, Please try again lata.')
            traceback.print_exc()
            
    imdbtt=wrap(imdbtt,['text'])        

Class = IMDB


# vim:set shiftwidth=4 tabstop=4 expandtab : 
