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

from bsddb import db


class Pinyin(callbacks.Plugin):
    """Add the help for "@plugin help Pinyin" here
    This should describe *how* to use this plugin."""
    pass

    def __init__(self,irc):
        self.__parent=super(Pinyin,self)
        self.__parent.__init__(irc)
        self.pydb=db.DB()
        self.pydb.open('pinyin.db', None, db.DB_HASH, db.DB_RDONLY)
        

    def pinyin(self, irc, msg, args, chars):
        """<chinese words>
        
        Lookup the pinyins for the given chinese chars.
        """
        results=[]
        for c in chars:
            p=self.pydb.get(c)
            if p != None:
                results.append('%s: %s'%(c,p))

        if len(results) > 0:
            irc.reply(' | '.join(results))
        else:
            irc.reply('Make sure "%s" is a chinese string'%chars)

    pinyin=wrap(pinyin,['something'])

        

Class = Pinyin


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
