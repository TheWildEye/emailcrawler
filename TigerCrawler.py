#!/usr/bin/env python3
# ─── TIGER MAIL CRAWLER BANNER ────────────────────────────────────────────────
# switch to bright yellow (ANSI 256 color)
print("\033[38;5;226m")
print(r"""

░██████████░██                            ░███     ░███          ░██░██  ░██████                                  ░██                   
    ░██                                   ░████   ░████             ░██ ░██   ░██                                 ░██                   
    ░██    ░██ ░████████ ░███████ ░██░████░██░██ ░██░██ ░██████  ░██░██░██       ░██░████░██████ ░██    ░██    ░██░██ ░███████ ░██░████ 
    ░██    ░██░██    ░██░██    ░██░███    ░██ ░████ ░██      ░██ ░██░██░██       ░███         ░██░██    ░██    ░██░██░██    ░██░███     
    ░██    ░██░██    ░██░█████████░██     ░██  ░██  ░██ ░███████ ░██░██░██       ░██     ░███████ ░██  ░████  ░██ ░██░█████████░██      
    ░██    ░██░██   ░███░██       ░██     ░██       ░██░██   ░██ ░██░██ ░██   ░██░██    ░██   ░██  ░██░██ ░██░██  ░██░██       ░██      
    ░██    ░██ ░█████░██ ░███████ ░██     ░██       ░██ ░█████░██░██░██  ░██████ ░██     ░█████░██  ░███   ░███   ░██ ░███████ ░██      
                     ░██                                                                                                                
               ░███████                                                                                                                 

""")
# reset color
print("\033[0m")
# ─── END BANNER ───────────────────────────────────────────────────────────────

import requests
from bs4 import BeautifulSoup
from collections import deque
import urllib.parse
import re

def crawl_emails(start_url, max_urls=100, timeout=5):
    urls_to_visit = deque([start_url])
    visited_urls = set()
    found_emails = set()
    count = 0

    while urls_to_visit and count < max_urls:
        count += 1
        url = urls_to_visit.popleft()
        visited_urls.add(url)

        print(f"[{count}] Processing: {url}")
        try:
            response = requests.get(url, timeout=timeout)
            content = response.text

            # Extract emails
            emails_on_page = set(re.findall(
                r'[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+',
                content, re.I
            ))
            found_emails.update(emails_on_page)

            # Parse links
            soup = BeautifulSoup(content, "lxml")
            parts = urllib.parse.urlsplit(url)
            base_url = f"{parts.scheme}://{parts.netloc}"
            path = url[:url.rfind("/") + 1] if "/" in parts.path else url

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"].strip()
                if href.startswith(("mailto:", "tel:", "javascript:", "#", "ftp:")):
                    continue

                if href.startswith("/"):
                    link = base_url + href
                elif href.startswith("http"):
                    link = href
                else:
                    link = urllib.parse.urljoin(path, href)

                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)

        except (requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.InvalidURL) as e:
            print(f"[-] Skipped ({e.__class__.__name__}): {url}")
            continue
        except Exception as e:
            print(f"[-] Unexpected error [{e}]: {url}")
            continue

    return found_emails

def main():
    user_input = input("[+] Enter your target URL to scan: ").strip()
    if not user_input.startswith(("http://", "https://")):
        print("[-] Please include http:// or https:// in the URL.")
        return

    emails = crawl_emails(user_input)

    print("\n[+] Emails found:")
    if emails:
        for mail in sorted(emails):
            print(" -", mail)
    else:
        print("No emails found.")

if __name__ == "__main__":
    main()
