from django.shortcuts import render, get_object_or_404
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.generic import FormView
from urllib.parse import urlparse
from scrapyd_api import ScrapydAPI
from uuid import uuid4
from googlesearch import search
from .forms import IndexFrom
from .models import SiteData
import copy


scrapyd = ScrapydAPI('http://localhost:6800')

class IndexView(FormView):
    template_name = 'main_app/index.html'
    form_class = IndexFrom
    success_url = '/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_keyword = None
        self.search_count = None
        self.task_id = None
        self.unique_id = None
        self.google_results = None
        self.site_data = None
        self.status = None

    def get(self, request, *args, **kwargs):
        self.search_keyword = request.GET.get('search_keyword')
        self.search_count = request.GET.get('search_count')
        self.task_id = request.GET.get('input_task_id')
        self.unique_id = request.GET.get('input_unique_id')
        self.google_results = self.google_search(request)
        self.crawl(request)
        self.fetch_site_data_from_db(request)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # はじめに継承元のメソッドを呼び出す
        context['search_keyword'] = self.search_keyword
        context['search_count'] = self.search_count
        context['google_results'] = self.google_results
        context['task_id'] = self.task_id
        context['unique_id'] = self.unique_id
        context['status'] = self.status
        context['site_data'] = self.site_data
        print(self.site_data)
        self.extract_url_for_link()
        return context

    def get_initial(self):
        """フォームに動的な初期値を渡している"""
        initial = super().get_initial()
        initial['input_task_id'] = self.task_id
        initial['input_unique_id'] = self.unique_id
        return initial

    def google_search(self, request):
        """1ページ10件、stop=2で20件のグーグルの検索結果を返す。
        最大で50までとなっているindex.htmlで20～50の値を選べる。変数名serach_count
        searchで帰ってくるのはジェネレーター"""
        if request.method == 'GET' and self.search_keyword:

            try:
                google = []
                for url in search(self.search_keyword,
                                  lang='jp',
                                  stop=int(self.search_count),
                                  user_agent='Mozilla/5.0 (Windows NT 6.1)'
                                  'AppleWebKit/537.36 (KHTML, like Gecko)'
                                  'Chrome/28.0.1500.63 Safari/537.36'
                                  ):
                    google.append(copy.deepcopy(url))

                return google

            # この例外の方法は正しくないかもしれない。
            # エラーを表示する事はセキュリティ上よくないかもしれない じゃあどうするべきなのか
            except Exception as e:
                print('検索の段階でエラーが発生しました')
                print(str(type(e)))
                print(str(e.args))
                print(str(e))

    def crawl(self, request):
        """
        検索結果のurlのリストから最初のurlだけを1つ抜き出してトリガーとしてscrapyを動かしている
        urlリストはモデルからDBへ
        """
        if request.method == 'GET' and self.google_results and self.search_keyword:
            url = self.google_results  # 最初のurlだけをトリガーに使ってscrapyを動かす
            if not url[0]:
                return JsonResponse({'error': 'Missing  args'})

            if not is_valid_url(url[0]):
                return JsonResponse({'error': 'URL is invalid'})

            domain = urlparse(url[0]).netloc
            self.unique_id = str(uuid4())
            site_data = SiteData()
            site_data.unique_id = self.unique_id

            site_data.google_results = self.google_results
            site_data.save()
            settings = {
                'unique_id': self.unique_id,  # unique ID for each record for DB
                'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',

            }

            # 第一引数にscrapyのプルジェクト名、第二引数にスパイダー名をいれる
            self.task_id = scrapyd.schedule('scrapy_app',
                                            'blogspider',
                                            settings=settings,
                                            url=url[0],
                                            domain=domain,
                                            unique_id=self.unique_id,
                                            )

            return JsonResponse({'task_id': self.task_id, 'unique_id': self.unique_id, 'status': 'started'})
            # 大事なのはこのjsonでschedulを送ることそれでscrapydが働いてくれる

    def fetch_site_data_from_db(self, request):
        if request.method == 'GET'and self.task_id and self.unique_id:
            if not self.task_id or not self.unique_id:
                return JsonResponse({'error': 'Missing args'})

            self.status = scrapyd.job_status('scrapy_app', self.task_id)
            # 第一引数にscrapyのプロジェクト名を入れる

            if self.status == 'finished':
                try:
                    item = SiteData.objects.get(unique_id=self.unique_id)
                    # クロール前に作成したunique_idをつかってモデルからdataをとりだす
                    self.site_data = item.to_dict['site_data']

                    return JsonResponse({'data': item.to_dict['site_data']})

                except Exception as e:

                    return JsonResponse({'error': str(e)})
            else:
                return JsonResponse({'status': self.status})

    def extract_url_for_link(self):
        # d = []
        d = self.site_data
        print(d)
        # for i in self.site_data:

            # d.append(i.get('url'))
        # return(d)

def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True
