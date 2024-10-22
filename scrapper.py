from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException
)
from PIL import Image, ImageDraw, ImageFont
import io
import time
import os
import json
import logging
from urllib.parse import urlparse
import concurrent.futures
from tqdm import tqdm
import colorsys  # This is the correct import

# Define UI element classes for YOLO
CLASSES = [
    'link', 'button', 'input', 'select', 'textarea', 'label', 
    'checkbox', 'radio', 'dropdown', 'slider', 'toggle', 
    'menu_item', 'clickable', 'icon', 'image', 'text'
]

# Comprehensive list of websites categorized by UI patterns
WEBSITES = {
    # 'e_commerce': [
    #     'https://www.amazon.com',
    #     'https://www.ebay.com',
    #     'https://www.etsy.com',
    #     'https://www.walmart.com',
    #     'https://www.target.com',
    #     'https://www.bestbuy.com',
    #     'https://www.newegg.com',
    #     'https://www.wayfair.com'
    # ],
    # 'social_media': [
    #     'https://www.reddit.com',
    #     'https://www.pinterest.com',
    #     'https://www.tumblr.com',
    #     'https://www.quora.com',
    #     'https://www.linkedin.com'
    # ],
    # 'productivity': [
    #     'https://trello.com',
    #     'https://www.notion.so',
    #     'https://asana.com',
    #     'https://www.atlassian.com/software/jira',
    #     'https://clickup.com',
    #     'https://monday.com',
    #     'https://www.todoist.com',
    #     'https://www.anydo.com'
    # ],
    # 'development': [
    #     'https://github.com',
    #     'https://gitlab.com',
    #     'https://bitbucket.org',
    #     'https://stackoverflow.com',
    #     'https://developer.mozilla.org',
    #     'https://www.w3schools.com',
    #     'https://codepen.io',
    #     'https://replit.com'
    # ],
    # 'design': [
    #     'https://dribbble.com',
    #     'https://www.behance.net',
    #     'https://www.figma.com',
    #     'https://www.sketch.com',
    #     'https://www.canva.com',
    #     'https://www.adobe.com/products/xd.html'
    # ],
    # 'education': [
    #     'https://www.coursera.org',
    #     'https://www.udemy.com',
    #     'https://www.edx.org',
    #     'https://www.khanacademy.org',
    #     'https://www.duolingo.com',
    #     'https://www.codecademy.com'
    # ],
    # 'documentation': [
    #     'https://docs.python.org',
    #     'https://reactjs.org',
    #     'https://vuejs.org',
    #     'https://angular.io',
    #     'https://docs.microsoft.com',
    #     'https://kubernetes.io/docs'
    # ],
    # 'dashboards': [
    #     'https://grafana.com',
    #     'https://www.datadoghq.com',
    #     'https://newrelic.com',
    #     'https://www.elastic.co/kibana',
    #     'https://www.splunk.com'
    # ],
    'mostvisited':[
        "https://www.google.com",
        "https://www.blogger.com",
        "https://youtube.com",
        "https://linkedin.com",
        "https://support.google.com",
        "https://cloudflare.com",
        "https://microsoft.com",
        "https://apple.com",
        "https://en.wikipedia.org",
        "https://play.google.com",
        "https://wordpress.org",
        "https://docs.google.com",
        "https://mozilla.org",
        "https://maps.google.com",
        "https://youtu.be",
        "https://drive.google.com",
        "https://bp.blogspot.com",
        "https://sites.google.com",
        "https://googleusercontent.com",
        "https://accounts.google.com",
        "https://t.me",
        "https://europa.eu",
        "https://plus.google.com",
        "https://whatsapp.com",
        "https://adobe.com",
        "https://facebook.com",
        "https://policies.google.com",
        "https://uol.com.br",
        "https://istockphoto.com",
        "https://vimeo.com",
        "https://vk.com",
        "https://github.com",
        "https://amazon.com",
        "https://search.google.com",
        "https://bbc.co.uk",
        "https://google.de",
        "https://live.com",
        "https://gravatar.com",
        "https://nih.gov",
        "https://dan.com",
        "https://files.wordpress.com",
        "https://www.yahoo.com",
        "https://cnn.com",
        "https://dropbox.com",
        "https://wikimedia.org",
        "https://creativecommons.org",
        "https://google.com.br",
        "https://line.me",
        "https://googleblog.com",
        "https://opera.com",
        "https://es.wikipedia.org",
        "https://globo.com",
        "https://brandbucket.com",
        "https://myspace.com",
        "https://slideshare.net",
        "https://paypal.com",
        "https://tiktok.com",
        "https://netvibes.com",
        "https://theguardian.com",
        "https://who.int",
        "https://goo.gl",
        "https://medium.com",
        "https://tools.google.com",
        "https://draft.blogger.com",
        "https://pt.wikipedia.org",
        "https://fr.wikipedia.org",
        "https://www.weebly.com",
        "https://news.google.com",
        "https://developers.google.com",
        "https://w3.org",
        "https://mail.google.com",
        "https://gstatic.com",
        "https://jimdofree.com",
        "https://cpanel.net",
        "https://imdb.com",
        "https://wa.me",
        "https://feedburner.com",
        "https://enable-javascript.com",
        "https://nytimes.com",
        "https://workspace.google.com",
        "https://ok.ru",
        "https://google.es",
        "https://dailymotion.com",
        "https://afternic.com",
        "https://bloomberg.com",
        "https://amazon.de",
        "https://photos.google.com",
        "https://wiley.com",
        "https://aliexpress.com",
        "https://indiatimes.com",
        "https://youronlinechoices.com",
        "https://elpais.com",
        "https://tinyurl.com",
        "https://yadi.sk",
        "https://spotify.com",
        "https://huffpost.com",
        "https://ru.wikipedia.org",
        "https://google.fr",
        "https://webmd.com",
        "https://samsung.com",
        "https://independent.co.uk",
        "https://amazon.co.jp",
        "https://get.google.com",
        "https://amazon.co.uk",
        "https://4shared.com",
        "https://telegram.me",
        "https://planalto.gov.br",
        "https://businessinsider.com",
        "https://ig.com.br",
        "https://issuu.com",
        "https://www.gov.br",
        "https://wsj.com",
        "https://hugedomains.com",
        "https://picasaweb.google.com",
        "https://usatoday.com",
        "https://scribd.com",
        "https://www.gov.uk",
        "https://storage.googleapis.com",
        "https://huffingtonpost.com",
        "https://bbc.com",
        "https://estadao.com.br",
        "https://nature.com",
        "https://mediafire.com",
        "https://washingtonpost.com",
        "https://forms.gle",
        "https://namecheap.com",
        "https://forbes.com",
        "https://mirror.co.uk",
        "https://soundcloud.com",
        "https://fb.com",
        "https://marketingplatform.google....",
        "https://domainmarket.com",
        "https://ytimg.com",
        "https://terra.com.br",
        "https://google.co.uk",
        "https://shutterstock.com",
        "https://dailymail.co.uk",
        "https://reg.ru",
        "https://t.co",
        "https://cdc.gov",
        "https://thesun.co.uk",
        "https://wp.com",
        "https://cnet.com",
        "https://instagram.com",
        "https://researchgate.net",
        "https://google.it",
        "https://fandom.com",
        "https://office.com",
        "https://list-manage.com",
        "https://msn.com",
        "https://un.org",
        "https://de.wikipedia.org",
        "https://ovh.com",
        "https://mail.ru",
        "https://bing.com",
        "https://news.yahoo.com",
        "https://myaccount.google.com",
        "https://hatena.ne.jp",
        "https://shopify.com",
        "https://adssettings.google.com",
        "https://bit.ly",
        "https://reuters.com",
        "https://booking.com",
        "https://discord.com",
        "https://buydomains.com",
        "https://nasa.gov",
        "https://aboutads.info",
        "https://time.com",
        "https://abril.com.br",
        "https://change.org",
        "https://nginx.org",
        "https://twitter.com",
        "https://www.wikipedia.org",
        "https://archive.org",
        "https://cbsnews.com",
        "https://networkadvertising.org",
        "https://telegraph.co.uk",
        "https://pinterest.com",
        "https://google.co.jp",
        "https://pixabay.com",
        "https://zendesk.com",
        "https://cpanel.com",
        "https://vistaprint.com",
        "https://sky.com",
        "https://windows.net",
        "https://alicdn.com",
        "https://google.ca",
        "https://lemonde.fr",
        "https://newyorker.com",
        "https://webnode.page",
        "https://surveymonkey.com",
        "https://translate.google.com",
        "https://calendar.google.com",
        "https://amazonaws.com",
        "https://academia.edu",
        "https://apache.org",
        "https://imageshack.us",
        "https://akamaihd.net",
        "https://nginx.com",
        "https://discord.gg",
        "https://thetimes.co.uk",
        "https://search.yahoo.com",
        "https://amazon.fr",
        "https://yelp.com",
        "https://berkeley.edu",
        "https://google.ru",
        "https://sedoparking.com",
        "https://cbc.ca",
        "https://unesco.org",
        "https://ggpht.com",
        "https://privacyshield.gov",
        "https://www.over-blog.com",
        "https://clarin.com",
        "https://www.wix.com",
        "https://whitehouse.gov",
        "https://icann.org",
        "https://gnu.org",
        "https://yandex.ru",
        "https://francetvinfo.fr",
        "https://gmail.com",
        "https://mozilla.com",
        "https://ziddu.com",
        "https://guardian.co.uk",
        "https://twitch.tv",
        "https://sedo.com",
        "https://foxnews.com",
        "https://rambler.ru",
        "https://books.google.com",
        "https://stanford.edu",
        "https://wikihow.com",
        "https://it.wikipedia.org",
        "https://20minutos.es",
        "https://sfgate.com",
        "https://liveinternet.ru",
        "https://ja.wikipedia.org",
        "https://000webhost.com",
        "https://espn.com",
        "https://eventbrite.com",
        "https://disney.com",
        "https://statista.com",
        "https://addthis.com",
        "https://pinterest.fr",
        "https://lavanguardia.com",
        "https://vkontakte.ru",
        "https://doubleclick.net",
        "https://bp2.blogger.com",
        "https://skype.com",
        "https://sciencedaily.com",
        "https://bloglovin.com",
        "https://insider.com",
        "https://pl.wikipedia.org",
        "https://sputniknews.com",
        "https://id.wikipedia.org",
        "https://doi.org",
        "https://nypost.com",
        "https://elmundo.es",
        "https://abcnews.go.com",
        "https://ipv4.google.com",
        "https://deezer.com",
        "https://express.co.uk",
        "https://detik.com",
        "https://mystrikingly.com",
        "https://rakuten.co.jp",
        "https://amzn.to",
        "https://arxiv.org",
        "https://alibaba.com",
        "https://fb.me",
        "https://wikia.com",
        "https://t-online.de",
        "https://telegra.ph",
        "https://mega.nz",
        "https://usnews.com",
        "https://plos.org",
        "https://naver.com",
        "https://ibm.com",
        "https://smh.com.au",
        "https://dw.com",
        "https://google.nl",
        "https://lefigaro.fr",
        "https://bp1.blogger.com",
        "https://picasa.google.com",
        "https://theatlantic.com",
        "https://nydailynews.com",
        "https://themeforest.net",
        "https://rtve.es",
        "https://newsweek.com",
        "https://ovh.net",
        "https://ca.gov",
        "https://goodreads.com",
        "https://economist.com",
        "https://target.com",
        "https://marca.com",
        "https://kickstarter.com",
        "https://hindustantimes.com",
        "https://weibo.com",
        "https://finance.yahoo.com",
        "https://huawei.com",
        "https://e-monsite.com",
        "https://hubspot.com",
        "https://npr.org",
        "https://netflix.com",
        "https://gizmodo.com",
        "https://netlify.app",
        "https://yandex.com",
        "https://mashable.com",
        "https://cnil.fr",
        "https://latimes.com",
        "https://steampowered.com",
        "https://rt.com",
        "https://photobucket.com",
        "https://quora.com",
        "https://nbcnews.com",
        "https://android.com",
        "https://instructables.com",
        "https://www.canalblog.com",
        "https://www.livejournal.com",
        "https://ouest-france.fr",
        "https://tripadvisor.com",
        "https://ovhcloud.com",
        "https://pexels.com",
        "https://oracle.com",
        "https://yahoo.co.jp",
        "https://addtoany.com",
        "https://sakura.ne.jp",
        "https://cointernet.com.co",
        "https://twimg.com",
        "https://britannica.com",
        "https://php.net",
        "https://standard.co.uk",
        "https://groups.google.com",
        "https://cnbc.com",
        "https://loc.gov",
        "https://qq.com",
        "https://buzzfeed.com",
        "https://godaddy.com",
        "https://ikea.com",
        "https://disqus.com",
        "https://taringa.net",
        "https://ea.com",
        "https://dropcatch.com",
        "https://techcrunch.com",
        "https://canva.com",
        "https://offset.com",
        "https://ebay.com",
        "https://zoom.us",
        "https://cambridge.org",
        "https://unsplash.com",
        "https://playstation.com",
        "https://people.com",
        "https://springer.com",
        "https://psychologytoday.com",
        "https://sendspace.com",
        "https://home.pl",
        "https://rapidshare.com",
        "https://prezi.com",
        "https://photos1.blogger.com",
        "https://thenai.org",
        "https://ftc.gov",
        "https://google.pl",
        "https://ted.com",
        "https://secureserver.net",
        "https://code.google.com",
        "https://plesk.com",
        "https://aol.com",
        "https://biglobe.ne.jp",
        "https://hp.com",
        "https://canada.ca",
        "https://linktr.ee",
        "https://hollywoodreporter.com",
        "https://ietf.org",
        "https://clickbank.net",
        "https://harvard.edu",
        "https://amazon.es",
        "https://oup.com",
        "https://timeweb.ru",
        "https://engadget.com",
        "https://vice.com",
        "https://cornell.edu",
        "https://dreamstime.com",
        "https://tmz.com",
        "https://gofundme.com",
        "https://pbs.org",
        "https://stackoverflow.com",
        "https://abc.net.au",
        "https://sciencedirect.com",
        "https://ft.com",
        "https://variety.com",
        "https://alexa.com",
        "https://abc.es",
        "https://walmart.com",
        "https://gooyaabitemplates.com",
        "https://redbull.com",
        "https://ssl-images-amazon.com",
        "https://theverge.com",
        "https://spiegel.de",
        "https://about.com",
        "https://nationalgeographic.com",
        "https://bandcamp.com",
        "https://m.wikipedia.org",
        "https://zippyshare.com",
        "https://wired.com",
        "https://freepik.com",
        "https://outlook.com",
        "https://mit.edu",
        "https://sapo.pt",
        "https://goo.ne.jp",
        "https://java.com",
        "https://google.co.th",
        "https://scmp.com",
        "https://mayoclinic.org",
        "https://scholastic.com",
        "https://nba.com",
        "https://reverbnation.com",
        "https://depositfiles.com",
        "https://video.google.com",
        "https://howstuffworks.com",
        "https://cbslocal.com",
        "https://merriam-webster.com",
        "https://focus.de",
        "https://admin.ch",
        "https://gfycat.com",
        "https://com.com",
        "https://narod.ru",
        "https://boston.com",
        "https://sony.com",
        "https://justjared.com",
        "https://bitly.com",
        "https://jstor.org",
        "https://amebaownd.com",
        "https://g.co",
        "https://gsmarena.com",
        "https://lexpress.fr",
        "https://reddit.com",
        "https://usgs.gov",
        "https://bigcommerce.com",
        "https://gettyimages.com",
        "https://ign.com",
        "https://justgiving.com",
        "https://techradar.com",
        "https://weather.com",
        "https://amazon.ca",
        "https://justice.gov",
        "https://sciencemag.org",
        "https://pcmag.com",
        "https://theconversation.com",
        "https://foursquare.com",
        "https://flickr.com",
        "https://giphy.com",
        "https://tvtropes.org",
        "https://fifa.com",
        "https://upenn.edu",
        "https://digg.com",
        "https://bestfreecams.club",
        "https://histats.com",
        "https://salesforce.com",
        "https://blog.google",
        "https://apnews.com",
        "https://theglobeandmail.com",
        "https://m.me",
        "https://europapress.es",
        "https://washington.edu",
        "https://thefreedictionary.com",
        "https://jhu.edu",
        "https://euronews.com",
        "https://liberation.fr",
        "https://ads.google.com",
        "https://trustpilot.com",
        "https://google.com.tw",
        "https://softonic.com",
        "https://kakao.com",
        "https://storage.canalblog.com",
        "https://interia.pl",
        "https://metro.co.uk",
        "https://viglink.com",
        "https://last.fm",
        "https://blackberry.com",
        "https://public-api.wordpress.com",
        "https://sina.com.cn",
        "https://unicef.org",
        "https://archives.gov",
        "https://nps.gov",
        "https://utexas.edu",
        "https://biblegateway.com",
        "https://usda.gov",
        "https://indiegogo.com",
        "https://nikkei.com",
        "https://radiofrance.fr",
        "https://repubblica.it",
        "https://substack.com",
        "https://ap.org",
        "https://nicovideo.jp",
        "https://joomla.org",
        "https://news.com.au",
        "https://allaboutcookies.org",
        "https://mailchimp.com",
        "https://stores.jp",
        "https://intel.com",
        "https://bp0.blogger.com",
        "https://box.com",
        "https://nhk.or.jp",
    ]



}

