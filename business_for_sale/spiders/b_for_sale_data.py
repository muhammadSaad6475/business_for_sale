from listingDescriptionHandler import generate_readable_description, generate_readable_title_withAI, generate_image_from_AI, resize_and_convert_image
import scrapy
import csv
import json
from datetime import datetime
import dotenv
import re
import os
import boto3


dotenv.load_dotenv()
NEW_IMAGE_SCRAPPED_SQS_URL = os.environ.get("NEW_IMAGE_SCRAPPED_SQS_URL")


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
                url = line.strip()  # Remove any leading/trailing whitespace
                if url:
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
        category = self.extractCategory(response.url)  # Extract category once for all listings on the page

        for url in listing_urls:
            if '/franchises/' in url:
                yield scrapy.Request(url, callback=self.extract_franchise_data, meta={'listing_url': url,})
            else:
                category = self.extractCategory(response.url)
                yield scrapy.Request(url, callback=self.extract_business_data, meta={'category': category})

        next_page = response.css(".next-link a::attr(href)").get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_business, )

    def extract_business_data(self, response):
        listing_url = response.url
        category = response.meta['category']  # This should correctly extract the category

        article_id = response.css('#listing-id::text').get()
        if (article_id):
            article_id = article_id.strip()
            article_id = article_id.replace('\r', '').replace('\n', '')

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
        print("raw_business_description is", raw_business_description)

        #cleaned_business_description = ' '.join([desc.strip() for desc in raw_business_description if desc.strip()])
        raw_business_description = raw_business_description.replace('\r', '').replace('\n', '')
        scraped_business_description_text = raw_business_description if raw_business_description else 'NA'
        generated_image_url = "https://publiclistingphotos.s3.amazonaws.com/no-photo.jpg"

        print("scraped_business_description_text is", scraped_business_description_text)
        ai_images_dict = {}

        if (scraped_business_description_text and scraped_business_description_text != 'NA' and scraped_business_description_text != ""):
            business_description = generate_readable_description(scraped_business_description_text)

            ai_images_dict = generate_image_from_AI(business_description, article_id, businesses_title)

        else:
            business_description = scraped_business_description_text

        if (business_description and business_description != 'NA' and business_description != ""):
            title = generate_readable_title_withAI(business_description)
        else:
            title = 'NA'

        scrapped_image_url = response.css(".gallery::attr(href)").get()

        dynamic_dict = []
        dynamic_dict.append(ai_images_dict)
#        dynamic_dict.update(ai_images_dict)

        print("dynamic_dict after AI Image Dict", dynamic_dict)

        print("dynamic_dict after AI Image Dict", json.dumps(dynamic_dict))

        if scrapped_image_url:
            scrapped_images_dict = {}
            # Sizes you want to resize your image to
            sizes = [(851, 420), (526, 240), (146, 202), (411, 243), (265, 146)]
            s3_object_key = article_id+"_BFS_Scrapped.png"

            for size in sizes:
                resized_s3_url = resize_and_convert_image(scrapped_image_url, size, s3_object_key)
                key = f"{size[0]}x{size[1]}"
                scrapped_images_dict[key] = resized_s3_url

            dynamic_dict.append(scrapped_images_dict)
            

            print("dynamic_dict after Scrapped Image Dict", dynamic_dict)

            print("dynamic_dict after Scrapped Image Dict", json.dumps(dynamic_dict))

            # Send a message to the Scrapped Queue
            # Now send a SNS message so that the image can be processed
            # Prepare a JSON message with the S3 URL and the file name
            message = {
                "article_id": article_id,
                "s3_url": scrapped_image_url,
            }
            # send_sns_message
            #send_sqs_message(NEW_IMAGE_SCRAPPED_SQS_URL, message, article_id)

        def safe_strip(value):
            return value.strip() if value else value

        def extract_lower_range(range):
            # Remove dollar sign and whitespace
            clean_range = range.replace('$', '').replace(' ', '')

            # Check if the input is a range
            if '-'  in clean_range:            
                # Split the range into lower and upper bounds
                lower_bound = clean_range.split('-')[0]
            else:
                lower_bound = clean_range
            
            # Convert to absolute number
            if 'K' in lower_bound:
                lower_bound = int(float(lower_bound.replace('K', '')) * 1000)
            elif 'M' in lower_bound:
                lower_bound = int(float(lower_bound.replace('M', '')) * 1000000)
            else:
                lower_bound = int(lower_bound)
            
            return lower_bound

        computed_category = category
        broker_listing_party = "broker_listing_party"
        broker_phone = "broker_phone"
        broker_name = "broker_name"

        print("dynamic_dict ready to be written", dynamic_dict)
        print("dynamic_dict ready to be written", json.dumps(dynamic_dict))

        cash_flow = safe_strip(cash_flow)
        cash_flow = extract_lower_range(cash_flow)

        sales_revenue = safe_strip(sales_revenue)
        sales_revenue = extract_lower_range(sales_revenue)

        item = {
            "ad_id": str(safe_strip(article_id))+"_BFS",
            "source": "BusinessForSale",
            "article_url": listing_url,
            "category": computed_category,
            'Title': safe_strip(title),
            'location': safe_strip(address),
            'listing-photos': json.dumps(dynamic_dict),
            "businessListedBy": broker_listing_party,
            "broker-phone": broker_phone,
            "broker-name": broker_name,
            'asking_price': safe_strip(asking_price),
            'cash_flow': cash_flow,
            'gross_revenue': sales_revenue,
            'scraped_business_description': scraped_business_description_text,
            'business_description': business_description,
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
        data = []

        # Check if the file exists and is not empty before trying to load it
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)  # Load existing data
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file {filename}. Starting with an empty list.")
                    # If JSON is corrupt, start with an empty list
                    data = []

        # Append new item to the list
        data.append(item)

        # Always open the file in write mode to overwrite existing content or create new
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

def upload_to_s3(file_name, bucket, object_name=None):
    """
    Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_name is used
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except Exception as e:
        return False
    return True


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
