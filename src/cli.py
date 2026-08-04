"""
Non-Neumann System Full-Market CLI & Market Session Daemon Mode
"""

import sys
import argparse
import json
from orchestrator import NonNeumannPredictor
from market_daemon import MarketSessionDaemon


def main():
    parser = argparse.ArgumentParser(
        prog="non-neumann",
        description="Non-Neumann Dynamic Bulk Prediction Engine CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: predict
    predict_parser = subparsers.add_parser("predict", help="Execute 4,000-ticker dynamic bulk prediction scan")
    predict_parser.add_argument("--time", type=str, default="09:30", choices=["08:30", "09:30", "10:30"], help="Timed trigger slot")
    predict_parser.add_argument("--ticker", type=str, default="ALL", help="Target specific ticker or 'ALL' for full market scan")

    # Command: daemon (Perpetual Market Stream)
    daemon_parser = subparsers.add_parser("daemon", help="Start continuous non-stop market session daemon (08:30 -> 15:30)")

    # Command: serve (HTTP API)
    serve_parser = subparsers.add_parser("serve", help="Start ultra-fast microservice API for trading bots")
    serve_parser.add_argument("--port", type=int, default=8080, help="Port number for HTTP server")

    args = parser.parse_args()

    if args.command == "daemon":
        daemon = MarketSessionDaemon(memory_limit_mb=500.0)
        daemon.start_perpetual_market_stream(simulated_fast_mode=True)

    elif args.command == "serve":
        print(f"[Non-Neumann Engine] Starting Full-Market Microservice API on port {args.port}...")
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
