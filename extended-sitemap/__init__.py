# -*- coding: utf-8 -*-
import os

from codecs import open

from pelican import signals, contents
from pelican.utils import get_date

from pprint import pprint

from urlparse import urljoin


class SitemapGenerator(object):
    """
    Class for generating a sitemap.xml.
    """

    xml_wrap = """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="%(SITEURL)s/sitemap-stylesheet.xsl"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%(urls)s
</urlset>"""

    template_url = """<url>
<loc>%(loc)s</loc>
<lastmod>%(lastmod)s</lastmod>
<changefreq>%(changefreq)s</changefreq>
<priority>%(priority).2f</priority>
</url>"""

    settings_default = {
        'priorities': {
            'indexes': 1.0,
            'articles': 0.8,
            'pages': 0.5,
        },
        'changefrequencies': {
            'indexes': 'daily',
            'articles': 'weekly',
            'pages': 'monthly',
        }
    }

    def __init__(self, context, settings, path, theme, output_path, **kwargs):
        # TODO documentation
        self.path_content = path
        self.path_output = output_path
        self.context = context
        self.url_site = settings.get('SITEURL')
        self.settings = settings.get('EXTENDED_SITEMAP_PLUGIN', self.settings_default)

    def generate_output(self, writer):
        """
        Generates the sitemap file and the stylesheet file and puts them into the content dir.
        :param writer: the writer instance
        :type writer: pelican.writers.Writer
        """
        # TODO remove
        # pprint(self.context, indent=4)

        # write xml stylesheet
        with open(os.path.join(os.path.dirname(__file__), 'sitemap-stylesheet.xsl'), 'r', encoding='utf-8') as fd_origin:
            with open(os.path.join(self.path_output, 'sitemap-stylesheet.xsl'), 'w', encoding='utf-8') as fd_destination:
                xsl = fd_origin.read()
                # replace some template markers
                # TODO use pelican template magic
                xsl = xsl.replace('{{ SITENAME }}', self.context.get('SITENAME'))
                fd_destination.write(xsl)

        urls = ''

        def content_datetime_compare(x, y):
            """
            Compares two pelican.contents.Content classes with each other based on their date property.
            :param x: first content element
            :type x: pelican.contents.Content
            :param y: second content element
            :type x: pelican.contents.Content
            :returns: if x is before y
            :rtype: bool
            """
            return x.date > y.date

        # TODO process indexes

        # process articles
        for article in sorted(self.context['articles'], cmp=content_datetime_compare):
            urls += self.template_url % {
                'loc': urljoin(self.url_site, self.context.get('ARTICLE_URL').format(**article.url_format)),
                # W3C YYYY-MM-DDThh:mm:ssTZD
                'lastmod': article.date.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'changefreq': self.settings.get('changefrequencies').get('articles'),
                'priority': self.settings.get('priorities').get('articles'),
            }

        # TODO process pages

        # write the final sitemap file
        with open(os.path.join(self.path_output, 'sitemap.xml'), 'w', encoding='utf-8') as fd:
            fd.write(self.xml_wrap % {
                'SITEURL': self.url_site,
                'urls': urls
            })


def get_generators(generators):
    """
    Returns the generators of this plugin,
    :param generators: current generators
    :type generators: pelican.Pelican
    :returns: the sitemap generator type
    :rtype: type
    """
    return SitemapGenerator


def register():
    """
    Registers the sitemap generator.
    """
    signals.get_generators.connect(get_generators)