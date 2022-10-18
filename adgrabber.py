import os
import random
from pymy import *
from bs4 import BeautifulSoup as bs
import threading
from threading import Lock
from urllib.parse import urlparse, urljoin
from time import sleep

currentuser = os.environ["USERNAME"]
# Define the lock globally to avoid the "recursive use of cursors not allowed" error
lock = Lock()


class SiteGrawbler():

    def __init__(self, url, extract_div_name='', find_tagname='', tagatt='', save_filename_extension_as='.html', force_overwrite='', save_directory=f'C:\\Users\\{currentuser}\\Downloads\\' ):
        
        self.url = url
        # set the subdomain to look for
        # self.sub_domain_only = domain_path(url)
        self.domain_only = getdomain_only(url)
        self.defaultdownloadfolder = joinpath_raw(save_directory, self.domain_only)
        self.extract_from_div_name  = extract_div_name
        self.find_tagname = find_tagname
        self.tagatt = tagatt
        self.save_filename_extension_as = save_filename_extension_as
        self.force_overwrite = force_overwrite
        # let declare the extension files we need
        self.image_links, self.media_links, self.webpage_links, self.css_links = [], [],[],[]
        # db part
        lock.acquire(True)
        self.dbname = resource_path(self.defaultdownloadfolder +'\\_adsql.db')
        # let connect to db
        self.init_db()


    def init_db(self):
        makefolder(self.defaultdownloadfolder)
        
        db = Db(self.dbname)
        # {'dname': new_filename, 'remotelink': file, 'dpath': path_folder_name, 'locallink': local_path_folder_name}
        create_scrapmedia_table = """ CREATE TABLE IF NOT EXISTS media_link (
                id integer PRIMARY KEY,
                url text NOT NULL,
                dtype text NOT NULL,
                dstatus integer
            ); """
        try:
            db.createdb(create_scrapmedia_table)

        except Exception:
            pass
        
        
    def download_file(self, fromlink, save_path='', save_pathlink=''):
        # check if file exists or not
        result = False
        filename = basename(save_pathlink)
        
        if not file_exists(save_pathlink):
            # make folder path where to save to
            makefolder(save_path)
            # downlaod and save locally
            result = downloadremote(fromlink, save_pathlink)
            
        if result:
            print(f'{filename} is downloaded to [{save_path}]\n')
        # else:
        #     print(f'{filename} failed download to [{save_path}]')
            
        return result


    def add_to_db(self, items, dont_download='1', isdownloaded='1'): 
        # we download and save item
        # check if we should backpass the file downloading and just save it on db
        # print(items)
        # print(f'dont_download: {dont_download} isdownloaded: {isdownloaded}\n')
        if dont_download:
            # check if its was downloaded successfully or not
            isdownloaded = self.download_file(items['remotelink'], items['localpath'], items['locallink'])
            if isdownloaded:
                isdownloaded = 1
            else:
                isdownloaded = 0            
            
        try:
            db = Db(self.dbname)
            con_db = db.check('id', 'media_link', f"url='{items['remotelink']}' AND dtype='{items['type']}' ")
            if con_db is None:
                db.insert('media_link', 'id, url, dtype, dstatus', f"NULL,'{items['remotelink']}','{items['type']}', '{isdownloaded}'")
        
        except Exception:
            pass
        

    def check_if_domain_starts_with(self, url):
        securelink, unsecurelink = 'https://' + self.domain_only, 'http://' + self.domain_only
        
        if url.startswith(securelink) or url.startswith(unsecurelink):
            return True

        return False
    
    
    def get_html_content(self, url):
        return remoteread_file(url)
    
    
    def prepare_link(self, link):
        # let get filename to save to
        # remove end tail slash
        link = link.rstrip('/')
        
        path_folder_name = clean_url_path(new_urlpath(link))
        local_path_folder_name = local_normalpath(path_folder_name)
        new_filename = basename(path_folder_name)
        local_path_folder = joinpath_raw(self.defaultdownloadfolder, urlfolder(path_folder_name).replace('/',"\\"))
        # new formate to save found file
        local_path_folder_name = joinpath_raw(local_path_folder, new_filename)
        return  {'name': new_filename, 'remotelink': link, 'linkpath': path_folder_name, 'locallink': local_path_folder_name,  'localpath': local_path_folder}
    
    
    def set_file_mimeType(self, url):
        # get extension
        link_extension =  exts(url)
        # new formate to save found file
        new_save_item = self.prepare_link(url)
        # sometimes we dont get extension from SEO webpages so we assume its a webpage 
        if not link_extension:
            if self.check_if_domain_starts_with(url):
                # add extenstion to filename
                localpath = new_save_item['localpath']
                new_save_item['locallink'] = new_save_item['localpath'] + self.save_filename_extension_as
                new_save_item['localpath'] = localpath.replace(new_save_item['name'],'').rstrip('\\')
                new_save_item['name'] = new_save_item['name'] + self.save_filename_extension_as
                new_save_item['linkpath'] = new_save_item['linkpath'] + self.save_filename_extension_as
                new_save_item['type'] = 'link'
                
                self.add_to_db(new_save_item, '', 0)
            
        else :
            # find image 
            if link_extension in extension_imagelist():
                # good image found let add to list
                if self.check_if_domain_starts_with(url):
                    new_save_item['type'] = 'media'
                    self.add_to_db(new_save_item)
                
            # find Webpage 
            if link_extension in extension_webpagelist():
                # good Webpage found let add to list
                if self.check_if_domain_starts_with(url):
                    new_save_item['type'] = 'link'
                    self.add_to_db(new_save_item, '', 0)
                
            # find StyleSheet css 
            if link_extension in extension_css():
                # good StyleSheet css found let add to list
                if self.check_if_domain_starts_with(url):
                    new_save_item['type'] = 'link'
                    # let process this css to download all it media content 
                    self.parce_css_file(url)
                    self.add_to_db(new_save_item, '')
            
        # print(result)
        return new_save_item
        
        
    def save_locally(self, dcontent, dpath, saveto_url, charset='utf-8'):
        #firstly get folder then create it
        if dpath:
            makefolder(dpath)
            
        try:
            with open(saveto_url, 'w', encoding=charset) as fp:
                fp.write(dcontent)
                
            return True
        
        except Exception as e:
            print('1 ', e)
            try:
                with open(saveto_url, 'w') as fp:
                    fp.write(dcontent)
                    
                return True
            
            except Exception as e:
                print(e)
                return False
        
        
    def parce_css_file(self, link):
        check_path = self.prepare_link(link)
        
        if not file_exists(check_path['locallink']) or self.force_overwrite:
            dcontent_result = self.get_html_content(link)
            dcontent = dcontent_result['body']
            dcontent_charset = dcontent_result['charset']
            
            dcontent = bs(dcontent, 'html.parser')
            #get all background embeded in style url
            soupbackground_image = self.parse_background_url_image_links(dcontent)
            # print(soupbackground_image)
            
            if len(soupbackground_image): 
                for found_link in soupbackground_image:
                    if found_link:
                        try:
                            oldurl = found_link.replace('"', '').replace( "'", '')
                        
                            downloadableurl = parse_url_short_link(link, oldurl)
                            
                            # print(downloadableurl)
                            self.set_file_mimeType(downloadableurl)
                            
                        except Exception:
                            pass
                    

            result = self.save_locally(dcontent.prettify(), check_path['localpath'], check_path['locallink'], dcontent_charset)
            if result:
                print(f'{check_path["name"]} is saved to [{check_path["localpath"]}]\n')
            else:
                print(f'{check_path["name"]} failed to saved to [{check_path["localpath"]}]\n')
        
        
    def get_all_links(self, url='', is_index ='1'):
        if not url:
            url = self.url.rstrip('/') #remove ending tralling /
            
        print('Processing... ', url, '\n')
        
        check_path = self.prepare_link(url)
        new_filename =  check_path['linkpath']
        
        if is_index:
            new_filename =  'index' + self.save_filename_extension_as
            check_path['locallink'] =  check_path['localpath'] + new_filename
            check_path['name'] =  new_filename
            check_path['linkpath'] =  new_filename
        
        if not file_exists(check_path['locallink']) or self.force_overwrite:
            dcontent_result = self.get_html_content(url)
            dcontent = dcontent_result['body']
            dcontent_charset = dcontent_result['charset']
            
            dcontent = bs(dcontent, 'html.parser')

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
            soupbackground_image = self.parse_background_url_image_links(dcontent)
        
            if len(soupbackground_image): 
                for found_link in soupbackground_image:
                    if found_link:
                        try:
                            oldurl = found_link.replace('"', '').replace( "'", '')
                        
                            downloadableurl = parse_url_short_link(url, oldurl)
                            processed_result = self.set_file_mimeType(downloadableurl)
                            dcontent = dcontent.replace(found_link, processed_result['linkpath'])
            
                        except Exception:
                            pass
                    
            #get all url a tags
            try:
                for a_stag in dcontent.find_all('a'):
                    #save for the next parsing must be full url
                    if a_stag["href"]:
                        href_link = cleanurl(url, a_stag["href"])
                        href_new_link = self.set_file_mimeType(href_link)
                        # now let rewrite the content to save
                        print(href_new_link['linkpath'])
                        a_stag["href"] = href_new_link['linkpath']

            except Exception:
                pass

            #get all url link tags
            try:
                for a_stag in dcontent.find_all('link'):
                    #save for the next parsing must be full url
                    if a_stag["href"]:
                        href_link = cleanurl(url, a_stag["href"])
                        href_new_link = self.set_file_mimeType(href_link)
                        # now let rewrite the content to save
                        a_stag["href"] = href_new_link['linkpath']

            except Exception:
                pass

            # #get all url script tags
            try:
                for a_stag in dcontent.find_all('script'):
                    #save for the next parsing must be full url
                    if a_stag["src"]:
                        href_link = cleanurl(url, a_stag["src"])
                        href_new_link = self.set_file_mimeType(href_link)
                        # now let rewrite the content to save
                        a_stag["src"] = href_new_link['linkpath']

            except Exception:
                pass

            # #get all url img tags
            try:
                for a_stag in dcontent.find_all('img'):
                    #save for the next parsing must be full url
                    if a_stag["src"]:
                        href_link = cleanurl(url, a_stag["src"])
                        href_new_link = self.set_file_mimeType(href_link)
                        # now let rewrite the content to save
                        a_stag["src"] = href_new_link['linkpath']

            except Exception:
                pass
                
            # print(check_path)
            result = self.save_locally(dcontent.prettify(), check_path['localpath'], check_path['locallink'], dcontent_charset)
            if result:
                print(f'{check_path["name"]} is saved to [{check_path["localpath"]}]\n')
            else:
                print(f'{check_path["name"]} failed to saved to [{check_path["localpath"]}]\n')
            
            try:
                db = Db(self.dbname)
                db.others(f"UPDATE media_link SET dstatus='1' WHERE url='{url}' ")
                
            except Exception as e:
                print('Error Updating page ', e)
                pass
            
                
        if is_index:
            # now let continue 
            db = Db(self.dbname)
            retry = 0
            while True:
                # break out of the loop the file link has finish 
                if retry ==3:
                    break
                
                try:
                    queue_items = db.fetch("SELECT url FROM media_link WHERE dstatus='0' AND dtype='link' ")
                    if len(queue_items) > 0:
                        for itemurl in queue_items:
                            self.get_all_links(itemurl['url'], '')
                            sleep(2)
                    
                except Exception as e:
                    print(e)
                    pass
                
                retry +=1
                
                sleep(3)

    
    def parse_background_url_image_links(self, dcontent):
        result = []
        dcontent = str(dcontent)
        
        if dcontent:
            try:
                result = findall(r'url\((.*?)\)', dcontent)

            except Exception as e:
                print('BACKGROUNDURL Error ', e)
                pass
        
        return result
    

if __name__ == "__main__":
    do = SiteGrawbler('https://wehostz.com/') #
    print(do.get_all_links())
    # print(do.parce_css_file('https://www.globalgiving.org/v2/css/minimal.css'))
    # let get the url variables 
    # https://wehostz.com/css/style.css
    # new_filename = cleantitle(basename(file))
    # print(firstpath_name(('http://wehostz.com/images/exchange-ecurrency.css', 1)))
    # {'name': 'fresh-leads.html', 'remotelink': 'http://wehostz.com/fresh-leads', 'linkpath': 'fresh-leads.html', 'locallink': 'fresh-leads.html', 'localpath': 'C:\\Users\\Blessed\\Downloads\\wehostz.com\\fresh-leads', 'type': 'link'}
