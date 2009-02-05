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
import supybot.conf as conf

from bsddb import db
from os import path


class Hanzi(callbacks.Plugin):
    """Add the help for "@plugin help Hanzi" here
    This should describe *how* to use this plugin."""
    BASE_PATH=path.dirname(path.realpath(__file__))
    # Get the channel encoding
    CHANNEL_ENCODING=conf.supybot.plugins.Hanzi.encoding()
    DB_ENCODING='utf-8'

    def __init__(self,irc):
        self.__parent=super(Hanzi,self)
        self.__parent.__init__(irc)
        self.pydb=db.DB()
        self.wbdb=db.DB()
        pydbpath=path.join(Hanzi.BASE_PATH,'pinyin.db')
        wbdbpath=path.join(Hanzi.BASE_PATH,'wubi.db')
        self.pydb.open(pydbpath, None, db.DB_HASH, db.DB_RDONLY)
        self.wbdb.open(wbdbpath, None, db.DB_HASH, db.DB_RDONLY)

    def pinyin(self, irc, msg, args, chars):
        """<chinese words>
        
        Lookup the pinyins for the given chinese chars.
        """
        chars=chars.decode(Hanzi.CHANNEL_ENCODING)
        result="Make sure you have input a chinese string"
        items=[]
        for c in chars:
            p=self.pydb.get(c.encode(Hanzi.DB_ENCODING))
            if p != None:
                p=p.decode(Hanzi.DB_ENCODING)
                items.append('%s: %s'%(c,p))

        if len(items) > 0:
            result=' | '.join(items)

        irc.reply(result.encode(Hanzi.CHANNEL_ENCODING))

    pinyin=wrap(pinyin,['something'])

    def wubi(self, irc, msg, args, chars):
        """<chinese chars>
        
        Lookup the Wubi keys for the given chinese chars.
        """
        chars=chars.decode(Hanzi.CHANNEL_ENCODING)
        result="Make sure you have input a chinese string"
        tmp=self.wbdb.get(chars.encode(Hanzi.DB_ENCODING))
        if tmp:
            result=chars+': '+tmp.decode(Hanzi.DB_ENCODING)
        elif len(chars)>1:
            items=[]
            for c in chars:
                c=c.encode(Hanzi.DB_ENCODING)
                p=self.wbdb.get(c)
                if p != None:
                    tmp=c+': '+p
                    items.append(tmp.decode(Hanzi.DB_ENCODING))

            if len(items) > 0:
                result=' | '.join(items)

        irc.reply(result.encode(Hanzi.CHANNEL_ENCODING))
    wubi=wrap(wubi,['something'])
        

Class = Hanzi


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
