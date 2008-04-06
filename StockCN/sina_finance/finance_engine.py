# -*- coding: utf-8 -*-

import re
import traceback
import urllib,urllib2
import thread
import sys

from singleton import Singleton
from finance_items import FinanceItemFactory
        
class SearchEngine(Singleton):
    
    ENCODING='gbk'
    # the following url is used in http://biz.finance.sina.com.cn/suggest/lookup_n.php
    SUGGEST_URL=r'http://202.108.37.42:8086/f.suggest?q=%s'
    DATA_URL=r'http://hq.sinajs.cn/list=%s'
    SUGG_PATT=re.compile(r'everydata\[\d+\]=".*\t([a-z]+-[a-z0-9]+-.*)";', re.I)
    DATA_PATT=re.compile(r'var hq_str_.*?="(.*?)";', re.I)
    TOP_DATA_PATT=re.compile(r'\["[a-z]*(\d+", ".*?", -?[\d\.]+, [\d\.]+)\],?',re.I)
    
    TOP_LISTS={'shu':('stock_sh_up_d_10',u'代码: %s, 名称: %s, 涨幅: %s$P, 当前价格: %s'),
               'shd':('stock_sh_down_d_10',u'代码: %s, 名称: %s, 跌幅: %s$P, 当前价格: %s'),
               'szu':('stock_sz_up_d_10',u'代码: %s, 名称: %s, 涨幅%s$P, 当前价格: %s'),
               'szd':('stock_sz_down_d_10',u'代码: %s, 名称: %s, 跌幅: %s$P, 当前价格: %s'),
               'shv':('stock_sh_volume_d_10',u'代码: %s, 名称: %s, 成交量: %s手, 当前价格: %s'),
               'sha':('stock_sh_amount_d_10',u'代码: %s, 名称: %s, 成交量: %s万元, 当前价格: %s'),
               'szv':('stock_sz_volume_d_10',u'代码: %s, 名称: %s, 成交量: %s手, 当前价格: %s'),
               'sza':('stock_sz_amount_d_10',u'代码: %s, 名称: %s, 成交量: %s万元, 当前价格: %s'),
               'wu':('warrant_up_d_10',u'代码: %s, 名称: %s, 涨幅: %s$P, 当前价格: %s'),
               'wd':('warrant_down_d_10',u'代码: %s, 名称: %s, 涨幅: %s$P, 当前价格: %s'),
               'bu':('stock_b_up_d_10',u'代码: %s, 名称: %s, 涨幅: %s$P, 当前价格: %s'),
               'bd':('stock_b_down_d_10',u'代码: %s, 名称: %s, 涨幅: %s$P, 当前价格: %s'),
               'fu':('fund_up_d_10',u'代码: %s, 名称: %s, 涨幅: %s$P, 当前价格: %s'),
               'fd':('fund_down_d_10',u'代码: %s, 名称: %s, 涨幅: %s$P, 当前价格: %s')
               }
        
    def __init__(self):
        pass
    
    def urlopen(self,url):
        req=urllib2.Request(url, None,
                            {'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'})
        return urllib2.urlopen(req)

    def fetch_content(self,url):
        handl=self.urlopen(url)
        data=handl.read().decode(SearchEngine.ENCODING)
        handl.close()
        return data
    
    def generate_suggest_url(self,qstr):
        return (SearchEngine.SUGGEST_URL%qstr).encode(SearchEngine.ENCODING)
    
    def generate_data_url(self,hqstrs):
        return SearchEngine.DATA_URL%(','.join(hqstrs))
        
    def lookup_suggests(self,qstr):
        try:
            url=self.generate_suggest_url(qstr)
            data=self.fetch_content(url)
            # suggest str is in the following format 'flag-symbol-name'
            # example: sh-600001-StockName 
            suggests=SearchEngine.SUGG_PATT.findall(data)     
        except:
            traceback.print_exc()
            suggests=[]
        return suggests
    
    def feed_all(self,items):
        succecced=[]
        try:
            num_of_items=len(items)
            if num_of_items>0:
                url=self.generate_data_url([ item.to_hqstr() for item in items ])
                rawdata=self.fetch_content(url)
                results=SearchEngine.DATA_PATT.findall(rawdata)
                if num_of_items==len(results):
                    for i in range(num_of_items):
                        if items[i].feed(results[i])==True:
                            succecced.append(items[i])
                        
        except:
            traceback.print_exc()
        
        return succecced

            
    def search(self,qstrs):
        # 1. lookup the hqstrs
        suggests=[]
        for qstr in qstrs:
            suggests+=self.lookup_suggests(qstr)
        # 2. parse the suggests into finance items(types: sh,sz,fu,ft,fx...)
        ff=FinanceItemFactory()
        items=[ ff.create(sugg) for sugg in suggests ]
        items=[ i for i in items if i != None ]
        # 3. feed all Items
        feeded_items=self.feed_all(items)
        # 4. return the finance items
        return feeded_items
    
    def top10(self,key):
        results=[]
        if SearchEngine.TOP_LISTS.has_key(key):
            qstr,fmtstr=SearchEngine.TOP_LISTS[key]
            data=self.fetch_content(self.generate_suggest_url(qstr))
            itemstrs=SearchEngine.TOP_DATA_PATT.findall(data)
            
            count=1
            for i in itemstrs:
                item="[%d]"%count+fmtstr%(i.replace('"','').replace(' ','').split(','))
                results.append(item)
                count+=1
        
        return results
            
    def index(self):    
        pass
        
    
if __name__=='__main__':
    eng=SearchEngine()
#    sugg=eng.lookup_suggests('000001')
#    for s in sugg:
#        print s.encode('gbk')
        
    items=eng.search(['600001','600050','699999'])
    for i in items:
        print ("%s"%i).encode('gbk')
    
    items=eng.search(['000001','hdgt','sfz','0981','hkd','hkyn','cu0711'])
    for i in items:
        print ("%s"%i).encode('gbk')
        