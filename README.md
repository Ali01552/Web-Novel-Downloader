## Novel Scraper: Download and Convert Light Novels to Epub

This Python application scrapes light novels from various websites and converts them into a downloadable epub file.

### Features

- Supports multiple Table of Content (TOC) formats
- Download chapters asynchronously for faster retrieval
- Handles websites with Cloudflare protection
- Generates epub with chapters and (optional) cover image

### Installation

1. Make sure you have Python 3 installed.
2. Clone this repository using `git clone https://github.com/Ali01552/Web-Novel-Downloader.git`
3. Install required libraries by running `pip install -r requirements.txt` in your terminal (navigate to the cloned directory first).

### Usage

1. Create a configuration file named `config.ini` in the same directory as the script (`App.py`).
2. Edit `config.ini` according to the instructions below.
3. Run the script using `python App.py config.ini`

### Configuration (`config.ini`):

```makefile
[Novel-Info]
Novel-Name: The name of the light novel you want to download.
Chapters-No: The total number of chapters in the light novel.
chapter-container-selector: CSS selector for the element containing each chapter content. (Inspect the website's HTML to find this)
title-selector: (Optional) CSS selector for the element containing the chapter title. (Leave blank if the chapter title is not retrievable)
home-page: The website's homepage URL.

[TOC1] (for TOC with predictable chapter links):
chapter 2nd url: The URL pattern for the second chapter (remove chapter number from the url).
chapter 3rd url: The URL pattern for the third chapter (remove chapter number from the url).

[TOC2] (for TOC in a separate webpage):
mode(p-u): Choose "p" to provide the file path of the TOC webpage (HTML), or "u" to provide the URL of the TOC webpage.
url of the content page (if mode is "u"): The URL of the webpage containing the chapter links.
selector of the content page links: CSS selector for the elements containing the chapter links in the content webpage.
path of the content page (html file) (if mode is "p"): The file path of the HTML file containing the chapter links.

[TOC3] (for TOC spread across multiple pages):
link of the 2nd page: The URL of the second TOC page.
link of the 3rd page: The URL of the third TOC page.
number of pages: The total number of TOC pages.
selector of the content page links: CSS selector for the elements containing the chapter links in each TOC page.

[scrap-mode]
mode-number(1-2): Choose "1" for asynchronous chapter download (faster) or "2" for synchronous download (may be slower).

[Cover] (Optional)
cover-path: The file path of the image you want to use as the epub cover. Enter "0" to skip cover image.
```

Note that the configuration file uses the INI format, and the `config.ini` file should be placed in the same directory as the `App.py` script.

