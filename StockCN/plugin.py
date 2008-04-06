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
import traceback
import sina_stock

import sina_finance


class StockCN(callbacks.Plugin):
    """Add the help for "@plugin help StockCN" here
    This should describe *how* to use this plugin."""
    threaded = True
    def __init__(self,irc):
        self.__parent=super(StockCN,self)
        self.__parent.__init__(irc)

        self.encode=conf.supybot.plugins.StockCN.encode()
        self.engine=sina_stock.StockEngine(self.encode)

    def stock(self,irc,msg,args,words):
        """<keyword1> [<keyword2>] [<keyword3>]....
        
           Keywords can the id, abbr or name of a stock
        """
        try:
            eng=sina_finance.SearchEngine()
            results=eng.search([ w.decode(self.encode) for w in words ])
            for item in results:
                irc.reply(('%s'%item).encode(self.encode))
        except:
            traceback.print_exc()
            
    stock=wrap(stock,[many('something')])

    def index (self, irc, msg, args):
        """None
        
        This command takes no arguments."""
        try:
            results=self.engine.index()
            for item in results:
                irc.reply(item)
        except :
            traceback.print_exc()
    
    index=wrap(index)

    def top10 (self, irc, msg, args,ltype,options):
        """<ltype> [--{limit} num]
        
        Displaying the Top10 Lists. 
        ltype is the top10 type to show, it should be one of the following strings: 
        'shu,shd,szu,szd,shv,sha,szv,sza,wu,wd,bu,bd,fu,fd'
        --limit num of items to show, from 1 - 10
        """
        
        options=dict(options)
       
        limit=0
        if options.has_key('limit'):
            limit=options['limit']
            if limit>10:
                limit=10
        
        try:
            eng=sina_finance.SearchEngine()
            results=eng.top10(ltype)
            for item in results:
                irc.reply(item.encode(self.encode))
        except :
            traceback.print_exc()
    
    top10=wrap(top10,['something',getopts({'limit':'int'})])    


Class = StockCN


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
