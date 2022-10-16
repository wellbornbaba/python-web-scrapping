import os
import random
from pymy import *
from bs4 import BeautifulSoup as bs
import threading
from threading import Lock

currentuser = os.environ["USERNAME"]
# Define the lock globally to avoid the "recursive use of cursors not allowed" error
lock = Lock()


class SiteGrawbler():

    def __init__(self, url, extract_div_name='', find_tagname='', tagatt=''):
        self.defaultdownloadfolder = f'C:\\Users\\{currentuser}\\Downloads'
        self.url = url
        # set the subdomain to look for
        self.sub_domain_only = domain_path(url)
        self.extract_from_div_name  = extract_div_name
        self.find_tagname = find_tagname
        self.tagatt = tagatt
        # let declare the extension files we need
        self.image_links, self.media_links, self.webpage_links, self.css_links = [], [],[],[]

    
    def get_html_content(self):
        return remoteread_file(self.url)
    
    
    def set_file_mimeType(self, file):
        # get extension
        link_extension =  exts(file)
        # sometimes we dont get extension from SEO webpages so we assume its a webpage 
        if not link_extension:
            if file.startswith(self.sub_domain_only):
                add_to_list(file, self.webpage_links)
            
        else :
            # find image 
            if link_extension in extension_imagelist():
                # good image found let add to list
                if file.startswith(self.sub_domain_only):
                    add_to_list(file, self.image_links)
                
            # find Webpage 
            if link_extension in extension_webpagelist():
                # good Webpage found let add to list
                if file.startswith(self.sub_domain_only):
                    add_to_list(file, self.webpage_links)
                
            # find StyleSheet css 
            if link_extension in extension_css():
                # good StyleSheet css found let add to list
                if file.startswith(self.sub_domain_only):
                    add_to_list(file, self.css_links)


    def get_all_links(self):
        dcontent = self.get_html_content()
        
        dcontent = bs(dcontent, 'html.parser')
        url = self.url.rstrip('/') #remove ending tralling /
        result = []

        # if is decleared we only extract attribute with the value provided not parsing all body of the page
        if self.extract_from_div_name:
            tagname = self.find_tagname.lower()
            htmlclasslist = []
            if ',' in self.tagatt :
                for ex in self.tagatt .split(','):
                    if ex:
                        htmlclasslist.append(ex.strip())
            else:
                htmlclasslist.append(self.tagatt .strip())

            if tagname == 'id':
                for foundhtml in dcontent.find_all(self.extract_from_div_name, id=htmlclasslist):
                    dcontent = foundhtml
            else:
                for foundhtml in dcontent.find_all(self.extract_from_div_name, class_=htmlclasslist):
                    dcontent = foundhtml

        #get all background embeded in style url
        try:
            soupbackground_image = findall(r'url\((.*?)\)', dcontent)
            for cssjsurl in soupbackground_image:
                oldurl = cssjsurl.replace('"', '').replace( "'", '').replace('..', '')
                
                checkoldbase = oldurl[0]
                if checkoldbase == '/':
                    downloadableurl = url + oldurl
                else:
                    downloadableurl = url + '/' + oldurl

                self.set_file_mimeType(downloadableurl)
                result.append(downloadableurl)

        except Exception as e:
            print('BACKGROUNDURL Error ', e)
            pass

        #get all url a tags
        try:
            for a_stag in dcontent.find_all('a'):
                #save for the next parsing must be full url
                href_link = cleanurl(url, a_stag["href"])
                self.set_file_mimeType(href_link)
                result.append(href_link)

        except Exception as e:
            print('HREF Error ', e)
            pass

        #get all url link tags
        try:
            for a_stag in dcontent.find_all('link'):
                #save for the next parsing must be full url
                href_link = cleanurl(url, a_stag["href"])
                self.set_file_mimeType(href_link)
                result.append(href_link)

        except Exception as e:
            print('LINK Error ', e)
            pass

        #get all url script tags
        try:
            for a_stag in dcontent.find_all('script'):
                #save for the next parsing must be full url
                
                href_link = cleanurl(url, a_stag["src"])
                self.set_file_mimeType(href_link)
                result.append(href_link)

        except Exception as e:
            print('SCRIPT Error ', e)
            pass

        #get all url img tags
        try:
            for a_stag in dcontent.find_all('img'):
                #save for the next parsing must be full url
                href_link = cleanurl(url, a_stag["src"])
                self.set_file_mimeType(href_link)
                result.append(href_link)

        except Exception as e:
            # result.append(str(e))
            print('IMG Error ', e)
            pass

        return remove_duplicate_list(self.image_links)
    
    
    def check_if_same_domain(self, url):
        default_url = ''



if __name__ == "__main__":
    do = SiteGrawbler('http://wehostz.com/') #
    print(do.get_all_links())
    # let get the url variables 
    # https://wehostz.com/css/style.css
    # print(domain_path("https://wehostz.com/"))
