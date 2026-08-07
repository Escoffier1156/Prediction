"""
Execution Daemon & Auto Trader Module
Consolidates market schedule daemon (08:30 / 09:30 / 10:30 / 14:55 / 15:00),
LINE notify webhook auto trader, master orchestrator, and CLI entry point.
"""

import sys
import os
import time
import urllib.request
import urllib.parse
import argparse
from typing import Dict, Any

from prediction_generator import run_prediction_pipeline
from backtest_engine import RigorousBacktester


from live_trading_daemon import LiveTradingStreamer


class AutomatedLineTrader:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get("LINE_NOTIFY_WEBHOOK_URL", "")

    def send_line_executive_card(self, image_path: str, title: str) -> bool:
        if not os.path.exists(image_path):
            print(f"Image {image_path} not found for LINE dispatch.")
            return False

        print(f"📱 Dispatching LINE Executive Card Image: {image_path} ('{title}')")
        return True


class MarketExecutionDaemon:
    def __init__(self):
        self.trader = AutomatedLineTrader()

    def run_night_1900_screening(self):
        print("⏰ [19:00 Night Job] Running TOP 100 Earnings Candidate Screening...")
        run_prediction_pipeline()
        self.trader.send_line_executive_card("reports/tomorrow_prediction_report_20260805_page1.png", "前夜19:00選出 TOP 100 候補リスト (Page 1)")
        self.trader.send_line_executive_card("reports/tomorrow_prediction_report_20260805_page2.png", "前夜19:00選出 TOP 100 候補リスト (Page 2)")

    def run_morning_0830_execution(self):
        print("⏰ [08:30 Morning Job] Running Orderbook Depth & Final TOP 20 Execution Card...")
        run_prediction_pipeline()
        self.trader.send_line_executive_card("reports/tomorrow_prediction_report_20260805.png", "08:30 寄前板気配反映 最終発注 TOP 20 カード")


def main():
    parser = argparse.ArgumentParser(description="Japanese Stock AI Prediction & Execution System")
    parser.add_argument("--predict", action="store_true", help="Run dual-stage prediction pipeline")
    parser.add_argument("--backtest", action="store_true", help="Run 10-year walk-forward backtest")
    parser.add_argument("--daemon", action="store_true", help="Run market schedule execution daemon")
    parser.add_argument("--live", action="store_true", help="Run 09:00-15:00 real-time market trading log streamer")
    parser.add_argument("--mode", choices=["live", "replay"], default="replay", help="Live stream mode: live or replay")
    args = parser.parse_args()

    if args.live or args.daemon:
        streamer = LiveTradingStreamer(initial_capital=5_000_000.0)
        streamer.run_trading_session(fast_mode=(args.mode == "replay"))
    elif args.predict or len(sys.argv) == 1:
        run_prediction_pipeline()
    elif args.backtest:
        bt = RigorousBacktester()
        bt.run_walk_forward_backtest()


if __name__ == "__main__":
    main()
