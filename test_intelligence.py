from app.intelligence import State,score
def test_neutral(): assert score(State())[1]=='NEUTRAL'
def test_long(): assert score(State(taker_bias=1,book_imbalance=1,whale_flow=1,smart_money=1,pattern_edge=1,oi_delta=.2))[0]>0
def test_short(): assert score(State(taker_bias=-1,book_imbalance=-1,whale_flow=-1,smart_money=-1,pattern_edge=-1,oi_delta=-.2))[0]<0