class UIScraper:
    def __init__(self, output_dir="yolo_dataset", max_retries=3, timeout=10):
        # Original initialization code remains the same...
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.timeout = timeout
        self.processed_urls = set()
        self.failed_urls = set()
        
        # Setup directories including new annotations directory
        self.setup_directories()
        self.setup_logging()
        
        # Initialize statistics
        self.stats = {
            'processed_urls': 0,
            'failed_urls': 0,
            'total_elements': 0,
            'elements_by_class': {class_name: 0 for class_name in CLASSES},
            'elements_by_category': {category: 0 for category in WEBSITES.keys()}
        }
        
        # Generate distinct colors for each class
        self.class_colors = self.generate_distinct_colors(len(CLASSES))

    def setup_directories(self):
        """Setup necessary directories for the dataset"""
        self.images_dir = os.path.join(self.output_dir, "images")
        self.labels_dir = os.path.join(self.output_dir, "labels")
        self.annotated_dir = os.path.join(self.output_dir, "annotated_images")
        for directory in [self.images_dir, self.labels_dir, self.annotated_dir]:
            os.makedirs(directory, exist_ok=True)

    def get_element_label(self, element, class_name):
        """Get a descriptive label for the element combining accessibility info and element type"""
        try:
            # Get all possible text identifiers
            aria_label = element.get_attribute("aria-label")
            title = element.get_attribute("title")
            placeholder = element.get_attribute("placeholder")
            value = element.get_attribute("value")
            text_content = element.text
            name = element.get_attribute("name")
            
            # For images, try to get alt text
            alt_text = element.get_attribute("alt") if element.tag_name == "img" else None
            
            # Try to get the most meaningful text in order of priority
            label_text = (aria_label or 
                        title or 
                        placeholder or 
                        alt_text or 
                        text_content or 
                        value or 
                        name or 
                        "").strip()
            
            # If we have meaningful text, combine it with the class name
            if label_text:
                # Truncate if too long
                if len(label_text) > 30:
                    label_text = label_text[:27] + "..."
                return f"{class_name}: {label_text}"
            
            return class_name
            
        except Exception as e:
            logging.debug(f"Error getting element label: {str(e)}")
            return class_name

    def draw_annotation(self, image, element_info, image_width, image_height):
        """Draw bounding box and label for a single element"""
        draw = ImageDraw.Draw(image)
        coords = element_info['coordinates']
        class_id = element_info['class_id']
        class_name = CLASSES[class_id]
        color = self.class_colors[class_id]
        
        # Get enhanced label
        label = self.get_element_label(element_info['element'], class_name)
        
        # Draw rectangle
        draw.rectangle(
            [
                coords['x1'],
                coords['y1'],
                coords['x2'],
                coords['y2']
            ],
            outline=color,
            width=2
        )
        
        # Draw label background and text
        try:
            # Try to load a font, fall back to default if not available
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        except:
            font = ImageFont.load_default()
            
        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Position label above element if possible, below if not enough space
        if coords['y1'] > text_height + 4:
            label_y = max(0, coords['y1'] - text_height - 4)
        else:
            label_y = min(image_height - text_height, coords['y2'] + 4)
        
        label_bg_coords = [
            coords['x1'],
            label_y,
            coords['x1'] + text_width + 4,
            label_y + text_height
        ]
        
        # Add semi-transparent background for better readability
        background_color = (*color, 180)  # RGB + alpha
        draw.rectangle(label_bg_coords, fill=background_color)
        draw.text(
            (label_bg_coords[0] + 2, label_bg_coords[1]),
            label,
            fill='white',
            font=font
        )

    def get_element_info(self, driver, element, viewport_metrics):
        """Get information about a specific UI element with proper scaling"""
        try:
            # Get element rectangle
            rect = driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return {
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height
                };
            """, element)
            
            # Get device pixel ratio and viewport dimensions
            metrics = driver.execute_script("""
                return {
                    devicePixelRatio: window.devicePixelRatio || 1,
                    viewportWidth: window.innerWidth || document.documentElement.clientWidth,
                    viewportHeight: window.innerHeight || document.documentElement.clientHeight
                };
            """)
            
            # Calculate scaling factors
            device_pixel_ratio = metrics['devicePixelRatio']
            scale_x = viewport_metrics['width'] / metrics['viewportWidth']
            scale_y = viewport_metrics['height'] / metrics['viewportHeight']
            
            # Apply scaling to coordinates
            coordinates = {
                "x1": max(0, rect['left'] * scale_x * device_pixel_ratio),
                "y1": max(0, rect['top'] * scale_y * device_pixel_ratio),
                "x2": min(
                    viewport_metrics['width'],
                    (rect['left'] + rect['width']) * scale_x * device_pixel_ratio
                ),
                "y2": min(
                    viewport_metrics['height'],
                    (rect['top'] + rect['height']) * scale_y * device_pixel_ratio
                )
            }
            
            if (coordinates['x2'] > coordinates['x1'] and 
                coordinates['y2'] > coordinates['y1']):
                
                tag_name = element.tag_name
                element_type = element.get_attribute("type") or element.get_attribute("role")
                class_name = element.get_attribute("class") or ""
                aria_label = element.get_attribute("aria-label") or ""
                
                # Gather rich text information
                title = element.get_attribute("title")
                placeholder = element.get_attribute("placeholder")
                value = element.get_attribute("value")
                text_content = element.text
                name = element.get_attribute("name")
                alt_text = element.get_attribute("alt") if tag_name == "img" else None
                
                class_id = self.get_class_id(tag_name, element_type, class_name, aria_label)
                
                if class_id != -1:
                    self.stats['total_elements'] += 1
                    self.stats['elements_by_class'][CLASSES[class_id]] += 1
                    
                    # Create rich element info dictionary
                    return {
                        "coordinates": coordinates,
                        "class_id": class_id,
                        "class_name": CLASSES[class_id],
                        "tag_name": tag_name,
                        "element_type": element_type,
                        "accessibility": {
                            "aria_label": aria_label,
                            "title": title,
                            "alt_text": alt_text,
                            "role": element.get_attribute("role")
                        },
                        "content": {
                            "text": text_content,
                            "placeholder": placeholder,
                            "value": value,
                            "name": name
                        },
                        "descriptive_label": self.get_element_label(element, CLASSES[class_id]),
                        "element": element  # Keep reference for drawing
                    }
        except Exception as e:
            logging.debug(f"Error processing element: {str(e)}")
        return None
    def generate_distinct_colors(self, n_colors):
        """Generate visually distinct colors for annotations"""
        colors = []
        for i in range(n_colors):
            hue = i / n_colors
            saturation = 0.8 + (i % 3) * 0.1  # Vary saturation slightly
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            # Convert to 8-bit RGB
            color = tuple(int(c * 255) for c in rgb)
            colors.append(color)
        return colors



    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.output_dir, 'scraper.log')),
                logging.StreamHandler()
            ]
        )


    def get_class_id(self, tag_name, element_type, class_name, aria_label=None):
        """Determine the class ID for a UI element"""
        tag_name = tag_name.lower()
        class_name = class_name.lower() if class_name else ""
        element_type = element_type.lower() if element_type else ""
        aria_label = aria_label.lower() if aria_label else ""
        
        if ('button' in class_name or tag_name == 'button' or 
            element_type == 'button' or 'btn' in class_name):
            return CLASSES.index('button')
        elif tag_name == 'a' or element_type == 'link':
            return CLASSES.index('link')
        elif tag_name == 'input':
            if element_type == 'checkbox':
                return CLASSES.index('checkbox')
            elif element_type == 'radio':
                return CLASSES.index('radio')
            else:
                return CLASSES.index('input')
        elif (tag_name == 'select' or 'dropdown' in class_name or
              element_type == 'combobox'):
            return CLASSES.index('dropdown')
        elif tag_name == 'textarea':
            return CLASSES.index('textarea')
        elif tag_name == 'label':
            return CLASSES.index('label')
        elif 'slider' in class_name or element_type == 'slider':
            return CLASSES.index('slider')
        elif 'toggle' in class_name or element_type == 'switch':
            return CLASSES.index('toggle')
        elif ('menu-item' in class_name or element_type == 'menuitem'):
            return CLASSES.index('menu_item')
        elif 'clickable' in class_name:
            return CLASSES.index('clickable')
        elif (tag_name in ['i', 'svg'] or 'icon' in class_name):
            return CLASSES.index('icon')
        return -1


    def get_elements(self, driver, viewport_metrics):
        """Get all relevant UI elements from the page"""
        elements_info = []
        
        # XPath for finding interactive elements
        elements = driver.find_elements(By.XPATH, """
            //*[
                self::a or
                self::button or
                self::input or
                self::select or
                self::textarea or
                self::label or
                self::*[@onclick or @role='button' or @role='link' or
                        @role='menuitem' or @role='slider' or
                        @role='scrollbar' or @role='checkbox' or
                        @role='radio' or @role='textbox' or
                        @role='combobox' or @role='listbox' or
                        @role='switch' or @tabindex or
                        contains(@class, 'button') or
                        contains(@class, 'btn') or
                        contains(@class, 'dropdown') or
                        contains(@class, 'menu-item') or
                        contains(@class, 'clickable') or
                        contains(@class, 'link')]
            ]
        """)
        
        for element in elements:
            try:
                element_info = self.get_element_info(driver, element, viewport_metrics)
                if element_info:
                    elements_info.append(element_info)
            except StaleElementReferenceException:
                continue
                
        return elements_info


    def setup_driver(self):
        """Setup Chrome driver with optimal settings and fixed viewport size"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # Set a specific window size to ensure consistent scaling
        options.add_argument("--window-size=1920,1080")
        
        # Force device scale factor to 1
        options.add_argument("--force-device-scale-factor=1")
        
        # Add additional preferences
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2,
                'automatic_downloads': 2
            },
            'profile.managed_default_content_settings': {
                'images': 1
            }
        }
        options.add_experimental_option('prefs', prefs)
        
        return webdriver.Chrome(options=options)

    def process_url(self, url, category):
        """Process a single URL with proper viewport handling"""
        if url in self.processed_urls:
            logging.info(f"Skipping already processed URL: {url}")
            return
        
        driver = None
        try:
            driver = self.setup_driver()
            logging.info(f"Processing {url}")
            
            driver.get(url)
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Set zoom level to 100%
            driver.execute_script("document.body.style.zoom = '100%'")
            
            # Allow for dynamic content to load
            time.sleep(2)
            
            # Get accurate viewport metrics
            viewport_metrics = driver.execute_script("""
                return {
                    width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
                    height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
                    scrollX: window.pageXOffset,
                    scrollY: window.pageYOffset,
                    devicePixelRatio: window.devicePixelRatio || 1
                };
            """)
            
            # Collect elements
            elements_info = self.get_elements(driver, viewport_metrics)
            
            if elements_info:
                screenshot = driver.get_screenshot_as_png()
                self.save_data(url, category, elements_info, screenshot)
                self.processed_urls.add(url)
                self.stats['processed_urls'] += 1
                self.stats['elements_by_category'][category] += len(elements_info)
                logging.info(f"Successfully processed: {url}")
            else:
                self.failed_urls.add(url)
                self.stats['failed_urls'] += 1
                logging.warning(f"No elements found for: {url}")
                
        except Exception as e:
            self.failed_urls.add(url)
            self.stats['failed_urls'] += 1
            logging.error(f"Error processing {url}: {str(e)}")
        finally:
            if driver:
                driver.quit()

    def save_class_list(self):
        """Save the list of classes"""
        with open(os.path.join(self.output_dir, "classes.txt"), 'w') as f:
            for class_name in CLASSES:
                f.write(f"{class_name}\n")

    def save_statistics(self):
        """Save scraping statistics"""
        stats_file = os.path.join(self.output_dir, "statistics.json")
        failed_urls_file = os.path.join(self.output_dir, "failed_urls.txt")
        
        # Save main statistics
        with open(stats_file, 'w') as f:
            stats_data = {
                'timestamp': int(time.time()),
                'total_processed': self.stats['processed_urls'],
                'total_failed': self.stats['failed_urls'],
                'total_elements': self.stats['total_elements'],
                'elements_by_class': self.stats['elements_by_class'],
                'elements_by_category': self.stats['elements_by_category'],
                'processed_urls': list(self.processed_urls)
            }
            json.dump(stats_data, f, indent=2)
        
        # Save failed URLs
        with open(failed_urls_file, 'w') as f:
            for url in self.failed_urls:
                f.write(f"{url}\n")

    def run(self, max_workers=5):
        """Main execution method"""
        try:
            logging.info("Starting UI Element Scraper")
            
            # Process each category of websites
            all_tasks = []
            for category, urls in WEBSITES.items():
                for url in urls:
                    all_tasks.append((url, category))
            
            # Process URLs concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(self.process_url, url, category)
                    for url, category in all_tasks
                ]
                
                # Show progress bar
                for _ in tqdm(
                    concurrent.futures.as_completed(futures),
                    total=len(all_tasks),
                    desc="Processing websites"
                ):
                    pass
            
            # Save results
            self.save_class_list()
            self.save_statistics()
            
            # Print summary
            self.print_summary()
            
            logging.info("Scraping completed successfully!")
            
        except Exception as e:
            logging.error(f"Error during scraping: {str(e)}")
            raise

    def print_summary(self):
        """Print scraping summary"""
        print("\nScraping Summary:")
        print("=" * 50)
        print(f"Total URLs processed: {self.stats['processed_urls']}")
        print(f"Failed URLs: {self.stats['failed_urls']}")
        print(f"Total elements detected: {self.stats['total_elements']}")
        
        print("\nElements by category:")
        print("-" * 30)
        for category, count in self.stats['elements_by_category'].items():
            print(f"{category}: {count}")
        
        print("\nElements by class:")
        print("-" * 30)
        for class_name, count in self.stats['elements_by_class'].items():
            print(f"{class_name}: {count}")

    def save_data(self, url, category, elements_info, screenshot):
        """Save screenshot, annotations, and annotated image"""
        try:
            filename = f"{category}_{urlparse(url).netloc}_{int(time.time())}"
            
            # Open screenshot as PIL Image
            image = Image.open(io.BytesIO(screenshot))
            image_width, image_height = image.size
            
            # Save original screenshot
            image_path = os.path.join(self.images_dir, f"{filename}.png")
            image.save(image_path)
            
            # Create and save annotated image
            annotated_image = image.copy()
            for element in elements_info:
                self.draw_annotation(annotated_image, element, image_width, image_height)
            
            # Save annotated image
            annotated_path = os.path.join(self.annotated_dir, f"{filename}_annotated.png")
            annotated_image.save(annotated_path)
            
            # Save YOLO annotations (simplified format for training)
            annotation_path = os.path.join(self.labels_dir, f"{filename}.txt")
            with open(annotation_path, 'w') as f:
                for element in elements_info:
                    coords = element['coordinates']
                    x_center = (coords['x1'] + coords['x2']) / (2 * image_width)
                    y_center = (coords['y1'] + coords['y2']) / (2 * image_height)
                    width = (coords['x2'] - coords['x1']) / image_width
                    height = (coords['y2'] - coords['y1']) / image_height
                    
                    f.write(f"{element['class_id']} {x_center} {y_center} {width} {height}\n")
            
            # Save rich metadata (including descriptive labels and additional info)
            metadata_path = os.path.join(self.labels_dir, f"{filename}_meta.json")
            with open(metadata_path, 'w') as f:
                metadata = {
                    'url': url,
                    'category': category,
                    'timestamp': int(time.time()),
                    'image_size': {'width': image_width, 'height': image_height},
                    'elements': elements_info,
                    'dataset_split': 'train',  # You can modify this based on your needs
                    'additional_info': {
                        'browser': 'chrome',
                        'viewport_size': f"{image_width}x{image_height}",
                        'total_elements': len(elements_info)
                    }
                }
                json.dump(metadata, f, indent=2)
            
            logging.info(f"Saved data for {url} with {len(elements_info)} elements")
                
        except Exception as e:
            logging.error(f"Error saving data for {url}: {str(e)}")

