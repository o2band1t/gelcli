import os
from datetime import datetime
from gelbooru_scraper import *
from DEFUNCT_threaded_thumbnail_scraper import *


## threaded ##

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


### non-threaded ###

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


### test batch 2 ###

def test_threaded_thumbnail_2():
	ths: set = threaded_get_image_thumbnails(
		tags=['outdoors', '1girl', 'rating:general'],
		page_start_num=0,
		end_num=-1,
		max_threads=10
	)
	print(len(ths)) #dbg
	print('threaded done')


def test_thumbnail_2():
	session = requests.session()
	ths = get_image_thumbnails(['outdoors', '1girl', 'rating:general'], 0, -1)
	print(len(ths))
	print('non-threaded done')


######

def test_batch_2():
	
	t1 = datetime.now()
	test_threaded_thumbnail_2()
	t2 = datetime.now()
	print((t2 - t1).seconds)
	
	t1 = datetime.now()
	test_thumbnail_2()
	t2 = datetime.now()
	print((t2 - t1).seconds)


	# max threads 10

	# findings with ['1boy', 'outdoors', 'rating:general'] :
	# non-threaded thumbnail scraper is faster (for images up to ~4600)
	# non-threaded thumbnail scraper consistently returns correct results
	# threaded thumbnail scraper does not always return consistent results
		# first try came back at only ~2900 thumbnails
	
	# findings with ['1girl', 'outdoors', 'rating:general'] :
	# non-threaded thumbnail scraper is faster (even for images up to ~16900)
	# non-threaded thumbnail scraper consistently returns correct results
	# threaded thumbnail scraper does not always return consistent results
		# first try cme back at only ~2000 thumbnails


if __name__ == '__main__':
	test_batch_2()
	


