# python-web-scrapping
Scrap web site contents, data mining and so on

# Import Notes

1. NOTE: 2 main folders will be created [PUBLIC] and [RESOURCES]
2. [PUBLIC] folder contain folders such as /fonts and /**images**
3. [RESOURCES] folder contain folders such as /js, /scss and /view
4. All .css files are automatically converted to .scss files and "app.scss" is created pointing to all found .scss files for easy structure formatting
5. All .js files are automatically move to /js folders and "app.js" is created pointing to all found .js files for easy structure formatting.
6. All .php files were rename to .blade.php while if any exclude folders are set will be ignored from renaming to .blade.php
7. if "global_shorten_laravelurl" is set it will automatically set a global variable to replace the main url {{url}} check the code
8. This script automatically correct all link pointing to each folders associated with his extensions
# DEPENDANCE
1. pymy.py follow this github url to download it <a href="https://gist.github.com/wellbornbaba/98f2ada227245bc4fea4b9635eb91556">https://gist.github.com/wellbornbaba/98f2ada227245bc4fea4b9635eb91556</a>
2. Beautiful Soup. install "pip install Beautifulsoup"****

# HOW TO USE
1. self.pathfile = r'C:\site'
point to the folder where your site is located
2. run the code
3. once finish running look for folder "_laravelbuild"
4. copy the folders according to your Laravel project and enjoy your easy works.
5. Good luck and happy coding

. Thanks for using this software
You can contact us directly wemediaent@gmail.com for more suggestions or complaints
We are working to include more functions
