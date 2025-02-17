# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from dotenv import load_dotenv, dotenv_values
import os, fire
from dataclasses import dataclass


load_dotenv()

app_crw = FirecrawlApp(api_key=os.environ.get('FIRECRAWL_API_KEY'))

class NestedModel1(BaseModel):
    pair: str
    status: str = None
    delist_date: str = None
    exchange: str = None

class ExtractSchema(BaseModel):
    trading_pairs: list[NestedModel1]

@dataclass
class SiteExtract:
    exchange: str
    NestedModel1: classmethod
    ExtractSchema: classmethod

    def site_constract(self):

        if self.exchange == 'gateio':
            ex = self.exchange.split('io')[0] + '.io'
            return app_crw.extract([
            f"https://gate.{ex}/announcements/delisted"
            ], {
                'prompt': f'Extract all trading pairs that will be delisted or have been recently delisted. Include the status and delist date if available. The exchange name should be lower case. For gate.io exchange replace the exchange parameter with "gateio"',
                'schema': self.ExtractSchema.model_json_schema(),
            })
        elif self.exchange == 'bybit':
            return app_crw.extract([
            f"https://announcements.{self.exchange}.com/en/?category=delistings"
            ], {
                'prompt': f'Extract all trading pairs that will be delisted or have been recently delisted. Include the status and delist date if available. The exchange name should be lower case. For gate.io exchange replace the exchange parameter with "gateio"',
                'schema': self.ExtractSchema.model_json_schema(),
            })
        elif self.exchange == 'binance':
            return app_crw.extract([
            f"https://{self.exchange}.com/en/support/announcement/delisting?c=161"
            ], {
                'prompt': f'Extract all trading pairs that will be delisted or have been recently delisted. Include the status and delist date if available. The exchange name should be lower case. For gate.io exchange replace the exchange parameter with "gateio"',
                'schema': self.ExtractSchema.model_json_schema(),
            })
        else:
            return 'exchange not supported'


#info = data.get('data').get('trading_pairs')

#exchanges = set(item['exchange'] for item in info)



def scraper(exchange: str):
    try:
        info = SiteExtract(exchange=exchange).site_constract().get('data').get('trading_pairs')
        print(info)
        pairs = []
        for i in range(0,len(info)):
            ex = info[i].get('exchange')
            if ex == 'gateio':
                pairs.append(info[i].get('pair') + '/USDT:USDT')
            else:
                p = info[i].get('pair').split('USDT')[0] + '/USDT:USDT'
                pairs.append(p)
        print(f'extraction of {len(pairs)} complete!')
        return pairs
    except Exception as e:
        print(e)

if __name__ == 'main':
    fire.Fire(scraper)

