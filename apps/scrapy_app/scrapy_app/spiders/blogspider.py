# -*- coding: utf-8 -*-

import scrapy
from scrapy import Request
from apps.main_app.models import SiteData
from collections import OrderedDict

"""
$ scrapy crawl blogspider
ファイルでスパイダーを動かすコマンド
"""


class BlogSpider(scrapy.Spider):
    name = 'blogspider'  # Spiderの名前。これが無いと動かない

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.unique_id = kwargs.get('unique_id')  # viewsから
        self.start_urls = [self.url]
        self.item = OrderedDict()

        super(BlogSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        # データベースから取り出した文字列から不必要なものを取り除いてlistしてscrapyに渡している
        site_data = SiteData.objects.get(pk=self.unique_id)
        google_results = site_data.google_results
        urls = google_results.translate(str.maketrans({"[": None, "]": None, "'": None, ",": None})).split()
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        """ タイトル、ディスクリプションh1~h6までを取得
        response.xpath('//h1/text()').extract())
        1ページ内のすべてのh1タグを取得している
        list(s.strip().translate(str.maketrans({'\r': None, '\n': None, '\t': None}))
        改行文字を空白文字に置き換えている
        list(filter(lambda str: str != '', list
        lambda式を使用して変換してできた空白文字をlist内から削除している
        """
        item = self.item
        item['url'] = response.url
        item['title'] = ' '.join(s.strip().translate({
            '\r': None, '\n': None, '\t': None}) for s in response.xpath('//title/text()').extract_first())
        item['description'] = ' '.join(s.strip().translate({'\r': None, '\n': None, '\t': None}) for s in
                                       response.xpath('/html/head/meta[@name="description"]/@content').extract_first())
        item['h1'] = list(filter(lambda str: str != '', list(s.strip().translate(str.maketrans({
            '\r': None, '\n': None, '\t': None})) for s in response.xpath('//h1/text()').extract())))
        item['h2'] = list(filter(lambda str: str != '', list(s.strip().translate(str.maketrans({
            '\r': None, '\n': None, '\t': None})) for s in response.xpath('//h2/text()').extract())))
        item['h3'] = list(filter(lambda str: str != '', list(s.strip().translate(str.maketrans({
            '\r': None, '\n': None, '\t': None})) for s in response.xpath('//h3/text()').extract())))
        item['h4'] = list(filter(lambda str: str != '', list(s.strip().translate(str.maketrans({
            '\r': None, '\n': None, '\t': None})) for s in response.xpath('//h4/text()').extract())))
        item['h5'] = list(filter(lambda str: str != '', list(s.strip().translate(str.maketrans({
            '\r': None, '\n': None, '\t': None})) for s in response.xpath('//h5/text()').extract())))
        item['h6'] = list(filter(lambda str: str != '', list(s.strip().translate(str.maketrans({
            '\r': None, '\n': None, '\t': None})) for s in response.xpath('//h6/text()').extract())))

        yield item




if __name__ == '__main__':
    pass
