import json
from django.db import models
from django.utils import timezone


class SiteData(models.Model):
    unique_id = models.CharField(primary_key=True, max_length=100, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    google_results = models.TextField(blank=True)
    site_data = models.TextField(blank=True)  # クロールしたdataはpipelinesから送られてくる

    @property
    def to_dict(self):
        """ # viewsからmodelを呼び出した際、json形式で呼び出すための関数"""
        site_data = {
            'site_data': json.loads(self.site_data),
            'created_at': self.created_at,


        }
        return site_data

