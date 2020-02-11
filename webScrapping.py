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

	def __init__(self):
		self.defaultdownloadfolder = f'C:\\Users\\{currentuser}\\Downloads'
		self.grabinput = "https://scrapethissite.com"
		self.grabmaindomain = domaintld(self.grabinput, 'domain')
		self.changeextension = '.html'
		self.grabproxylist = []  # Add Proxy: e.g '127.0.0.1:8000','56.99.99.88:6000'
		self.jsfolder = 'js'  # store all js and java script
		self.cssfolder = 'css'  # store all css and scss
		self.imagefolder = 'images'  # store all related media files
		self.fontfolder = 'fonts'  # store all fonts
		self.pagefolder = ''
		self.fontslist = ['.ttf', '.woff', '.woff2', '.eot', '.less', '.otf',  '.ac']
		self.ignorelist = ['.html', '.htm', '.html5',
		    '.php', '.py', '.java', '.blade', '.aspx']
		self.downloadfiles = ['.pdf', '.exe', '.docx', '.doc', '.csv']
		self.grapdofollow = True
		self.totalnumber_of_url = 0
		self.grabproxylist = ''
		self.totalcountdb_stored = 0
		lock.acquire(True)
		self.dbname = 'scrapDB.db'
		self.extravariable = ""  # {{url}}
		self.usegrabaction = "Download"  # Download or Extract
		self.usegrabpage = "Full Site"  # Single Page or Full Site

		db = Db(resource_path(self.dbname))
		create_scrapmedia_table = """ CREATE TABLE IF NOT EXISTS scrapmedia (
									id integer PRIMARY KEY,
									url text NOT NULL,
									status integer
								); """

		create_scrapurl_table = """CREATE TABLE IF NOT EXISTS scrapurl (
									id integer PRIMARY KEY,
									url text NOT NULL,
									status integer
							);"""

		if not is_url(self.grabinput):
			print('Invalid website formate eg: http://yoursite.com')

		elif self.defaultdownloadfolder == '':
			print('Please select folder to save download')

		elif self.changeextension == '':
			print('Please changeextension must not be empty')

		elif internet_on() == 'off':
			print(' Sorry no internet connection, please on your internect connection ')

		else:
			db.createdb(create_scrapmedia_table)
			db.createdb(create_scrapurl_table)

			self.defaultdownloadfolder = joinpath(
			    self.defaultdownloadfolder, getdomain_only(self.grabinput))
			self.pathjsfolder = joinpath(self.defaultdownloadfolder, self.jsfolder)
			self.pathcssfolder = joinpath(self.defaultdownloadfolder, self.cssfolder)
			self.pathimagefolder = joinpath(
			    self.defaultdownloadfolder, self.imagefolder)
			self.pathfontfolder = joinpath(self.defaultdownloadfolder, self.fontfolder)
			self.pathpagefolder = joinpath(self.defaultdownloadfolder, self.pagefolder)
			folderlist = [self.pathcssfolder, self.pathfontfolder,
			    self.pathimagefolder, self.pathjsfolder, self.pathpagefolder]
			# create default folder with domain name
			makefolder(self.defaultdownloadfolder)
			# create folders
			for foldername in folderlist:
				makefolder(foldername)

			db.others("DELETE FROM scrapurl WHERE id!='' ")
			db.others("DELETE FROM scrapmedia WHERE id!='' ")
			# do the processing
			t1 = threading.Thread(name='Scrapping URL', target=self.run)
			t1.start()
			t2 = threading.Thread(name='Scrapping Downloading',
			                      target=self.downloadMedia)
			t2.start()

	def doparse(self, get_graburl, linkpath_defined, default=''):
		db = Db(resource_path(self.dbname))
		inputgraburl = self.grabinput
		changextension = self.changeextension
		grabproxytotal = len(self.grabproxylist)
		targetfolder = joinpath(self.defaultdownloadfolder, self.pathpagefolder)
		usingproxy1 = ''
		maindomainname = self.grabmaindomain
		usegrabpage = self.usegrabpage
		# get domain with full eg: http://domain.com
		self.getdomain = urldomains(inputgraburl)

		get_graburl = get_graburl.rstrip('/')
		writefile_to = basename(get_graburl)
		writefile_to_ext = exts(writefile_to)
		# get the local path of the url eg: http://google.com/en/search/q?=ii5 to en/search
		localpath = urlfolder(get_graburl)

		if not linkpath_defined:
			linkpath = localpaths(localpath)
		else:
			linkpath = linkpath_defined

		# maindomain is in the url and also check the first line http://facebook.com to compare
		if maindomainname in get_graburl:

			if default:
				writefile_to = 'index' + changextension

			else:
				if writefile_to_ext == '.txt':
					writefile_to = writefile_to
				else:
					# restructure url links to local paths
					if '?' in writefile_to:
						writefile_to = cleantitle(writefile_to.split('?')[1])
					writefile_to = cleantitle(getFilename(writefile_to)) + changextension

			if localpath:
				getfilefolder = joinpath(targetfolder, localpath)
			else:
				getfilefolder = targetfolder

			print(
			    f'**Parsing... [{get_graburl}]\n=============================================')

			try:
				# follow the site folder structure
				finalcopyto = joinpath(getfilefolder, writefile_to)
				# if proxy is defined we use the proxy to connect
				# its will randomly select proxy to use
				if self.grabproxylist:
					r1 = random.randint(0, grabproxytotal)
					usingproxy1 = self.grabproxylist[r1]

				dcontent = remoteread_file(get_graburl, usingproxy1)
				# if bad parsing returned
				try:
					soupbackground_image = findall(r'url\((.*?)\)', dcontent)
					for cssjsurl in soupbackground_image:
						oldurl = cssjsurl.replace('"', '').replace("'", '').replace('..', '')
						oldbase = basename(oldurl)
						ext = exts(cssjsurl)
						if '?' in ext:
							# this handles cases of file.eot?somethin
							# so get a clean extension
							ext = ext.split('?')[0]

						if '#' in ext:
							# this handles cases of file.eot#somethin
							# so get a clean extension
							ext = ext.split('#')[0]

						if ext in self.fontslist:
							dfolder = '../fonts'
						else:
							dfolder = '../images'
						# download image
						checkoldbase = oldurl[0]
						if checkoldbase == '/':
							downloadableurl = self.getdomain + oldurl
						else:
							downloadableurl = self.getdomain + '/' + oldurl

						cssjsdochck = db.check('id', 'scrapmedia', F"url='{downloadableurl}' ")
						if cssjsdochck is None:
							if not ext in self.ignorelist:
								print(' |->found/saved: ' + downloadableurl)
								db.insert('scrapmedia', 'id, url, status',
								          f"NULL,'{downloadableurl}', '0'")

						if linkpath:
							dfolder = dfolder.replace('../', '')

						newurlpath = linkpath + joinpath(dfolder, oldbase)
						dcontent = dcontent.replace(cssjsurl, newurlpath)
					maincontent = dcontent
				except Exception:
					maincontent = dcontent

				# do processing of others which are not in cssjs list
				content = bs(maincontent, 'html.parser')

				# find all a href
				print(' |->parsing <A> tags')
				countlog = 0
				grabproxy = 0
				for a_stag in content.find_all('a'):
					try:
						foundurl = a_stag["href"]
						# use this to remove any last / on the url for proper url linking
						foundurl_filter = foundurl.rstrip('/')
						sub_folder = urlfolder(foundurl_filter)
						basenamefound = basename(foundurl_filter)
						sub_slugindex_extension = exts(foundurl)

						# restructure url links to local paths
						if '?' in basenamefound:
							basenamefound = cleantitle(basenamefound.split('?')[1])

						getfilename = getFilename(basenamefound)
						if getfilename:
							sub_filetoname = cleantitle(getfilename) + changextension
							new_a_href = joinpath(sub_folder, sub_filetoname)
						else:
							new_a_href = sub_folder

						# only point url a href link if pass
						a_stag['href'] = linkpath + new_a_href

						# save for the next parsing must be full url
						foundurl = cleanurl(self.getdomain, foundurl)

						# make sure is only scrappin same domain or subdomain not external domain
						if maindomainname in foundurl:
							countlog += 1
							grabproxy += 1
							# Storing all found url for next scrapping
							if 'css' in foundurl or 'js' in foundurl:
								dochck = db.check('id', 'scrapmedia', F"url='{foundurl}' ")
								if dochck is None:
									db.insert('scrapmedia', 'id, url, status', f"NULL,'{foundurl}', '0'")
									print('  |->found/saved: ' + new_a_href)

							elif sub_slugindex_extension in self.downloadfiles:
								dochck = db.check('id', 'scrapmedia', F"url='{foundurl}' ")
								if dochck is None:
									db.insert('scrapmedia', 'id, url, status', f"NULL,'{foundurl}', '0'")
									print('  |->found/saved: ' + new_a_href)

							elif sub_slugindex_extension in self.ignorelist:
								# if 'css' in foundurl
								if usegrabpage == 'Full Site':
									check = db.check('id', 'scrapurl', "url='" + foundurl + "'")
									if check is None:
										db.insert('scrapurl', 'id, url, status',
										          "NULL,'" + foundurl + "', 0")
										print(' |->found/saved: ' + new_a_href)

							else:
								if usegrabpage == 'Full Site':
									check = db.check('id', 'scrapurl', "url='" + foundurl + "'")
									if check is None:
										db.insert('scrapurl', 'id, url, status',
										          "NULL,'" + foundurl + "', 0")
										print(' |->found/saved: ' + new_a_href)
					except Exception as e:
						print( f' |->Error parsing [{foundurl}] A HREF TAG: ' + str(e))

				print( ' |<<' + str(countlog) + ' parsed <a> tag')
				# '''
				# find all js script
				print( ' |->parsing <SCRIPT> tag')
				countscript = 0
				for s_stag in content.find_all('script'):
					try:
						j_href = s_stag['src']
						base = basename(j_href)
						downloadableurl = cleanurl(self.getdomain, j_href)
						extension = exts(base)

						# do the main downloading
						if not extension in self.ignorelist:
							dochck = db.check('id', 'scrapmedia', F"url='{downloadableurl}' ")
							if dochck is None:
								countscript += 1
								db.insert('scrapmedia', 'id, url, status',
											f"NULL,'{downloadableurl}', '0'")
								print(
										'  |->found/saved: ' + downloadableurl)
							else:
								pass

						# path to point the link to
						new_j_href = joinpath(urlfolder(j_href), base)

						s_stag['src'] = linkpath + new_j_href

					except Exception:
						pass
						# print( f' |->Error parsing [{j_href}] script TAG: ' + str(e))

				print( ' |<<' + str(countscript) + ' parsed <script> tag')

				# Find all css and scss files
				print( ' |->parsing <LINK> tag')
				countscript = 0
				for l_stag in content.find_all('link'):
					try:
						# remove integrity="" values and crossorigin="" values
						del l_stag['integrity']
						del l_stag['crossorigin']
						c_href = l_stag['href']
						base = basename(c_href)
						downloadableurl = cleanurl(self.getdomain, c_href)
						extension = exts(base)

						if not extension:
							# check is css or js
							if 'css' in base:
								base = extension + '.css'
								extension = '.css'

							if 'js' in base:
								base = extension + '.js'
								extension ='.js'

						if extension:
							if not extension in self.ignorelist:
								dochck = db.check('id', 'scrapmedia', F"url='{downloadableurl}' ")
								if dochck is None:
									countlog += 1
									print( ' |->found/saved: ' + base)
									db.insert('scrapmedia', 'id, url, status', f"NULL,'{downloadableurl}', '0'")
								else:
									pass
						# path to point the link to
						new_c_href  = joinpath(urlfolder(c_href), base)

						l_stag['href'] = linkpath + new_c_href

					except Exception:
						pass

				print( ' |<<' + str(countlog) +' parsed <link> tag')

				# find all images files
				print( ' |->parsing <IMG> tag')
				countscript = 0
				for i_stag in content.find_all('img'):
					try:
						im_href = i_stag['src']
						base = basename(im_href)
						downloadableurl = cleanurl(self.getdomain, im_href)
						extension = exts(base)

						# do the main downloading
						if not extension in self.ignorelist:
							dochck = db.check('id', 'scrapmedia', F"url='{downloadableurl}' ")
							if dochck is None:
								countscript += 1
								print( '  |->found/saved: ' + downloadableurl)
								db.insert('scrapmedia', 'id, url, status', f"NULL,'{downloadableurl}', '0'")
							else:
								pass
								# print('WARNING', ' |->already exists: ' + downloadableurl)

						new_im_href = joinpath(self.imagefolder, base)
						# print('------IMG: '+str(new_im_href))
						i_stag['src'] = linkpath + new_im_href

					except Exception:
						pass
						# print( f' |->Error parsing [{im_href}] img TAG: ' + str(e))

				print( ' |<<' + str(countscript) +' parsed <img> tag')

				try:
					parsedcontent = content.prettify().replace('&gt;', '>').replace('&amp;', '&').replace('&lt;', '<')
					# save parsed files
					if not os.path.exists(finalcopyto):
						makefolder(getfilefolder)
						localwrite_file(finalcopyto, parsedcontent)
						print( ' |->Saved to:=> ' + basename(finalcopyto))

				except Exception:
					pass
					# print( 'Error can not write the file to  [' + finalcopyto + '] ' + str(e))

				print( f'[**] Finished Parsing [{get_graburl}]\n=============================================\n')
				# '''
			except Exception:
				pass


		else:
			print(f'|xxxxx External Url Parsing not allowed [{get_graburl}]xxxxx|')

		try:
			lock.release()
		except Exception:
			pass

	def downloadMedia(self):
		db = Db(resource_path(self.dbname))
		usegrabaction = self.usegrabaction

		if usegrabaction == 'Download':
			retry = 0
			while True:
				retry += 1

				try:
					queue_media_list = db.fetch("SELECT url,id FROM scrapmedia WHERE status='0' ")
					self.totalcountdb_stored = len(queue_media_list) + self.totalcountdb_stored
					# check if all is done

					iscss = ''
					# start downloading things
					for itemurls in queue_media_list:

						downloadfrom = itemurls['url']
						downloadfromID = itemurls['id']
						# for rowurl in queue_media_list:
						grabproxytotal2 = len(self.grabproxylist)
						r2 = random.randint(0, grabproxytotal2)
						try:
							usingproxy2 = self.grabproxylist[r2]
						except:
							usingproxy2 = ''

						getdomain = urldomains(downloadfrom)
						getbasename = basename(downloadfrom)
						if not is_url(downloadfrom):
							downloadfrom = getdomain.rstrip('/') + '/' + downloadfrom.lstrip('/')

						if '?' in getbasename:
							getbasename = getbasename.split('?')[0]
						elif '#' in getbasename:
							getbasename = getbasename.split('#')[0]
						else:
							getbasename = getbasename

						# get file extensions from here
						ext = exts(getbasename).lower()
						if ext == '.js' or 'js' in getbasename:
							pathfolder = urlfolder(downloadfrom)
							if not pathfolder:
								pathfolder = self.pathjsfolder

						elif ext == '.css' or ext == '.scss' or 'css' in getbasename:
							pathfolder = urlfolder(downloadfrom)
							if not pathfolder:
								pathfolder = self.pathcssfolder

							iscss = 1

						elif ext in self.fontslist:
							pathfolder = self.pathfontfolder

						else:
							pathfolder = self.pathimagefolder

						if not ext:
							# meaning extension was not provided let reconstruct
							if 'css' in getbasename:
								getbasename = getbasename + '.css'
								iscss = 1

							elif 'js' in getbasename:
								getbasename = getbasename + '.js'

						# structure the domain filename full path
						usefolder = joinpath(self.defaultdownloadfolder, pathfolder)
						filename = joinpath(usefolder, getbasename)
						# save the parsed file
						makefolder(usefolder)

						if not os.path.exists(filename):
							# if this file is .css let searched for urls images and add to download db
							if iscss:
								try:
									htmlsoup = remoteread_file(downloadfrom)
								except Exception:
									pass

								try:
									for cssjsurl in findall(r'url\((.*?)\)', str(htmlsoup)):
										if '"' in cssjsurl:
											oldurl = cssjsurl.split('"')[1]
										elif "'" in cssjsurl:
											oldurl = cssjsurl.split("'")[1]
										else:
											oldurl = cssjsurl

										ext = exts(oldurl)
										oldurl = oldurl.replace('../', '')
										oldbase = basename(oldurl)

										if ext in self.fontslist:
											dfolder = '../fonts'
										else:
											dfolder = '../images'

										if not ext:
											if 'css' in cssjsurl:
												oldbase = oldbase + '.css'

											elif 'js' in cssjsurl:
												oldbase = oldbase+'.js'

										cleanpath = oldbase.replace( '%', '').replace('#', '')
										newurlpath = joinpath(dfolder, cleanpath)
										if is_url(oldurl):
											downloadableurl = oldurl
										else:
											downloadableurl = getdomain.rstrip('/') + '/' + oldurl.lstrip('/')

										cssjsdochck = db.check('id', 'scrapmedia', F"url='{downloadableurl}' ")
										if cssjsdochck is None:
											print( ' |->found/saved: ' + downloadableurl)
											db.insert('scrapmedia', 'id, url, status', f"NULL,'{downloadableurl}', '0'")

								except Exception:
									pass

							print( f' -***Downloading... {downloadfrom}')
							# handles the downloading part
							if remotedownload_file(downloadfrom, filename, usingproxy2):
								print( f' -***Downloaded... {getbasename}')
							else:
								print( f' -***Download failed... {getbasename}')

						db.others(f"UPDATE scrapmedia SET status='1' WHERE id='{downloadfromID}' ")
				except Exception as e:
					print(str(e))
		try:
			lock.release()
		except Exception:
			pass

	def run(self):
		graburl = self.grabinput
		linkpath = self.extravariable
		db = Db(resource_path(self.dbname))
		# do the processing
		self.doparse(graburl, linkpath, 1)

		while True:
			queue_url_list = db.fetch("SELECT url FROM scrapurl WHERE status='0' ")
			self.totalcountdb_stored = len(queue_url_list) + self.totalcountdb_stored

			for itemurl in queue_url_list:

				processurl = itemurl['url']
				# do the processing
				self.doparse(processurl, linkpath)
				# mark as proceed
				db.others(f"UPDATE scrapurl SET status='1' WHERE url='{processurl}' ")

			queueurl_list = db.fetch("SELECT id  FROM scrapurl WHERE status='0' ")
			queuemedia_list = db.fetch("SELECT id FROM scrapmedia WHERE status='0' ")
			totalleft = len(queueurl_list) + len(queuemedia_list)

			if not totalleft:
				db.others("DELETE FROM scrapurl WHERE id!='' ")
				db.others("DELETE FROM scrapmedia WHERE id!='' ")
				print( f'|->***DOWNLOAD COMPLETED***********|\nTOTAL PROCESSED: {self.totalcountdb_stored}\n')
				# reset alls
				self.totalcountdb_stored = ''
				break
		try:
			lock.release()
		except Exception:
			pass


if __name__ == "__main__":
	SiteGrawbler()
