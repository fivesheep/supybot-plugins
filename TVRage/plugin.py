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
import supybot.conf as conf
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import traceback
import tvrage
import re

class TVRage(callbacks.Plugin):
    """Add the help for "@plugin help TVRage" here
    This should describe *how* to use this plugin."""
    threaded = True
    def __init__(self,irc):
        self.__parent=super(TVRage,self)
        self.__parent.__init__(irc)

        self.encode=conf.supybot.plugins.TVRage.encode()
        self.search_engine=tvrage.TvrageSearchEngine()
        #print self.encode

    def tv(self,irc,msg,args,show):
        """<show_name>

           search the tv show via http://www.tvrage.com
        """
        try:
            results=self.search_engine.quick_search(show)
            if len(results)==0:
                irc.reply("03Nothing Found!")
            else:
                irc.reply(show_raw+" 07[Name: %s] [Premiered: %s] [Country: %s] [Status: %s] [Classification: %s] [Genres: %s] [Latest Episode: %s]"%(
                                results['Show Name'],results['Premiered'],results['Country'],results['Status'],
                                results['Classification'],results['Genres'],results['Latest Episode']))
                irc.reply("12[URL: %s ]"%(results['Show URL']))
        except:
            irc.reply("Oops, an exception happended during searching!")
            traceback.print_exc()
    tv=wrap(tv,['text'])

Class = TVRage


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
