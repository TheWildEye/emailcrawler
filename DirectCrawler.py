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

DEVELOPED BY - VYOM NAGPAL """)
# reset color
print("\033[0m")
# ─── END BANNER ───────────────────────────────────────────────────────────────

import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

# ─── CONFIG ──────────────────────────────────────────────────────────────────
MAX_URLS    = 100
MAX_WORKERS = 10
TIMEOUT     = 5

# reuse TCP connections & set a custom UA
session = requests.Session()
session.headers.update({"User-Agent": "TigerMailCrawler/1.0"})

# compile a stricter email regex
EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
# extensions to filter out
BAD_EXTS = (".png", ".jpg", ".jpeg", ".webp")

def fetch(url):
    try:
        resp = session.get(url, timeout=TIMEOUT)
        return url, resp.text
    except Exception:
        return url, None

def crawl_emails_parallel(start_url):
    seen     = {start_url}
    emails   = set()
    to_crawl = [start_url]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        # kick off initial batch
        futures = {pool.submit(fetch, to_crawl.pop(0)): True}

        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)

            for fut in done:
                url, html = fut.result()
                futures.pop(fut)

                if not html:
                    continue

                # extract emails and filter out image-like
                found = set(EMAIL_REGEX.findall(html))
                found = {e for e in found if not e.lower().endswith(BAD_EXTS)}
                emails |= found

                # parse out links
                parts = urllib.parse.urlsplit(url)
                base  = f"{parts.scheme}://{parts.netloc}"
                path  = url[:url.rfind("/") + 1] if "/" in parts.path else url

                soup = BeautifulSoup(html, "lxml")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith(("mailto:", "tel:", "#", "javascript:", "ftp:")):
                        continue
                    if href.startswith("/"):
                        link = base + href
                    elif href.startswith("http"):
                        link = href
                    else:
                        link = urllib.parse.urljoin(path, href)

                    if link not in seen and len(seen) < MAX_URLS:
                        seen.add(link)
                        to_crawl.append(link)

                # refill pool up to MAX_WORKERS
                while to_crawl and len(seen) <= MAX_URLS and len(futures) < MAX_WORKERS:
                    next_url = to_crawl.pop(0)
                    futures[pool.submit(fetch, next_url)] = True

    return emails

def main():
    user_input = input("[+] Enter your target URL to scan: ").strip()
    if not user_input.startswith(("http://", "https://")):
        print("[-] Please include http:// or https:// in the URL.")
        return

    found = crawl_emails_parallel(user_input)
    print("\n[+] Emails found:")
    if found:
        for mail in sorted(found):
            print(" -", mail)
    else:
        print("No emails found.")

if __name__ == "__main__":
    main()
