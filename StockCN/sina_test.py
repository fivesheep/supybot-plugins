#!/bin/env python
# -*- coding: utf-8 -*-

import sina_finance

if __name__=='__main__':
    eng=sina_finance.SearchEngine()
#    sugg=eng.lookup_suggests('000001')
#    for s in sugg:
#        print s.encode('gbk')
        
    
    items=eng.search(['600001','600050','699999','000001','hdgt','sfz','0981','hkd','hkyn','cu0711',u'硬麦'])
    for i in items:
        try:
            print ("%s"%i).encode('gbk')
        except:
            print ("%s"%i).encode('utf-8')