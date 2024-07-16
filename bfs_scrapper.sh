#!/bin/bash

# Your command to run in nohup
nohup scrapy crawl b_for_sale_data &

# Wait for the command to complete
wait $!

# Send an email notification
echo "Business For Sale Scrapper has completed running." | mail -s "Command Completion Notification" malhotra.vikas@gmail.com
