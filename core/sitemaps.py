from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class MainViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"
    protocol = "https"

    def items(self):
        return ["conventions:index"]

    def location(self, item):
        return reverse(item)


class StaticViewSitemap(Sitemap):
    priority = 0.1
    changefreq = "daily"
    protocol = "https"

    def items(self):
        return ["cgu", "accessibilite", "stats:index"]

    def location(self, item):
        return reverse(item)


SITEMAPS = {
    "main": MainViewSitemap,
    "static": StaticViewSitemap,
}
