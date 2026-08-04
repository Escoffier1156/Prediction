"""
Japan Stock Market Prediction SDK
Ultra-simple 1-line integration framework for downstream Trading Bots.
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import time
from orchestrator import NonNeumannPredictor


@dataclass
class TradeSignal:
    ticker: str
    trigger_time: str
    current_price: float
    take_profit: float
    stop_loss: float
    probability: float
    execution_time_sec: float
    peak_memory_mb: float
    is_memory_safe: bool

    @property
    def risk_reward_ratio(self) -> float:
        reward = self.take_profit - self.current_price
        risk = self.current_price - self.stop_loss
        return round(reward / risk, 2) if risk > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "trigger_time": self.trigger_time,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "probability_pct": self.probability,
            "risk_reward_ratio": self.risk_reward_ratio,
            "memory_safe": self.is_memory_safe
        }


class JapanStockEngine:
    """
    SDK Main Interface for Trading Bots.
    Provides 1-line instant prediction call with 500MB memory ceiling enforcement.
    """
    _instance = None

    def __new__(cls, memory_limit_mb: float = 500.0):
        if cls._instance is None:
            cls._instance = super(JapanStockEngine, cls).__new__(cls)
            cls._instance.predictor = NonNeumannPredictor(memory_limit_mb=memory_limit_mb)
        return cls._instance

    def predict(self, ticker: str = "9984.JP", trigger_time: Optional[str] = None) -> TradeSignal:
        """
        1-Line Prediction Call for Trading Bots.
        """
        if not trigger_time:
            now_hour = time.localtime().tm_hour
            if now_hour < 9:
                trigger_time = "08:30"
            elif now_hour < 10:
                trigger_time = "09:30"
            else:
                trigger_time = "10:30"

        res = self.predictor.execute_timed_prediction_cycle(trigger_time=trigger_time, ticker=ticker)

        return TradeSignal(
            ticker=ticker,
            trigger_time=trigger_time,
            current_price=res.get("current_price", 0.0),
            take_profit=res.get("take_profit_target", 0.0),
            stop_loss=res.get("stop_loss_target", 0.0),
            probability=res.get("logical_probability_pct", 0.0),
            execution_time_sec=res.get("execution_time_sec", 0.0),
            peak_memory_mb=res.get("peak_memory_mb", 0.0),
            is_memory_safe=(res.get("memory_ceiling_status") == "STRICTLY_ENFORCED")
        )


def with_japan_stock_prediction(ticker: str = "9984.JP", trigger_time: Optional[str] = "09:30"):
    """
    Decorator for Trading Bot order execution functions.
    Injects predicted TradeSignal directly as first argument.
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            engine = JapanStockEngine()
            signal = engine.predict(ticker=ticker, trigger_time=trigger_time)
            return func(signal, *args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    print("=== Japan Stock Market Prediction Engine SDK Demo ===")
    engine = JapanStockEngine()
    sig = engine.predict(ticker="9984.JP", trigger_time="09:30")
    print(f"Target Ticker: {sig.ticker}")
    print(f"  Take Profit: {sig.take_profit} JPY")
    print(f"  Stop Loss:   {sig.stop_loss} JPY")
    print(f"  Confidence:  {sig.probability}%")
