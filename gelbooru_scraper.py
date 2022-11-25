
'''
todo:

- review python threading
- write function to multithread downloading the images
'''

####

import requests
import bs4
import threading


BASE_SEARCH_URL = 'https://gelbooru.com/index.php?page=post&s=list'


def stringify_tags(tags: list[str]) -> str:
	return '+'.join(tags).replace(':', '%3a')


def get_image_thumbnails(**kwargs) -> list[bs4.Tag]:

	''' 
	valid kwargs: 
		page_start_idx: int,
		end_idx: int,
		tags: list[str]
	'''

	session = requests.Session()

	start_idx: int = kwargs['page_start_idx'] if 'page_start_idx' in kwargs else 0
	end_idx: int = kwargs['end_idx'] if 'end_idx' in kwargs else -1
	tags: list[str] = kwargs['tags'] if 'tags' in kwargs else []
	
	page_start_idx: int = start_idx
	
	thumbnails: list[bs4.Tag] = []
	
	do_again = True
	
	while do_again:
		
		resp = session.get(
			BASE_SEARCH_URL 
			+ f'&tags={stringify_tags(tags)}' 
			+ f'&pid={page_start_idx}'
		)
		
		soup = bs4.BeautifulSoup(resp.text, features='lxml')

		if end_idx == -1:
		
			thumbnails += \
				[img['src'] for img in soup.find_all('img') \
				if 'img3' in img['src']]
		
			do_again = True

		else:
		
			for img in soup.find_all('img'):
		
				if not 'img3' in img['src']:
					continue
		
				thumbnails.append(img)
		
				if len(thumbnails) > (end_idx - start_idx):
					return thumbnails

			do_again = page_start_idx <= end_idx

		# break if length of thumbnails has not changed from last iteration
		# i.e. blank page reached, ends
		if page_start_idx == len(thumbnails):
			break
		
		page_start_idx = len(thumbnails)
 
	return thumbnails


def test():

	start = 20
	end = 110

	thumbnails: list[bs4.Tag] = get_image_thumbnails(
		tags=['rating:general'],
		page_start_idx=start,
		end_idx=end
	)

	for i, thumbnail in enumerate(thumbnails, start=start):
		print(f'{i} -- {thumbnail.parent["href"]}')
	
	# Visit each URL of the parent link of the thumbnail
	# and extract the URL of the image
	# then download it.
	
	# Use multithreading.


if __name__ == '__main__':
	test()


