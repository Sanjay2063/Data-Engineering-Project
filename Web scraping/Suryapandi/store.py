import scrapy


class StoreSpider(scrapy.Spider):
    name = "store"
    allowed_domains = ["lenskart.com"]
    start_urls = ["https://www.lenskart.com/stores"]

    def parse(self, response):
        stores = response.css('div.StoreCard_storeAddressContainer__pBYqN')
        for store in stores:
            location = store.css('a.StoreCard_name__mrTXJ::text').get()
            address = store.css('a.StoreCard_storeAddress__PfC_v ::text').get()
            phone = store.css('div.StoreCard_wrapper__xhJ0A ::text').getall()
            if len(phone) >= 3:
                phone_number = phone[2]
            else:
                phone_number = 0
            ratings = store.css('div.StoreCard_rating__CPC2K ::text').get()
            ratings_c = store.css('div.StoreCard_reviewCount__FT2tY ::text').getall()
            if len(ratings_c) >= 3:
                ratings_count = ratings_c[1]
            else:
                ratings_count = 0
            yield {
                'location': location,
                'address': address,
                'phone_number': phone_number,
                'ratings': ratings,
                'ratings_count': ratings_count
            }
        urls = response.css('a.undefined::attr(href)').getall()
        url_names = response.css('a.undefined::text').getall
        for url in urls :
            next_page_url = f"https://www.lenskart.com/{url}"
            yield scrapy.Request(next_page_url, callback=self.parse)

