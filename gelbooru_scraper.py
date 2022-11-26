
import os
import shutil
import requests
import bs4
import threading
import queue


'''
problem:
	
some tags are uploaded to so frequently (e.g. rating:general)
that when another request for a PAGE is made (using &pid=),
the previously scraped images on the page have already
shifted to the right in position 
since the last time a PAGE was requested,
causing some images in the downloads folder
to be written to MORE THAN ONCE, resulting in 
less than the expected amount of images scraped
'''


BASE_SEARCH_URL = 'https://gelbooru.com/index.php?page=post&s=list'


def stringify_tags(tags: list[str]) -> str:
	return '+'.join(tags).replace(':', '%3a')


def get_image_thumbnails(**kwargs) -> list[bs4.Tag]:

	''' 
	valid kwargs: 
		start_idx: int,
		end_idx: int,
		tags: list[str]
	'''

	session = requests.Session()
	start_idx: int = kwargs['start_idx'] if 'start_idx' in kwargs else 0
	end_idx: int = kwargs['end_idx'] if 'end_idx' in kwargs else -1
	tags: list[str] = kwargs['tags'] if 'tags' in kwargs else []
	page_start_idx: int = start_idx
	thumbnails: list[bs4.Tag] = []
	
	is_next_page_needed = True
	while is_next_page_needed:	
		resp = session.get(
			BASE_SEARCH_URL 
			+ f'&tags={stringify_tags(tags)}' 
			+ f'&pid={page_start_idx}'
		)
		soup = bs4.BeautifulSoup(resp.text, features='lxml')
		
		if end_idx == -1:
			thumbnails += \
				[img for img in soup.find_all('img') \
				if 'img3' in img['src']]
			is_next_page_needed = True
		else:
			expected_length = end_idx - start_idx + 1
			for img in soup.find_all('img'):
				if not 'img3' in img['src']:
					continue
				thumbnails.append(img)
				if len(thumbnails) == expected_length:
					return thumbnails
			is_next_page_needed = page_start_idx <= end_idx
		# break if length of thumbnails has not changed from last iteration
		# i.e. blank page reached, ends
		
		if page_start_idx == len(thumbnails):
			break
		page_start_idx = len(thumbnails)
	
	return thumbnails


def scrape_image_from_post(url, dir_path, session=None) -> None:
	if session is None:
		resp = requests.get(url)
	else:
		resp = session.get(url)
	
	soup = bs4.BeautifulSoup(resp.text, features='lxml')
	img: bs4.Tag = soup.find('img', {'id': 'image'})
	
	if session is None:
		img_resp = requests.get(img['src'], stream=True)
	else:
		img_resp = session.get(img['src'], stream=True)
	
	with open(dir_path + '/' + img['src'].split('/')[-1], 'wb') as f:
		shutil.copyfileobj(img_resp.raw, f)


def scrape_worker(scrape_queue, dir_path, session) -> None:
	while not scrape_queue.empty():
		scrape_image_from_post(
			scrape_queue.get(),
			dir_path,
			session
		)
		scrape_queue.task_done()


def main():
	if not os.path.exists('gelbooru_scraper_downloads/'):
		os.mkdir('gelbooru_scraper_downloads')


def test():

	main()
	
	dir_path = 'gelbooru_scraper_downloads'
	session = requests.Session()
	
	ths = get_image_thumbnails(
		start_idx=0,
		end_idx=100,
		tags=['kakifly']
	)
	print(len(ths)) #dbg
	
	q = queue.Queue()
	for th in ths:
		post_link = th.parent['href']
		q.put(post_link)
	
	max_threads = 30
	for _ in range(max_threads):
		t = threading.Thread(
			target=scrape_worker,
			args=(q, dir_path, session),
			daemon=True
		)
		t.start()
	
	q.join()


if __name__ == '__main__':
	test()


