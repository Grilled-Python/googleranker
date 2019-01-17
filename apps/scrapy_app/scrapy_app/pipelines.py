# -*- coding: utf-8 -*-
from apps.main_app.models import SiteData
import json


class ScrapyAppPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        self.count_rank = 0  # 検索順位をカウント
        self.unique_id = unique_id
        self.items = []
        self.dict = {}

    @classmethod
    def from_crawler(cls, crawler):
        # このクラスメソッドが呼び出されてからパイプラインインスタンスを作成する。
        # 引数にクラスがあるので、クラス変数にアクセスできる
        return cls(
            unique_id=crawler.settings.get('unique_id')  # djangoのviewsを通ってくる
        )

    def close_spider(self, spider):
        # spiderが閉じた時呼び出される itemsをjson形式でdjangoモデルに保存する
        site_data = SiteData.objects.get(pk=self.unique_id)
        site_data.site_data = json.dumps(self.items)
        site_data.save()

    def process_item(self, item, spider,):
        """ここでスパイダーからのitemをまとめclose_spiderでsaveへ"""
        # 検索順位をrankとして追加している

        self.count_rank += 1
        item['rank'] = self.count_rank
        self.items.append(item.copy())
        return item


if __name__ == '__main__':
    pass