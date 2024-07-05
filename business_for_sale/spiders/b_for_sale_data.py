from listingDescriptionHandler import generate_readable_description, generate_readable_title_withAI, generate_image_from_AI
import scrapy
import csv
import json
from datetime import datetime
import dotenv
import re

dotenv.load_dotenv()

class BForSaleDataSpider(scrapy.Spider):
    name = "b_for_sale_data"

    def extractCategory(self, url):
        # Use a regular expression to find the relevant segment in the URL
        match = re.search(r"/us/search/([^?]+)", url)
        if match:
            # Extract the segment found by the regex
            segment = match.group(1)
            # Replace dashes with spaces and capitalize each word
            formatted_segment = ' '.join(word.capitalize() for word in segment.split('-'))
            return formatted_segment
        return "Category not found"
    
    def start_requests(self):
        # Path to the input file
        file_path = '/Users/vikas/builderspace/business_for_sale/input_urls/businessforsale_url.txt'

        with open(file_path, 'r') as file:
            lines = file.readlines()
            # Process each line
            for line in lines:
                line = line.strip()  # Remove any leading/trailing whitespace
                if line:
                    # Split the line on comma to extract category and URL
                    parts = line.split(',')
                    if len(parts) >= 2:
                        category = parts[0].strip()
                        url = parts[1].strip()

                        # Send the request with the category included in the meta data
                        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        
        url = response.url
        print(" url is to be scrapped ", url)
        category = self.extractCategory(url)

        if '/franchises/' in url:
            yield from self.parse_franchise(response)
        elif '/us/search/' in url:
            yield from self.parse_business(response)
        elif '.aspx' in url:
            yield from self.extract_business_data(response, category)
        else:
            self.logger.error(f'URL pattern not recognized: {url}')

    def parse_franchise(self, response):
        listing_urls = response.css("dd.listing-title a::attr(href)").getall()
        for url in listing_urls:
            yield scrapy.Request(url, callback=self.extract_franchise_data, meta={'listing_url': url,})

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_franchise)

    def extract_franchise_data(self, response):
        listing_url = response.meta.get('listing_url')
        title = response.css(".brochureTitle::text").get()
        description = response.css("#summary p::text").get()
        franchise_fee = response.css("li#financialInfo dl:nth-of-type(1) dd::text").get()
        minimum_investment = response.css("li#financialInfo dl:nth-of-type(2) dd::text").get()
        available_areas = response.css("#availableAreas p::text").get()

        def safe_strip(value):
            return value.strip() if value else value

        item = {
            'Listing URL': listing_url,
            'Title': safe_strip(title),
            'Description': safe_strip(description),
            'Franchise Fee': safe_strip(franchise_fee),
            'Minimum Investment': safe_strip(minimum_investment),
            'Available Areas': safe_strip(available_areas),
        }

        # self.write_to_csv('franchise_data.csv', item)
        self.write_to_json('franchise_data.json', item)
        yield item

    def parse_business(self, response):
        listing_urls = response.css("h2 a::attr(href)").getall()
    
        for url in listing_urls:
            if '/franchises/' in url:
                yield scrapy.Request(url, callback=self.extract_franchise_data, meta={'listing_url': url,})
            else:
                yield scrapy.Request(url, callback=self.extract_business_data, )

        next_page = response.css(".next-link a::attr(href)").get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_business, )

    def extract_business_data(self, response, category):
        listing_url = response.url
        article_id = response.css('#listing-id::text').get()
        businesses_title = response.css("h1::text").get()
        businesses_title = businesses_title.replace('\r', '').replace('\n', '')

        address = response.css("#address").xpath('string()').get()
        address = address.replace('\r', '').replace('\n', '')

        asking_price = response.css('div.overview-details dl.price dd span strong::text').get()
        sales_revenue = response.css('div.overview-details dl#revenue dd strong::text').get()
        cash_flow = response.css('div.overview-details dl#profit dd strong::text').get()

        property_information = self.extract_information(response, 'div#property-information')
        business_operation = self.extract_information(response, 'div#business-operation')
        other_information = self.extract_information(response, 'div#other-information')

        raw_business_description = response.css('.section-break:nth-child(1)').xpath('string()').get()
        cleaned_business_description = ' '.join([desc.strip() for desc in raw_business_description if desc.strip()])
        cleaned_business_description = cleaned_business_description.replace('\r', '').replace('\n', '')
        scraped_business_description_text = cleaned_business_description if cleaned_business_description else 'NA'
        generated_image_url = "https://publiclistingphotos.s3.amazonaws.com/no-photo.jpg"

        if (scraped_business_description_text and scraped_business_description_text != 'NA' and scraped_business_description_text != ""):
            business_description = generate_readable_description(scraped_business_description_text)

            generated_image_url = generate_image_from_AI(business_description, article_id, businesses_title)            
        else:
            business_description = scraped_business_description_text

        if (business_description and business_description != 'NA' and business_description != ""):
            title = generate_readable_title_withAI(business_description)
        else:
            title = 'NA'

        image_url = response.css(".gallery::attr(href)").get()

        def safe_strip(value):
            return value.strip() if value else value

        computed_category = category
        broker_listing_party = "broker_listing_party"
        broker_phone = "broker_phone"
        broker_name = "broker_name"

        item = {
            "ad_id": str(safe_strip(article_id))+"_BFS",
            "source": "BusinessForSale",
            "article_url": listing_url,
            "category": computed_category,
            'Title': safe_strip(title),
            'location': safe_strip(address),
            'image_url': image_url,
            "businessListedBy": broker_listing_party,
            "broker-phone": broker_phone,
            "broker-name": broker_name,
            'asking_price': safe_strip(asking_price),
            'cash_flow': safe_strip(cash_flow),
            'gross_revenue': safe_strip(sales_revenue),
            'scraped_business_description': scraped_business_description_text,
            'business_description': business_description,
            'generate_image_from_AI': generated_image_url,
            'property_information': property_information,
            'business_operation': business_operation,
            'other_information': other_information,
            'listing_para': safe_strip(raw_business_description),
        }

        # Get today's date in the format YYYYMMDD
        today_date = datetime.now().strftime("%Y%m%d")

        outputfile = 'business_for_sale_data'+today_date+'.json'

        # self.logger.debug(f'Business data extracted: {item}')
        # self.write_to_csv('business_data.csv', item)
        self.write_to_json(outputfile, item)
        yield item

    @staticmethod
    def write_to_csv(filename, item):
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=item.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(item)

    @staticmethod
    def write_to_json(filename, item):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        data.append(item)
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def extract_information(response, selector):
        section = response.css(selector)
        data = {}
        for dl in section.css('dl.listing-details'):
            dt = dl.css('dt::text').get().strip()
            dd = dl.css('dd p::text, dd::text').getall()
            dd = ' '.join([d.strip() for d in dd if d.strip()])
            data[dt] = dd
        return data
