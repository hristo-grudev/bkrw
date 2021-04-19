import scrapy

from scrapy.loader import ItemLoader

from ..items import BkrwItem
from itemloaders.processors import TakeFirst


class BkrwSpider(scrapy.Spider):
	name = 'bkrw'
	start_urls = ['https://bk.rw/media?q=all']

	def parse(self, response):
		post_links = response.xpath('//div[@class="bloc-in"]')
		for post in post_links:
			url = post.xpath('.//h4/a/@href').get()
			date = post.xpath('.//span[@class="date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//a[@class="page-link"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//p[@class="intro"]//text()[normalize-space()]').get()
		description = response.xpath('//div[@class="page-content col-md-12"]/div[@class="col-md-12"][last()]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BkrwItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
