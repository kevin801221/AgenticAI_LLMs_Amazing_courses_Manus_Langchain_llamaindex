import os
import requests
import json
from langchain.tools import tool

class SearchTools:

    @tool
    def searchInfo(query:str):
        """在網上搜索關於指定內容的相關信息"""
        return SearchTools.search(query)

    def search(query:str):
        url = "https://google.serper.dev/news"

        payload = json.dumps({
        "q": query,
        "hl": "zh-tw"
        })
        headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        results = response.json()['news']

        stirng = []
        for result in results:
            try:
                stirng.append('\n'.join([
                    f"標題: {result['title']}",
                    f"時間: {result['date']}",
                    f"來源: {result['source']}",
                    f"摘要: {result['snippet']}", "\n-----------------"
                ]))
            except KeyError:
                next

        content = '\n'.join(stirng)
        return f"\nSearch result: {content}\n"
