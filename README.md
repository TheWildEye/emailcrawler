# emailcrawler
Email crawler to find emails from a website.
For best usecase and to understand the crawling process, you can use the TigerCrawler.py which crawls and shows step by step crawling of the website and then provides email in the output.

On the other hand if you want emails directly you can use DirectCrawler.py which crawls in the backend using multiple thread workers and provides all the emails in the output.

FOR KALI LINUX USERS: Bash

git clone https://github.com/TheWildEye/emailcrawler.git

cd emailcrawler

python3 TigerCrawler.py

or

python3 DirectCrawler.py

FOR WINDOWS USERS: Powershell/cmd

git clone https://github.com/TheWildEye/emailcrawler.git

You need to install dependencies:
3 Dependencies :
1.requests
2.beautifulsoup4
3.lxml

python -m pip install --upgrade pip

python.exe -m pip install --upgrade pip (if it asks)

python -m pip install requests beautifulsoup4 lxml

ALL SET:

python TigerCrawler.exe

or

python DirectCrawler.exe


Tool Made by - Vyom Nagpal

For any queries - Contact - 234tiger234@gmail.com

