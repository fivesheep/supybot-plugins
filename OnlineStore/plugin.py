# -*- coding: utf-8 -*-
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
import supybot.conf as conf
import re
import urllib
"""
http://www.360buy.com/warelist.asp?productSort=&fromprice=&toprice=&fromcate=&fromlaod=&myKeyword=amd&wfacturer=&faid=&price=&facturer=&page=2


http://www.360buy.com/warelist.asp?productSort=&fromprice=&toprice=&fromcate=&fromlaod=&myKeyword=6600&wfacturer=Intel&faid=436&price=asc&facturer=
"""

class OnlineStore(callbacks.Plugin):
    """Add the help for "@plugin help OnlineStore" here
    This should describe *how* to use this plugin.
    
    --orderby : price,facturer
    """
    threaded = True
    def __init__(self,irc):
        self.__parent=super(OnlineStore,self)
        self.__parent.__init__(irc)
        
        self.encoding=conf.supybot.plugins.OnlineStore.encoding()
        self.re_jd_item=re.compile(r'<a href="wareshow\.asp\?wid=(\d+)" title="(.*?)">.*?</a></TD>.*?<div align="center">\s+(\d+|\d+\.\d+).</div></TD>\s+<TD><div align="center"><font color="#FF0000">\s+(.*?)<br />\s+(.*?)<br>(.*?)<br>')
    
    def jd(self,irc, msg, args, keyword, options):
        """<keyword> [--{fromprice,toprice,manufacturer,order-by-price,order-by-manufacturer} <value>]
        
        Search the products provided by 360buy.com with the given keyword. --fromprice is the min allowed price;
        --toprice is the max allowed price; --manufacturer is the manufacturer of the products; 
        --order-by-price with this option the results will be ordered by the price, it could only be 'asc' and 'desc';
        --order-by-manufacturer with this option the results will be ordered by the manufacturer, it could only be 'asc' and 'desc'.
        Note: for not flooding the user, only maxium 5 results will be returned.
        """
        
        # 1. Prepare the querying url
        parameters={'productSort':'',
                    'fromprice':'',
                    'toprice':'',
                    'fromcate':'',
                    'fromload':'',
                    'myKeyword':'',
                    'wfacturer':'',
                    'faid':'',
                    'price':'',
                    'facturer':'',
                    'page':''
                    }
        
        parameters['myKeyword']=keyword

        options=dict(options)
        
        if options.has_key('fromprice'):
            parameters['fromprice']=str(options['fromprice'])
            
        if options.has_key('toprice'):
            parameters['toprice']=str(options['toprice'])
            
        if options.has_key('manufacturer'):
            parameters['wfacturer']=options['manufacturer']
        elif options.has_key('mf'):
            parameters['wfacturer']=options['mf']
           
        if options.has_key('page'):
            parameters['page']=str(options['page'])
            
        if options.has_key('order-by-price') and options['order-by-price'] in ('desc','asc'):
            parameters['price']=options['order-by-price']
            
        if options.has_key('order-by-manufacturer') and options['order-by-manufacturer'] in ('desc','asc'):
            parameters['facturer']=options['order-by-manufacturer']
        
        parameters_string='&'.join([ '='.join(item) for item in parameters.items() ])
        url=r"http://www.360buy.com/warelist.asp?"+parameters_string.decode(self.encoding).encode('gbk')

        # 2. Fetch the searching result from the internet
        resp=urllib.urlopen(url)
        data=resp.read().decode('gbk')
        resp.close()
                
        # 3. Prepare for the results and output to the user       
        data=data[data.find('Form1'):data.rfind('</form>')].replace('\r\n','')
        items=self.re_jd_item.findall(data)
        num_of_items=len(items)
        if num_of_items > 0:
            for i in range(min(num_of_items,5)):
                item=items[i]
                pid=item[0]
                product=item[1]
                price=item[2]
                status=('|'.join(item[3:6])).replace('&nbsp;','')
                link=r'http://www.360buy.com/wareshow.asp?wid='+pid
                fmstr=u'[编号: %s ][商品名称: %s ][价格: %s元  ][存货: %s ][相关链接: %s ]'%(pid,product,price,status,link)
                irc.reply(fmstr.encode(self.encoding))
        else:
            irc.reply('No thing found!')
            
    jd=wrap(jd,['something',
                getopts({'fromprice':'int',
                         'toprice':'int',
                         'manufacturer':'something',
                         'mf':'something',
                         'order-by-price':'something',
                         'order-by-manufacturer':'something',
                         'page':'int'})])




Class = OnlineStore


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
