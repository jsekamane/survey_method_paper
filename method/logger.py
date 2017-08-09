# coding=utf-8

import logging

# Keep log of GET requests and the corresponding RESPONSE.
logger = logging.getLogger('fetch_data')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('log/fetch_data.log')
formatter = logging.Formatter('%(asctime)s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def log(response):
    # Log response status, response time in milliseconds and length of content.
    logger.info('GET %s' % response.url)
    logger.info('RESPONSE status %s time %s size %s' % (response.status_code, round(response.elapsed.total_seconds()*1000), len(response.content)) )