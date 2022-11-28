
from gelbooru_scraper import *


## Tests ##

def test_threaded_thumbnail():
	'''
	if not os.path.exists('gelbooru_scraper_downloads/'):
		os.mkdir('gelbooru_scraper_downloads')

	dir_path = 'gelbooru_scraper_downloads'
	session = requests.Session()
	'''
	ths: set = threaded_get_image_thumbnails(
		tags=['outdoors', 'rating:general', '1girl'],
		page_start_num=0,
		end_num=-1,
		max_threads=30
	)	
	print(len(ths)) #dbg
	#for th in ths:
	#	print(th['src']) #dbg
	'''
	q = queue.Queue()
	for th in ths:
		post_link = th.parent['href']
		q.put(post_link)
	
	max_threads = 30
	for _ in range(max_threads):
		t = threading.Thread(
			target=_download_worker,
			args=(q, dir_path, session),
			daemon=True
		)
		t.start()
	
	q.join()
	'''


def test_threaded_thumbnail_1():
	ths: set = threaded_get_image_thumbnails(
		tags=['kakifly'],
		page_start_num=0,
		end_num=-1,
		max_threads=10
	)
	print(len(ths)) #dbg


def test_thumbnail():

	session = requests.Session()
	
	ths = get_image_thumbnails(['kakifly'], 0, -1)
	print(len(ths)) #dbg
	
	'''
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
	'''


if __name__ == '__main__':
	test_thumbnail()
	test_threaded_thumbnail_1()


