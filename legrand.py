import scrapy
from scrapy_splash import SplashRequest
import time


class legrand(scrapy.Spider):
    name = 'leg'
    allowed_domains = ['www.legrand.us']
    start_urls = ['https://www.legrand.us/pass-and-seymour']
    base_url = 'https://www.legrand.us/'

    def parse(self, response, **kwargs):
        for cat in response.xpath('.//li[@class="first-level"]'):
            subcategory = cat.xpath('.//a/text()').get().strip()
            category = "Wiring Devices"
            cat_link = cat.xpath('.//a/@href').get().strip()
            absolute_url = response.urljoin(cat_link)
            time.sleep(2)
            yield SplashRequest(url=absolute_url, callback=self.parse_product, meta={'category': category,'subcategory': subcategory})

    def parse_product(self, response):
        category = response.request.meta['category']
        subcategory = response.request.meta['subcategory']
        bread = response.xpath('.//ol[@class="breadcrumb"]/li/a/text()').getall()
        crumb = response.xpath('.//ol[@class="breadcrumb"]/li[@class="active"]/text()').get().strip()
        bread.append(crumb)
        for products in response.xpath('.//a[@class="product__list--name js-link-switch"]'):
            product_link = products.xpath('.//@href').get()
            Title = products.xpath('.//text()').get().strip()
            bread.append(Title)
            breadcrumb = '/'.join(bread)
            bread.remove(Title)
            absolute_url1 = response.urljoin(product_link)
            time.sleep(2)
            yield SplashRequest(url=absolute_url1, callback=self.parse_item, meta={'category': category, 'subcategory': subcategory, 'breadcrumb': breadcrumb,'Title':Title})
        next_page = response.xpath(".//li[@class='pagination-next']/a/@href").get()
        if next_page:
            abs_url = f"https://www.legrand.us{next_page}"
            yield scrapy.Request(
                url=abs_url,
                callback=self.parse_product
            )

    def parse_item(self, response):
        category = response.request.meta['category']
        subcategory = response.request.meta['subcategory']
        title = response.request.meta['Title']
        url = response.url
        breadcrumb = response.request.meta['breadcrumb']
        img = response.xpath('.//div[@class="lr-img-wp"]/img[@class="owl-lazy"]/@data-src').getall()
        num = int(len(img)/2)
        img_1 = img[:num]
        img_2 = img[num:]
        full_img = []
        for zoom, normal in zip(img_1, img_2):
            img_dict = {
                'Zoom_image': zoom,
                'Item_image': normal,
            }
            full_img.append(img_dict)
        product_id = response.xpath('.//span[@class="lr-product-info--item sku"]/text()').get().strip()
        price = response.xpath('.//p[@class="price"]/span/text()').get().strip().replace('$', '')
        features = response.xpath('.//ul[@class="list-unstyled lr-features-list"]/li/span/text()').getall()
        features_list = ' | '.join(features)
        description = response.xpath('.//div[@class="description js-product-description"]/text()').get().strip()
        doc_text = response.xpath('.//div[@class="lr-resources-group"]/div/a/div[@class="lr-resource-name"]/text()').getall()
        doc_link = response.xpath('.//div[@class="lr-resources-group"]/div/a/@href').getall()
        doc_dict = {}
        for key, value in zip(doc_text, doc_link):
            doc_dict[key] = value
        manufacturer = response.xpath('.//span[@class="lr-product-info--item brand"]/text()').get().strip()
        spec = [i.strip() for i in response.xpath('.//div[@class="product-classifications"]/table/tbody/tr/td/text()').getall()]
        while "" in spec:
            spec.remove("")
        i = 0
        spec_dict = {}
        while i < len(spec) - 1:
            spec_dict[spec[i]] = spec[i + 1]
            i = i + 2

        for index, i in enumerate(spec):
            if i == "UPC Number":
                upc = spec[index+1]
                break
        yield {
            "URL": url,
            "Product ID": product_id,
            "Title": title,
            "Category": category,
            "Subcategory": subcategory,
            "Brand": "Pass & Seymour",
            "Breadcrumb": breadcrumb,
            'UPC Number': upc,
            'Manufacturer': manufacturer,
            "Price": price,
            'Description': description,
            "Features": features_list,
            'specifications': spec_dict,
            'IMG url': full_img,
            'Resources': doc_dict,
        }

