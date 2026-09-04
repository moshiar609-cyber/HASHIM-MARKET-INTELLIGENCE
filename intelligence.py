from dataclasses import dataclass
from math import isfinite

def clamp(x, a=-100.0, b=100.0):
    return max(a, min(b, x)) if isfinite(x) else 0.0

@dataclass
class State:
    price: float = 0.0
    oi_delta: float = 0.0
    funding: float = 0.0
    volume_ratio: float = 1.0
    taker_bias: float = 0.0
    book_imbalance: float = 0.0
    liquidation_bias: float = 0.0
    whale_flow: float = 0.0
    smart_money: float = 0.0
    pattern_edge: float = 0.0

def score(s: State):
    parts = {
        'oi': clamp(s.oi_delta * 220),
        'funding': clamp(-s.funding * 90000),
        'volume': clamp((s.volume_ratio - 1) * 18),
        'taker': clamp(s.taker_bias * 25),
        'book': clamp(s.book_imbalance * 20),
        'liquidation': clamp(s.liquidation_bias * 20),
        'whale': clamp(s.whale_flow * 25),
        'smart_money': clamp(s.smart_money * 20),
        'pattern': clamp(s.pattern_edge * 20),
    }
    weights = {'oi': .18, 'funding': .07, 'volume': .08, 'taker': .14,
               'book': .10, 'liquidation': .08, 'whale': .14,
               'smart_money': .09, 'pattern': .12}
    raw = sum(parts[k] * weights[k] for k in parts)
    active = [v for v in parts.values() if abs(v) >= 4]
    pos, neg = sum(v > 0 for v in active), sum(v < 0 for v in active)
    agreement = max(pos, neg) / max(1, len(active))
    final = clamp(raw * (0.65 + 0.35 * agreement))
    label = ('STRONG_LONG' if final >= 85 else 'LONG_WATCH' if final >= 70 else
             'STRONG_SHORT' if final <= -85 else 'SHORT_WATCH' if final <= -70 else 'NEUTRAL')
    reasons = [k for k, v in parts.items() if abs(v) >= 6]
    return round(final, 2), label, reasons, parts
