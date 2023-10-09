print("Loading Modules....")
import os
from termcolor import colored
from bs4 import BeautifulSoup as bs
import cloudscraper as sc
#from syn import syn
import time as ti
#import aiohttp
import asyncio
from aiocfscrape import CloudflareScraper

print(colored("Modules Loaded...","blue"))


class scraper():
	def __init__(self,name):
		self.name = name
		try:
			os.mkdir(self.name)
		except:
			os.system(f"rm -r '{self.name}'")
			os.mkdir(self.name)
		self.path = self.name+"/"
		self.csr = sc.create_scraper()
		self.failed_cha = {}
		self.failed_content = {}
		self.n = 1
		self.content_page_nums = 0
		self.contnet_pages = []

		self.chp_num = 0
		self.ch_selector = ""
		self.title_selector = None
		self.chap_links = []
		self.chap_links_t = []
		self.chap_links_copy = []
		
		self.cls = sc.create_scraper()
		self.counter = 0


	def con_pages(self,l1,l2,n):	#links of 2nd and 3rd pages and no of pages
		selecor = ["",""]
		c = 0
		index = []
		for x,y in zip(l1,l2):
			if x==y:
				pass
			else:
				selecor[0]+=x
				selecor[1]+=y
				index.append(c)
			c+=1
		links = []
		x = list(l1)
		for z in index:
			x[z] = '{}'
		for i in range(int(selecor[0])-1, n+1):
			l1 = ''.join(x).format(*[str(i)]*len(index))
			links.append(l1)
		return links

	def get_TOC_1(self,url): #url without the number of chapter
		#chapter links the same but change in last number
		for n in range(1,self.chp_num+1):
			print(colored(url+str(n),'green'))
			self.chap_links.append(url+str(n))
			self.chap_links_t.append(url+str(n))


	def get_TOC_2(self,path=None,url=None,selector=None, parentsite=None): #Load the TOC Html file or All chapters in the same url
		#Use the file method if the chapters cant be loaded except with javascript
		if path != None and url == None:
			with open(path, 'r', encoding="UTF-8") as f:
				x = f.read()
			soup = bs(x, "html.parser")
			links_tags = soup.select(selector)
			for i in links_tags:
				if "http" in i["href"]:
					self.chap_links.append(i["href"])
					print(colored(i["href"],'green'))
				else:
					self.chap_links.append(parentsite+i['href'])
					self.chap_links_t.append(parentsite+'/'+i['href'])
					print(colored(parentsite+i['href'],'green'))
		else:
			r = self.csr.get(url).text
			soup = bs(r, "html.parser")
			links_tags = soup.select(selector)
			for i in links_tags:
				if "http" in i["href"]:
					self.chap_links.append(i["href"])
					print(colored(i["href"],'green'))
				else:
					self.chap_links.append(parentsite+i['href'])
					self.chap_links_t.append(parentsite+'/'+i['href'])
					print(colored(parentsite+i['href'],'green'))

	def remove_sp_char(self,text):
		sp_char = "',.;:][(/\\)~!@#$%^&*_+=><?"
		n_tx = text
		for i in n_tx:
			if i in sp_char:
				n_tx = n_tx.replace(i,"")
		return n_tx


	def get_TOC_3(self,link, selector, parentsite=None):  #Table of content have more than one page		
		try:
			r = self.csr.get(link).text
		except Exception as e:
			self.failed_content[link] = e
			raise
		soup = bs(r, "html.parser")
		links_tags = soup.select(selector)
		try:
			for i in links_tags:
				if "http" in i["href"]:
					self.chap_links.append(i["href"])
					print(colored(i["href"],'green'))
				else:
					self.chap_links.append(parentsite+i["href"])
					self.chap_links_t.append(parentsite+'/'+i["href"])
					print(colored(parentsite+i['href'],'green'))
		except Exception as e:
			self.failed_content[link] = e
			raise


	def get_chap(self,ch,ch_selector, title_selector,name):
		soup = bs(ch, "html.parser")
		if title_selector != None:
			title = self.remove_sp_char(soup.select(title_selector)[0].text)
		else:
			title = f"Chapter {name}"
		chap = soup.select(ch_selector)
		with open(f"./{self.name}/{name}.html", "w" ,encoding="UTF-8") as f:
			f.write(f"<h1>{title}</h1>\n")
			for x in chap:
				f.write(str(x))
		self.n+=1


	def N_Req(self):
		n_results = []
		for l in self.chap_links:
			code = 0
			while code != 200:
				try:
					r = self.cls.get(l)
					if r.status_code == 200:
						n_results.append(r.text)
						print(f"{l} : {colored(r.status_code,'green')} \nHandeled ({self.counter}) requests")
						self.get_chap(r.text,ch_selector=self.ch_selector,title_selector=self.title_selector,name=self.counter)
						self.counter+=1
						code = 200
					else:
						print(colored(l+" : "+str(r.status_code)+" ...Bad response\nRetrying... Handeled ("+str(self.counter)+") requests",'red'))
						ti.sleep(2)
				except Exception as e:
					print(e)
					print(colored("Error Encountered.\nRtrying",'red'))
					ti.sleep(10)
					continue
		return n_results



	async def fetch(self,session, url,name):
		code = 0
		n = 1
		while code != 200:
			try:
				async with session.get(url) as response:
					if response.status == 200:
						print(f"{url} : {colored(response.status,'green')} \nHandeled ({self.counter}) requests")
						print(colored(f"Parsing results.. ({str(self.counter)}/{len(self.chap_links_copy)})","blue"))
						self.get_chap(await response.text(),ch_selector=self.ch_selector,title_selector=self.title_selector,name=name)
						code = 200
						self.counter+=1
						return await response.text()
					else:
						print(colored(url+" : "+str(response.status)+" ...Bad response\nRetrying... Handeled ("+str(self.counter)+") requests",'red'))
						asyncio.sleep(2)
			except Exception as e:
				print(e)
				print(colored("Error Encountered.\nRtrying",'red'))
				continue

	async def fetch_all(self,urls):
		async with CloudflareScraper() as session:
			tasks = []
			c = 1
			for url in urls:
				task = asyncio.ensure_future(self.fetch(session, url,c))
				tasks.append(task)
				c+=1
			responses = await asyncio.gather(*tasks)
			return responses

	def main(self):
		#self.loop = asyncio.get_event_loop()
		#self.results = self.loop.run_until_complete(self.fetch_all(self.chap_links))
		asyncio.run(self.fetch_all(self.chap_links))
		print("")



	def get_all_chaps_asyn(self,urls):
		print(colored("initiating...", "green"))
		#self.gett = syn(urls, self.name)
		print(colored("Generated URLs...", "green"))
		print(colored("Downloading start...", "green"))
		print("=="*50)
		self.main()
		print(colored("Done Downloading chapters", "red"))
		print("=="*50)
		print("=="*50)
		counter = 1
		'''for r in self.gett.results:
			print(colored(f"Parsing results.. ({str(counter)}/{len(self.gett.results)})","blue"))
			self.get_chap(r,ch_selector=self.ch_selector,title_selector=self.title_selector)
			counter+=1'''

	def get_all_chaps_syn(self,urls):
		print(colored("initiating...", "green"))
		#self.gett = syn(urls, self.name)
		print(colored("Generated URLs...", "green"))
		print(colored("Downloading start...", "green"))
		print("=="*50)
		rr = self.N_Req()
		print(colored("Done Downloading chapters", "red"))
		print("=="*50)
		print("=="*50)
	'''	counter = 1
		for r in rr:
			print(colored(f"Parsing results.. ({str(counter)}/{len(rr)})","blue"))
			self.get_chap(r,ch_selector=self.ch_selector,title_selector = self.title_selector)
			counter+=1'''








