"""
Japan Stock Market Prediction Engine - CLI Suite & Backtest Verifier
"""

import sys
import argparse
import json
from orchestrator import NonNeumannPredictor
from market_daemon import MarketSessionDaemon
from auto_trader import ZeroCodeAutoTrader
from performance_reporter import PerformanceReporter


def main():
    parser = argparse.ArgumentParser(
        prog="predict-japan",
        description="Japan Stock Market Prediction Engine (Zero-Code Auto-Trading & Backtest Suite)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: predict
    predict_parser = subparsers.add_parser("predict", help="Execute 4,000-ticker dynamic bulk prediction scan")
    predict_parser.add_argument("--time", type=str, default="09:30", choices=["08:30", "09:30", "10:30"], help="Timed trigger slot")
    predict_parser.add_argument("--ticker", type=str, default="ALL", help="Target specific ticker or 'ALL' for full market scan")

    # Command: backtest (Rigorous Walk-Forward Backtest & 10 Proof Metrics)
    backtest_parser = subparsers.add_parser("backtest", help="Run 100% reproducible Walk-Forward backtest with 10 proof metrics")
    backtest_parser.add_argument("--strategy", type=str, default="earnings_daytrade", help="Target strategy name")

    # Command: autotrade (Zero-Code Automated Trading)
    autotrade_parser = subparsers.add_parser("autotrade", help="Start Zero-Code Automated Trading Engine using config.json (No code needed!)")
    autotrade_parser.add_argument("--config", type=str, default="config.json", help="Path to config.json file")

    # Command: daemon (Perpetual Market Stream)
    daemon_parser = subparsers.add_parser("daemon", help="Start continuous non-stop market session daemon (08:30 -> 15:30)")

    # Command: serve (HTTP API)
    serve_parser = subparsers.add_parser("serve", help="Start ultra-fast microservice API for trading bots")
    serve_parser.add_argument("--port", type=int, default=8080, help="Port number for HTTP server")

    args = parser.parse_args()

    if args.command == "backtest":
        print("[Japan Stock Engine] Executing Walk-Forward Strategy Backtest & Proof Verification...")
        reporter = PerformanceReporter()
        res = reporter.generate_full_performance_proof()
        print(f"\n[Proof Output] Summary report generated: {res['summary_md']}")

    elif args.command == "autotrade":
        config_file = getattr(args, "config", "config.json")
        trader = ZeroCodeAutoTrader(config_path=config_file)
        trader.start_zero_code_autotrade(trigger_time="09:30")

    elif args.command == "daemon":
        daemon = MarketSessionDaemon(memory_limit_mb=500.0)
        daemon.start_perpetual_market_stream(simulated_fast_mode=True)

    elif args.command == "serve":
        print(f"[Japan Stock Engine] Starting Full-Market Microservice API on port {args.port}...")
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse

        class BotBulkPredictionHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                query = urllib.parse.parse_qs(parsed.query)
                ticker = query.get("ticker", ["ALL"])[0]
                trigger_time = query.get("time", ["09:30"])[0]

                predictor = NonNeumannPredictor(memory_limit_mb=500.0)
                res = predictor.execute_timed_prediction_cycle(trigger_time=trigger_time, ticker=ticker)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))

            def log_message(self, format, *args):
                pass

        server = HTTPServer(("0.0.0.0", args.port), BotBulkPredictionHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

    else:
        trigger_time = getattr(args, "time", "09:30")
        target_ticker = getattr(args, "ticker", "ALL")

        predictor = NonNeumannPredictor(memory_limit_mb=500.0)
        result = predictor.execute_timed_prediction_cycle(trigger_time=trigger_time, ticker=target_ticker)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
