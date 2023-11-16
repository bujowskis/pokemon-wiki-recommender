import scrapy
from scrapy.utils.misc import Item
from ..items import ArticleItem
from bs4 import BeautifulSoup

class PokemonSpider(scrapy.Spider):
  name = 'pokemon_spider'
  start_urls = ['https://bulbapedia.bulbagarden.net/wiki/Category:Pok%C3%A9mon']

  def parse(self, response):
    if 'Category:Pok%C3%A9mon' in response.url:
      print(f'***** *** list page url={response.url}')
      yield from self.parse_list_page(response)
    elif response.url.endswith('(Pok%C3%A9mon)'):
      print(f'***** *** article page url={response.url}')
      yield from self.parse_article_page(response)

  def parse_list_page(self, response):
    # parse all articles
    links = response.css('div#mw-pages a').extract()

    possibly_next_list_page = None
    article_links = []
    for link in links:
      soup = BeautifulSoup(link, 'html.parser')
      text = soup.a.get_text()
      href = soup.a['href']
      if text.endswith('(Pokémon)'):
        article_links.append(response.urljoin(href))
      elif text == 'next page':
        possibly_next_list_page = response.urljoin(href)
        
    for link in article_links:
      yield scrapy.Request(url=response.urljoin(link), callback=self.parse)
    
    # if next list page, parse it
    if possibly_next_list_page is not None:
      print(f'***** *** next list page url={possibly_next_list_page}')
      yield scrapy.Request(url=possibly_next_list_page, callback=self.parse)
    
  
  def parse_article_page(self, response):
    print(f"***** *** parse article url={response.url}")
    
    paragraphs = response.css('div#mw-content-text p').extract()
    texts = [BeautifulSoup(paragraph, 'html.parser').get_text() for paragraph in paragraphs]

    item = ArticleItem()
    item['url'] = response.url
    item['name'] = response.css('h1#firstHeading::text').get().removesuffix(' (Pokémon)')
    item['text'] = ' '.join(texts)

    yield item
