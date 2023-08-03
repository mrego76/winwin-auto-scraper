# price.py
import os
from scrapy import Spider, Request, FormRequest
from dotenv import load_dotenv
from .utils import extract_winwin_info, extract_danawa_info, modify_price
from winwin.items import ProductItem

load_dotenv()

MB_ID = os.getenv("MB_ID")
MB_PASSWORD = os.getenv("MB_PASSWORD")


class PriceSpider(Spider):
    name = "price"
    custom_settings = {
        "ITEM_PIPELINES": {"winwin.pipelines.WinwinPipeline": 300},
    }
    allowed_domains = ["comkill.com"]
    url = "https://comkill.com"
    login_url = url + "/bbs/login.php"
    login_check_url = url + "/bbs/login_check.php"
    adm_url = url + "/adm/"

    def start_requests(self):
        yield Request(self.login_url, callback=self.login)

    def login(self, response):
        url = response.css("input[name=url]").attrib["value"]
        return FormRequest(
            url=self.login_check_url,
            formdata={
                "url": url,
                "mb_id": MB_ID,
                "mb_password": MB_PASSWORD,
            },
            callback=self.after_login,
        )

    def after_login(self, response):
        yield Request(self.adm_url, callback=self.parse_adm)

    def parse_adm(self, response):
        if MB_ID in response.text:
            return FormRequest(
                url=self.url + "/adm_cate/product_list_multy.php",
                formdata={
                    "order1": "A.pd_no",
                    "sp_id": "basic",
                    "asc1": "asc",
                    "r_page": "5",
                    "mt1": "1",
                    "s1_cate": "A.pd_no",
                    "search1": "",
                    "pc_viewid": "basic",
                    "cate1": "",
                    "cate2": "",
                    "cate3": "",
                    "cate4": "",
                    "made": "",
                    "search": MB_ID,
                    "search2": "",
                    "s_cate": "pd_juluk",
                    "stype": "",
                    "etc1": "",
                    "s_pinfo": "",
                    "cf_save": "1",
                },
                callback=self.parse_modify_price,
            )
        else:
            self.log("Login failed. Check the login credentials.")

    def parse_modify_price(self, response):
        item = ProductItem()

        next_pages = response.xpath('.//tr[@class="ht70"]/td[3]/center/a')

        tables = response.xpath("//form[2]/table")

        for table in tables[4:-1]:
            print("-" * 50)
            print(table.xpath(".//textarea/text()").get())
            winwin_data = extract_winwin_info(table)
            print(winwin_data)
            danawa_data = extract_danawa_info(table)
            print(danawa_data)
            data = modify_price(winwin_data, danawa_data, 10)
            print(data)
            print("=" * 50)

            for key, value in winwin_data.items():
                if key.startswith("pd_no"):
                    item["id"] = value
                elif key.startswith("pd_name"):
                    item["name"] = value
                elif key.startswith("pd_cost_price_"):
                    item["cost_price"] = value
                elif key.startswith("pd_sobija_pan_basic_"):
                    item["sale_price"] = value

            item["first_price"] = danawa_data["일등가"]
            item["second_price"] = danawa_data["이등가"]

            yield item

        for page in next_pages:
            if page.xpath("text()").get() != " 1 ":
                yield response.follow(page, self.parse_modify_price)
