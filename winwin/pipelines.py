# pipelines.py
import os
from dotenv import load_dotenv
from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query

load_dotenv()

APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_URL = os.getenv("APPWRITE_URL")
APPWRITE_PROJECT = os.getenv("APPWRITE_PROJECT")
APPWRITE_DATABASE = os.getenv("APPWRITE_DATABASE")
APPWRITE_COLLECTION = os.getenv("APPWRITE_COLLECTION")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")

db_collection = (APPWRITE_DATABASE, APPWRITE_COLLECTION)

client = Client()
(
    client.set_endpoint(APPWRITE_URL)
    .set_project(APPWRITE_PROJECT)
    .set_key(APPWRITE_API_KEY)
)
databases = Databases(client)


class WinwinPipeline:
    def open_spider(self, spider: Spider):
        try:
            databases.get_collection(APPWRITE_DATABASE, APPWRITE_COLLECTION)
        except Exception as e:
            print("APPWRITE 데이터베이스 연결 에러")
            spider.crawler.engine.close_spider(spider, f"Error: {e}")

    def process_item(self, item, spider: Spider):
        data = ItemAdapter(item).asdict()
        winwin_code = data.get("id")

        # winwin_code로 검색
        response = databases.list_documents(
            *db_collection,
            [Query.equal("id", winwin_code)],
        )
        # 검색 결과가 있으면 업데이트
        if response["total"] > 0:
            databases.update_document(
                *db_collection,
                response["documents"][0]["$id"],
                data,
            )
        # 검색 결과가 없으면 새로 생성
        else:
            databases.create_document(
                *db_collection,
                "unique()",
                data,
            )

        return data
