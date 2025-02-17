# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from dotenv import load_dotenv
import os
import fire

load_dotenv()

app_crw = FirecrawlApp(api_key=os.environ.get('FIRECRAWL_API_KEY'))

class NestedModel1(BaseModel):
    pair: str
    status: Optional[str] = None
    delist_date: Optional[str] = None
    exchange: Optional[str] = None

class ExtractSchema(BaseModel):
    trading_pairs: List[NestedModel1]

class SiteExtract:
    def __init__(self, exchange: str):
        self.exchange = exchange

    def site_extract(self):
        common_prompt = (
            'Extract all trading pairs that will be delisted or have been recently delisted. '
            'Include the status and delist date if available. The exchange name should be in lowercase. '
            'For gate.io, use "gateio" as the exchange name.'
        )
        if self.exchange == 'gateio':
            return app_crw.extract(
                ["https://www.gate.io/announcements/delisted"],
                {
                    'prompt': common_prompt,
                    'schema': ExtractSchema.model_json_schema(),
                }
            )
        elif self.exchange == 'bybit':
            return app_crw.extract(
                [f"https://announcements.bybit.com/en/?category=delistings"],
                {
                    'prompt': common_prompt,
                    'schema': ExtractSchema.model_json_schema(),
                }
            )
        elif self.exchange == 'binance':
            return app_crw.extract(
                [f"https://www.binance.com/en/support/announcement/delisting?c=161"],
                {
                    'prompt': common_prompt,
                    'schema': ExtractSchema.model_json_schema(),
                }
            )
        elif self.exchange == 'okx':
            return app_crw.extract(
                [f"https://okx.com/help/section/announcements-delistings"],
                {
                    'prompt': common_prompt,
                    'schema': ExtractSchema.model_json_schema(),
                }
            )
        else:
            return {'error': 'Exchange not supported'}

def scraper(exchange: str):
    try:
        response = SiteExtract(exchange=exchange).site_extract()
        if isinstance(response, list) and len(response) > 0:
            data = response[0].get('data', {})
        else:
            data = response.get('data', {}) if isinstance(response, dict) else {}
        
        info = data.get('trading_pairs', [])
        pairs = []
        for item in info:
            pair = item.get('pair', '')
            exchange_name = item.get('exchange', '')
            if exchange_name == 'gateio':
                formatted_pair = f"{pair}/USDT:USDT"
            else:
                base_asset = pair.replace('USDT', '') if 'USDT' in pair else pair
                formatted_pair = f"{base_asset}/USDT:USDT"
            pairs.append(formatted_pair)
        #print(f"Extraction of {len(pairs)} pairs complete!")
        return pairs
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

if __name__ == '__main__':
    fire.Fire(scraper)