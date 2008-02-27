#!/bin/env python

import urllib2,urllib
from BeautifulSoup import BeautifulSoup
import re
import traceback

class TvrageSearchEngine:
    def __init__(self):
        self.header={'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'}
        split_keys=['1080i', '1080p', '720p', 'avc', 'bdrip', 'blueray',
                    'cam', 'camera', 'dsr', 'dsrip', 'dvbrip', 'dvd', 'dvdrip', 'dvdscr',
                    'fs', 'fullscreen', 'hd','hddvdrip', 'hddvd', 'hdrip', 'hdtv', 'hr',
                    'int', 'internal', 'limited', 'pdtv', 'proper', 'r[1-6]', 'repack', 'rerip', 
                    'retail','satrip', 'screener', 'sdtv', 'svcd', 'subbed',
                    'tc', 'telecine', 'telesync', 'ts', 'tvdvdr', 'tvrip',
                    'vc1','vc-1', 'vcd', 'vhsrip', 'wmv', 'workprint', 'x264', 'xvid']
        self.regex=re.compile(r'^(.*?)(\.\d{4})?\.('+'|'.join(split_keys)+')\..*?-.*?$',re.I)

    def quick_search(self,show):
        tmp={   'Show Name':'',
                'Premiered':'',
                'Country':'',
                'Status':'',
                'Genres':'',
                'Classification':'',
                'Latest Episode':'',
                'Show URL':'' }
        url=self._quickinfoUrl(show)
        results=[ l.replace('\n','').split('@') for l in urllib.urlopen(url).readlines()]

        if len(results)>2:
            for item in results:
                if len(item)==2:
                    tmp[item[0]]=item[1]
            return tmp
        else:
            return {}

    def _quickinfoUrl(self,qstr):
        # Filtering the querying string to remove the interference factors,
        # and then generate the querying url.
        qstr=qstr.strip().replace('_','.')
        groups=self.regex.findall(qstr)
        if len(groups)>0:
            qstr=groups[0][0]
        patt=re.compile(r'\.(S\d+E|\d+x|E)\d+\.?')
        match=patt.search(qstr)
        if match:
            qstr=qstr[:match.start()]
        qstr=qstr.replace('.',' ')
        qstr='+'.join([ s for s in qstr.split(' ') if s!=''])
        return r'http://www.tvrage.com/quickinfo.php?show='+qstr

    ######################################################################
    #   Lines below are out-of-date. will be deleted.
    ######################################################################
    def make_req(self,url,post_data=None):
        if post_data!=None:
            post_data=urllib.urlencode(post_data)
        return urllib2.Request(url,post_data,self.header)

    def get_remote_document(self,url,post_data=None):
        return urllib2.urlopen(self.make_req(url,post_data))

    def remove_tags(self,str_with_tags):
        flag=False
        result=[]
        for char in str_with_tags:
            if char == '<':
                flag=False
            elif char == '>':
                flag=True
            else:
                if flag==True:
                    result.append(char)
        return "".join(result)


    def do_search(self,keywords):
        url='http://www.tvrage.com/search.php?show_ids=1&search=' + '+'.join(keywords)
        doc=self.get_remote_document(url)
        results=[]
        # begin to handle the results
        soup=BeautifulSoup(doc.read())

        found_flag=soup.find('b',text=re.compile('^Found \d+ Show.*$'))
        if found_flag == None:
            return results
        num_found=int(found_flag.split(' ')[1])
        # print "***Num Found:%d"%num_found

        div_search_begin=soup.findAll('div',id='search_begin')[0]
        links=div_search_begin.findAll('a',href=re.compile('^http://www.tvrage.com/'))
        show_ids=div_search_begin.findAll('td',text=re.compile(r'^\[show=\d+\]$'))

        # print "***Links Found:%d"%len(links)
        # print "***Num of Show ids:%d"%len(show_ids)

        for i in range(0,min(num_found,5)):
            results.append((show_ids[i][6:-1], # remove '[show=' and ']', leave only the num
                            links[i].attrs[0][1],
                            links[i].contents[0]))

        return num_found,results

    def get_content_by_id(self,showid):
        if not re.compile(r'^\d+$').match(showid):
            # The given showid is not a num string.
            return None
        result={
                'URL:' : 'http://www.tvrage.com/shows/id-%s'%showid,
                }

        doc=self.get_remote_document('http://www.tvrage.com/shows/id-%s'%showid)
        soup=BeautifulSoup(doc.read())

        title_tags=soup.find('h3',attrs={'align':'center', 'class':'nospace'})
        if len(title_tags)!=1:
            return None
        result['Title']=title_tags.contents[0]

        tables=soup.findAll('table',width=None,align=None,cellpadding=None,cellspacing=None)
        if len(tables)==0:
            return None
        info_table=tables[0]
        value_tags=info_table.findAll('td',width=None,valign=None)
        item_tags=soup.findAll('td',attrs={'width':'150','valign':'top'})
        # len(item_tags) should equal len(value_tags)
        for i in range(0,len(item_tags)):
            key=self.remove_tags(str(item_tags[i])).strip()
            value=self.remove_tags(str(value_tags[i])).strip()
            result[key]=value

        return result

    def search(self,keywords):
        temp=[] # the array being return
        num_of_results,results=self.do_search(keywords)
        if num_of_results==0:
            #print "Nothing was found!"
            temp.append('Nothing Found!')
        elif num_of_results==1:
            #print the content
            content=self.get_content_by_id(results[0][0])
            for key in content.keys():
                temp.append("%s %s"%(key,content[key]))
        else:
            temp.append("Found %d Shows, Only Showing %d:"%(num_of_results,len(results)))
            for result in results:
                temp.append("[ShowId=%s] URL: %s, Title: %s"%result)

        return temp

    def search_id(self,showid):
        result=self.get_content_by_id(showid)
        temp=[]
        for key in result.keys():
            temp.append("%s %s"%(key,result[key]))

        return temp