if __name__ == "__main__":
	print("=="*50)
	os.system("figlet 'Novel Scraper'")
	print("=="*50)
	name = input(colored("Enter Novel Name: ", "green"))
	novel = scraper(name)
	########################################## CH_NUMBERS ###################################################
	checker = True
	while checker:
		try:
			n = int(input(colored("Enter the number of chapters: ", "green")))
			checker = False
		except ValueError:
			print(colored("Please Enter a valid number","red"))
	novel.chp_num = n
	############################################# CH SELECTOR ################################################
	ch_s = input(colored("Enter Chapter Container selector: ",'blue'))
	novel.ch_selector = ch_s
	############################################ TITLE #################################################
	checker = True
	while checker:
		ti_s = input(colored("Enter Title selector (if no press Enter): ",'blue'))
		if ti_s == "":
			novel.title_selector = None
			print(colored("Please Enter a Title Selector", "red"))
		else:
			novel.title_selector = ti_s
			checker = False
	########################################### TOC ##################################################	
	checker4 = True
	while checker4:
		toc = input(colored("Choose table of content type\n\t1)TOC1\n\t2)TOC2\n\t3)TOC3\n\t: ","green"))
		if toc == '1':
			toc1_url1 = input(colored("Enter a chapter's 2nd URL without the number: ",'green'))
			toc1_url2 = input(colored("Enter a chapter's 3rd URL without the number: ",'green'))
			novel.chap_links = novel.con_pages(toc1_url1,toc1_url2,novel.chp_num)
			novel.chap_links_copy = novel.chap_links
			print()
			print(colored("Got TOC!!", "blue"))
			print("=="*50)
			input(f"Got {len(novel.chap_links)} Links")
			checker4 = False
		################################################
		elif toc == '2':
			checker2 = True
			while checker2:
				sub_toc2 = input(colored("Choose TOC2 path or URL (p or u): ",'green'))
				if sub_toc2 in "uU":
					toc2_url = input(colored("Enter the URL of the Content page: ",'yellow'))
					toc2_Uselector = input(colored("Enter the Selector of the Content page links: ",'yellow'))
					toc2_Psite = input(colored("Enter the Home page of the Website (being scraped): ",'yellow'))
					novel.get_TOC_2(url=toc2_url, selector=toc2_Uselector, parentsite=toc2_Psite)
					novel.chap_links_copy = novel.chap_links
					print()
					print(colored("Got TOC!!", "blue"))
					print("=="*50)
					input(f"Got {len(novel.chap_links)} Links")
					checker2 = False
					checker4 = False
				###################
				elif sub_toc2 in "pP":
					toc2_path = input(colored("Enter the path of the Content page (HTML File): ",'yellow'))
					toc2_Pselector = input(colored("Enter the Selector of the Content page links: ",'yellow'))
					toc2_Psite = input(colored("Enter the Home page of the Website (being scraped): ",'yellow'))
					novel.get_TOC_2(path=toc2_path, selector=toc2_Pselector, parentsite=toc2_Psite)
					novel.chap_links_copy = novel.chap_links
					print()
					print(colored("Got TOC!!", "blue"))
					print("=="*50)
					input(f"Got {len(novel.chap_links)} Links")
					checker2 = False
					checker4 = False
				####################
				else:
					print(colored("Please Enter a valid choice p or u", "red"))
			##############################################
		elif toc == '3':
			print(colored("It seems that the TOC page have more than one page\n ","red"))
			l1 = input(colored("Enter the link of the 2nd page: ",'green'))
			l2 = input(colored("Enter the link of the 3rd page: ",'green'))
			checker3 = True
			while checker3:
				try:
					pn = int(input(colored("Enter the number of pages: ",'green')))
					checker3 = False
				except ValueError:
					print(colored("Please Enter a valid number", 'red'))
			urls = novel.con_pages(l1,l2,pn)
			toc3_Psite = input(colored("Enter the Home page of the Website (being scraped): ",'green'))
			toc3_s = input(colored("Enter the Selector of the Content page links: ",'green'))
			for i in urls:
				novel.get_TOC_3(i,toc3_s,toc3_Psite)
			print()
			novel.chap_links_copy = novel.chap_links
			print(colored("Got TOC!!", "blue"))
			input(f"Got {len(novel.chap_links)} Links")
			print("=="*50)
			checker4 = False
			##############################################
		else:
			print(colored("Please Enter a vaild choice (1,2 or 3)", "red"))
			continue

		#############################################################################################
	new_check = True
	while new_check:
		mode = input("1) Hard mode\n2) Soft mode\nPlease Chose 1 or 2: ")
		if mode == '1':
			print("=="*50)
			print(colored("Starting...",'red'))
			novel.get_all_chaps_asyn(novel.chap_links)
			print()
			print("=="*50)
			input(colored("Press any key to quit...","blue"))
			new_check = False
		elif mode == '2':
			print("=="*50)
			print(colored("Starting...",'red'))
			novel.get_all_chaps_syn(novel.chap_links)
			print()
			print("=="*50)
			input(colored("Press any key to quit...","blue"))
			new_check = False
		else:
			print(colored("Please Enter a Valid Choice..","red"))
			continue



