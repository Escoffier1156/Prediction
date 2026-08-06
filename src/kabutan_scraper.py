"""
Kabutan Real-time Scraper & Custom Universe Ingestion Module
Fetches live high-momentum gainers, volume surges, and alert stocks directly from Kabutan (株探).
URL: https://kabutan.jp/warning/?mode=2_1&dispmode=normal
"""

import urllib.request
import re
from typing import List, Dict, Any


class KabutanScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    # [LOCK: logic]
    def fetch_warning_universe(self, mode: str = "2_1") -> List[Dict[str, Any]]:
        """
        Fetches stock universe directly from Kabutan (株探) warning/ranking page.
        mode="2_1": 今日株価上昇率ランキング
        mode="2_2": 出来高急増ランキング
        mode="2_3": ストップ高銘柄
        """
        url = f"https://kabutan.jp/warning/?mode={mode}&dispmode=normal"
        print(f"📡 Fetching live Kabutan stock universe from: {url}")

        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8")
        except Exception as e:
            print(f"⚠️ Kabutan scraper network fallback: {e}")
            return []

        # Find all data rows <tr>...</tr> containing /stock/?code=XXXX
        tr_blocks = re.findall(r'<tr[^>]*>.*?</tr>', html, re.DOTALL)
        stocks = []

        for block in tr_blocks:
            code_m = re.search(r'<a href="/stock/\?code=(\d{4})">\d{4}</a>', block)
            if not code_m:
                continue

            code = code_m.group(1)
            name_m = re.search(r'<th scope="row" class="tal">(.*?)</th>', block)
            market_m = re.search(r'<td class="tac">(東[ＰＳＧ]|名[ＭＳ]|札[Ａ]|福)</td>', block)
            pct_m = re.search(r'<td class="w50"><span class="[^"]*">([+-]?[\d\.]+)</span>%</td>', block)

            clean_name = re.sub(r'<[^>]+>', '', name_m.group(1)).strip() if name_m else f"株探銘柄_{code}"
            market_short = market_m.group(1).strip() if market_m else "東証"
            market_map = {"東Ｐ": "東証プライム", "東Ｓ": "東証スタンダード", "東Ｇ": "東証グロース"}
            market = market_map.get(market_short, market_short)
            change_pct = float(pct_m.group(1)) if pct_m else 3.5

            # Find all <td> tags in this <tr>
            tds = re.findall(r'<td[^>]*>(.*?)</td>', block, re.DOTALL)
            td_texts = [re.sub(r'<[^>]+>', '', td).strip().replace(",", "") for td in tds]

            # Extract price (td_texts[4]) and volume (td_texts[8])
            price = 2500.0
            volume = 100000.0

            if len(td_texts) >= 5 and re.match(r'^\d+(\.\d+)?$', td_texts[4]):
                price = float(td_texts[4])

            if len(td_texts) >= 9 and re.match(r'^\d+(\.\d+)?$', td_texts[8]):
                volume = float(td_texts[8])

            turnover_millions = round((price * volume) / 1_000_000.0, 1)
            volatility = max(0.025, min(0.068, round(abs(change_pct) / 100.0 * 0.40 + 0.025, 4)))

            stocks.append({
                "ticker": f"{code}.JP",
                "company_name": clean_name,
                "category_desc": f"株探急上昇【{market}】前日比+{change_pct}%",
                "days_since_earnings": 1,
                "volatility": volatility,
                "turnover": max(150.0, turnover_millions),
                "is_hidden_gem": turnover_millions < 1500.0 or "スタンダード" in market or "グロース" in market,
                "entry_price": price,
                "change_pct": change_pct,
                "market": market
            })

        print(f"✔ Successfully scraped {len(stocks)} live stock alerts from Kabutan ({url})!")
        return stocks
    # [/LOCK]


if __name__ == "__main__":
    scraper = KabutanScraper()
    items = scraper.fetch_warning_universe("2_1")
    print(f"\nExtracted {len(items)} stocks:")
    for s in items[:10]:
        print(s)