##if __name__=='__main__':
##    tvr=TvrageSearchEngine()
##    tvr.search(['The','4400'])
##    print '-'*100
##    tvr.search(['Hello'])
##    print '-'*100
##    tvr.search(['Hellosssssssssssssssss'])

##tvr=TvrageSearchEngine()
##
##def tvr_timer(userdata):
##    global tvr
##    srv=userdata[0]
##    word=userdata[1]
##
##    try:
##        results=tvr.search(word[1].split(' ')[1:])
##        for result in results:
##            # print "msg %s %s"%(word[0],result)
##            context=xchat.find_context(server=srv)
##            context.command("notice %s %s"%(word[0], result))
##    except:
##        print "Error on searching tvr!!!"
##        traceback.print_exc()
##
##    return False
##
##def tvrid_timer(userdata):
##    global tvr
##    srv=userdata[0]
##    word=userdata[1]
##
##    try:
##        result=tvr.search_id(word[1][6:].strip())
##        for item in result:
##            context=xchat.find_context(server=srv)
##            context.command("notice %s %s"%(item))
##    except:
##        print "Error on getting show info"
##        traceback.print_exc()
##
##    return False
##
##def tvrquick_timer(userdata):
##    global tvr
##    srv=userdata[0]
##    word=userdata[1]
##
##    context=xchat.find_context(server=srv)
##    try:
##        results=tvr.quick_search(word[1].split(' ')[1:])
##        if len(results)==0:
##            context.command("notice %s 03Nothing Found!"%word[0])
##            return False
##
##        context.command("notice %s 07[Name: %s] [Premiered: %s] [Country: %s] [Status: %s] [Classification: %s] [Genres: %s] [Latest Episode: %s]"%(
##                            word[0], results['Show Name'],results['Premiered'],results['Country'],
##                            results['Status'], results['Classification'],results['Genres'],results['Latest Episode']))
##
##        context.command("notice %s 12[URL: %s]"%(word[0],results['Show URL']))
##    except:
##        print "Error on quick search"
##        context.command("notice %s 03Error!"%word[0])
##        traceback.print_exc()
##
##    return False
##
##def tvr_search(word, word_eol, userdata):
##    srv=xchat.get_info('server')
##
##    if len(word) >= 2:
##        if word[1].startswith('!tvd '):
##            xchat.hook_timer(100,tvr_timer,(srv,word))
##        elif word[1].startswith('!tvid '):
##            xchat.hook_timer(100,tvrid_timer,(srv,word))
##        elif word[1].startswith('!tv '):
##            xchat.hook_timer(100, tvrquick_timer,(srv,word))
##
##    return xchat.EAT_NONE
##
##
##xchat.hook_print("Channel Message",tvr_search)
##
##print "TVR Search Engine is loaded!"
