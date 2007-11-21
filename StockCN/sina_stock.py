# -*- coding: gbk -*-

import re
import traceback
import urllib2
import thread
import StringIO
from BeautifulSoup import BeautifulSoup

index_lock=thread.allocate_lock()
cash_flow_lock=thread.allocate_lock()

index_cache={'create_at':None,'data':None}
cash_flow_cache={'create_at':None,'data':None}

class StockEngine:
    def __init__(self,encode='gbk'):
        self.encode=encode
        self.columns=(  '�� ��','������', 
                        '����', '��ǰ�۸�', 
                        '��ͼ�', '��߼�', 
                        '�����','������', 
                        '�ɽ���', '�ɽ���',
                        'buy1','buy_price1',
                        'buy2','buy_price2',
                        'buy3','buy_price3',
                        'buy4','buy_price4',
                        'buy5','buy_price5',
                        'sell','sell_price1',
                        'sel2','sell_price2',
                        'sel3','sell_price3',
                        'sel4','sell_price4',
                        'sel5','sell_price5',
                        '�� ��','ʱ ��')

    def __getLink(self, link):
        req=urllib2.Request(link,None,
                               {'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'})
        return urllib2.urlopen(req)
    
    def __lookup(self, qstr):
        patt=re.compile(r'^\d{6}$')
        if patt.match(qstr):
            flag=int(qstr[0])
            if flag > 4:
                return 'sh'+qstr
            elif flag < 4:
                return 'sz'+qstr
            else:
                return None
        else:
            try:
                
                lookup_url="http://biz.finance.sina.com.cn/suggest/lookup.php?q=%s"%qstr
                handl=self.__getLink(lookup_url)
                redirected_url=handl.geturl()
                handl.close()
                patt=re.compile(r'^.*company/([a-z0-9]+)/nc.shtml$', re.I)
                m=patt.match(redirected_url)
                if m != None:
                    return m.group(1)
                else:
                    return None
            except:
                traceback.print_exc()
                return None
        
    def __getStockData(self, stock_ids):
        columns=self.columns
        if None != stock_ids and len(stock_ids)>0:
            stock_url="http://hq.sinajs.cn/&list=%s"%(",".join(stock_ids))
            handl=self.__getLink(stock_url)
            results=[]
            for i in range(len(stock_ids)):
                line=handl.readline()
                data=line.split('"')[1].split(",")
                
                result=[]
                for i in range(len(columns)):
                    result.append((columns[i],data[i]))
                results.append(result)
                
            handl.close()
            return results
        else:
            return None
    
    def search(self,stocks):
        tmp=[]
        real_ids=[]
        for word in stocks:
            word=word.decode(self.encode).encode('gbk')
            try:
                id=self.__lookup(word)
                if id != None:
                    real_ids.append((word,id))
                else:
                    pass
                    #irc.reply("û���� '%s' ��صĹ�Ʊ��Ϣ"%word)
            except:
                traceback.print_exc()
        
        try:
            results=self.__getStockData([ id[1] for id in real_ids])
            if results == None:
                return
            for i in range(len(results)):
                result=results[i]
                percent="%.2f"%((float(result[3][1])/float(result[2][1])-1)*100)+'%'
                result_str="%d [%s] ��Ʊ����: %s, ��ǰ��: %s, �Ƿ�: %s, ������: %s, ����: %s, ��ͼ�: %s, ��߼�: %s, ʱ ��:%s %s "% (
                                i+1, real_ids[i][0],result[0][1],result[3][1], percent,result[2][1],result[1][1],
                                result[5][1],result[4][1],result[30][1], result[31][1])
                tmp.append(result_str.decode('gbk').encode(self.encode))
        except :
            traceback.print_exc()
        
        if len(real_ids)==0:
            tmp.append("�Բ���, ϵͳ�Ҳ�������ѯ�Ĺ�Ʊ��Ϣ".decode('gbk').encode(self.encode))
        
        return tmp


    def index (self):
        tmp=[]
        try:
            results=self.__getLink("http://hq.sinajs.cn/&list=s_sh000001,s_sz399001,s_sh000300,s_sh000011,s_sz399305,s_sz399106")
            count=0
            for line in results:
                count+=1
                if count > 6:
                    break                
                data=line.split('"')[1].split(",")
                name=data[0]
                value=float(data[1])
                markup=float(data[2])
                markup_percent=float(data[3])
                quality=int(data[4])
                amount=float(data[5])/10000.0
                
                statement='\x031\x02%s - ����ָ��\x02 %.3f \x02ָ���ǵ�\x02 %.3f \x02�ɽ���\x02 %d \x02�ɽ���\x02 %.2f�� \x02�ǵ���\x02 %.2f%s'
                
                if markup_percent > 0:
                    statement='\x031\x02%s - ����ָ��\x02\x034 %.3f \x02\x031ָ���ǵ�\x02\x034 %.3f \x02\x031�ɽ���\x02\x034 %d \x02\x031�ɽ���\x02\x034 %.2f�� \x02\x031�ǵ���\x02\x034 %.2f%s'
                elif markup_percent < 0 :
                    statement='\x031\x02%s - ����ָ��\x02\x033 %.3f \x02\x031ָ���ǵ�\x02\x033 %.3f \x02\x031�ɽ���\x02\x033 %d \x02\x031�ɽ���\x02\x033 %.2f�� \x02\x031�ǵ���\x02\x033 %.2f%s'
                                
                item=statement%(name,value,markup,quality,amount,markup_percent,'%')
                tmp.append(item.decode('gbk').encode(self.encode))
            results.close()
        except :
            traceback.print_exc()
        return tmp

    def cash_flow(self):
        global lock
        tmp=[]

        # check the cache




if __name__=='__main__':
    engine=StockEngine('utf-8')
    results=engine.index()
    for r in results:
        print r
