import os
import shutil
import requests
import bs4
import threading
import queue


BASE_SEARCH_URL = 'https://gelbooru.com/index.php?page=post&s=list'


def _stringify_tags(tags: list[str]) -> str:
	return '+'.join(tags).replace(':', '%3a')


def _download_worker(scrape_queue, dir_path, session) -> None:
	while not scrape_queue.empty():
		download_image_from_post(
			scrape_queue.get(),
			dir_path,
			session
		)
		scrape_queue.task_done()


# API for scraping gelbooru

def get_image_thumbnails(tags, page_start_num, end_num) -> list[bs4.Tag]:
	'''
	warning:

	some tags are uploaded to so frequently (e.g. rating:general)
	that when another request for a PAGE is made (using &pid=),
	the previously scraped images on the page have already
	shifted to the right in position 
	since the last time a PAGE was requested,
	causing some images in the downloads folder
	to be written to MORE THAN ONCE, resulting in 
	less than the expected amount of images scraped
	'''
	session = requests.Session()
	page_start1_idx: int = page_start_num
	thumbnails: list[bs4.Tag] = []	
	while True:	
		resp = session.get(
			BASE_SEARCH_URL 
			+ f'&tags={_stringify_tags(tags)}' 
			+ f'&pid={page_start1_idx}'
		)
		soup = bs4.BeautifulSoup(resp.text, features='lxml')
		thumbnails_on_page = \
			[img for img in soup.find_all('img') if 'img3' in img['src']]
		# break if blank page
		if len(thumbnails_on_page) == 0:
				break
		if end_num == -1:
			thumbnails += thumbnails_on_page
		else:
			expected_length = end_num - page_start_num + 1
			thumbnails += thumbnails_on_page[:expected_length]
			if len(thumbnails) == expected_length:
				break
		# break if length of thumbnails has not changed from last iteration
		# i.e. blank page reached, ends
		if page_start1_idx == len(thumbnails):
			break
		page_start1_idx = len(thumbnails)
	return thumbnails


def download_image_from_post(url, dir_path, session=None) -> None:
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


def download_images(**kw) -> None:
	tags = kw['tags'] if 'tags' in kw else []
	dir_path = kw['dir_path'] if 'dir_path' in kw else 'gelbooru_scraper_downloads/'
	quantity = kw['quantity'] if 'quantity' in kw else 1
	start = kw['start'] if 'start' in kw else 0
	max_threads = kw['max_threads'] if 'max_threads' in kw else 10
	
	session = requests.Session()
	thumbnails = get_image_thumbnails(tags, start, start + quantity - 1)
	q: queue.Queue[str] = queue.Queue()
	for img in thumbnails:
		q.put(img.parent['href'])
	
	threads = []
	for _ in range(max_threads):
		threads.append(
			threading.Thread(
				target=_download_worker,
				args=(q, dir_path, session),
				daemon=True
			)
		)
	for t in threads:
		t.start()
	for t in threads:
		t.join()