def add_custom_websites():
    """Add additional websites to the WEBSITES dictionary"""
    # Web Applications
    WEBSITES['web_apps'] = [
        'https://www.dropbox.com',
        'https://web.whatsapp.com',
        'https://discord.com',
        'https://slack.com',
        'https://www.evernote.com',
        'https://workspace.google.com'
    ]
    
    # Developer Tools
    WEBSITES['dev_tools'] = [
        'https://codesandbox.io',
        'https://codepen.io',
        'https://jsfiddle.net',
        'https://replit.com',
        'https://jupyter.org',
        'https://www.jetbrains.com'
    ]
    
    # Creative Tools
    WEBSITES['creative'] = [
        'https://www.photopea.com',
        'https://www.pixilart.com',
        'https://www.remove.bg',
        'https://www.canva.com',
        'https://www.figma.com'
    ]
    
    # News and Media
    WEBSITES['news'] = [
        'https://www.bbc.com',
        'https://www.reuters.com',
        'https://www.bloomberg.com',
        'https://www.theverge.com',
        'https://techcrunch.com'
    ]
    
    # AI/ML Platforms
    WEBSITES['ai_platforms'] = [
        'https://huggingface.co',
        'https://www.kaggle.com',
        'https://colab.research.google.com',
        'https://wandb.ai',
        
    ]



def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="UI Element Scraper for YOLO Dataset"
    )
    parser.add_argument(
        "--output-dir",
        default="yolo_dataset",
        help="Output directory for dataset"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum concurrent workers"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Page load timeout in seconds"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries per URL"
    )
    
    args = parser.parse_args()
    
    # Add additional websites
    add_custom_websites()
    
    # Initialize and run scraper
    scraper = UIScraper(
        output_dir=args.output_dir,
        max_retries=args.max_retries,
        timeout=args.timeout
    )
    
    scraper.run(max_workers=args.max_workers)

if __name__ == "__main__":
    main()