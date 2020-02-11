# python-web-scrapping
Scrap web site contents, download entire website offline for later viewing or readiing. This script extract any website content offline maintaining it default folder structures but rewrite/point the URL links locally for easy browsing.

You also have the ability to specific if you want to change the save extension by changing the extension and so on.

# Import Notes

1. Here you can specify where you want the web files downloaded to **self.defaultdownloadfolder**
2. **self.grabinput** specify which website url you want to scrap or download
3. **self.changeextension** specify the extension you wish the files downloaded to save as
4. **self.grabproxylist** list socks ip and port 127.122.133.11:8080 and so on if you wish to use proxy socks to do the parsing or leave empty. NOTE should be in an array
5. **self.extravariable** set if you wish to have default url e.g: http://fullsite.com/ or in laravel {{url}} or in php <?php echo $url; ?> or you leave it blank to point locally

6. This script automatically correct all link pointing to each folders associated with his extensions
# DEPENDANCE
1. pymy.py follow this github url to download it <a href="https://gist.github.com/wellbornbaba/98f2ada227245bc4fea4b9635eb91556">https://gist.github.com/wellbornbaba/98f2ada227245bc4fea4b9635eb91556</a>
2. Beautiful Soup. install "pip install Beautifulsoup"****

# HOW TO USE
1. **self.grabinput** = 'http://downloadmysite.com'

2. run the code
3. once finish running look for folder at the saved directory **self.defaultdownloadfolder**

. Thanks for using this software
You can contact us directly wemediaent@gmail.com for more suggestions or complaints
We are working to include more functions
