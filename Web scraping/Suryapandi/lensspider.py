import scrapy
import json

class LenskartSpider(scrapy.Spider):
    name = 'lensspider'
    start_urls = ['https://api-gateway.juno.lenskart.com/v2/products/category/3363?page-size=15&page=0']
    page_number = 0

    def parse(self, response):
        data = json.loads(response.body)
        product_list = data['result']['product_list']

        for product in product_list:
            item = {}
            item['id']   = product.get('id','')
            item['colour'] = product.get('color', '')
            item['size'] = product.get('size', '')
            item['width'] = product.get('width', '')
            item['brand'] = product['brand_name']
            item['model'] = product['model_name']
            item['price'] = product['prices'][1]['price']
            item['type'] = product['classification']
            item['count'] = product.get('purchaseCount', '')
            item['rating'] = product.get('avgRating', '')
            item['no_rating'] = product.get('totalNoOfRatings', 0)
            item['link'] = product['product_url']
            yield item

            # Request individual product page and parse details
            # yield scrapy.Request(item['link'], callback=self.parse_product, meta={'item': item})

        # Simulate scrolling and fetch next page
        self.page_number += 1
        next_page = f'https://api-gateway.juno.lenskart.com/v2/products/category/3363?page-size=15&page={self.page_number}'
        yield scrapy.Request(next_page, callback=self.parse)

    # def parse_product(self, response):
    #     item = response.meta['item']
    #     item['product_id'] = response.css('span.TechInfoVal--jmyd3g::text').get()
    #     yield item
