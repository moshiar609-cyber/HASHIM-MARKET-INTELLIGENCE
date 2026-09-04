import os,json,asyncio,time
import httpx, websockets
import redis.asyncio as redis
import asyncpg

BASE=os.getenv('BINANCE_BASE','https://fapi.binance.com')
WS=os.getenv('BINANCE_WS','wss://fstream.binance.com/stream')
REDIS=os.getenv('REDIS_URL','redis://redis:6379/0')
DB=os.getenv('DATABASE_URL','postgresql://hashim:hashim@postgres:5432/hashim')

async def connect_db():
    for i in range(30):
        try: return await asyncpg.connect(DB)
        except Exception as e:
            print('db retry',repr(e),flush=True); await asyncio.sleep(min(2+i,10))
    raise RuntimeError('database unavailable')

async def symbols(client):
    r=await client.get(BASE+'/fapi/v1/exchangeInfo'); r.raise_for_status(); x=r.json()
    return [s['symbol'].lower() for s in x['symbols'] if s.get('status')=='TRADING' and s.get('contractType')=='PERPETUAL' and s.get('quoteAsset')=='USDT']

async def persist(con,symbol,typ,d):
    await con.execute('INSERT INTO market_events(symbol,event_type,price,qty,side,bid_qty,ask_qty,payload) VALUES($1,$2,$3,$4,$5,$6,$7,$8)',symbol,typ,d.get('price'),d.get('qty'),d.get('side'),d.get('bid_qty'),d.get('ask_qty'),json.dumps(d))

async def run():
    r=redis.from_url(REDIS,decode_responses=True)
    async with httpx.AsyncClient(timeout=20) as client:
        while True:
            con=await connect_db()
            try:
                syms=await symbols(client); top=max(1,int(os.getenv('TOP_SYMBOLS','100')))
                streams=['!bookTicker','!forceOrder@arr']+[f'{s}@aggTrade' for s in syms[:top]]
                url=WS+'?streams='+'/'.join(streams)
                print('collector streams',len(streams),flush=True)
                async with websockets.connect(url,ping_interval=20,ping_timeout=30,max_size=8_000_000) as ws:
                    async for msg in ws:
                        outer=json.loads(msg); d=outer.get('data',outer); e=d.get('e')
                        if e=='bookTicker':
                            s=d['s']; bid_p=float(d['b']); ask_p=float(d['a']); bq=float(d['B']); aq=float(d['A'])
                            old=await r.hgetall('market:'+s)
                            await r.hset('market:'+s,mapping={'price':(bid_p+ask_p)/2,'bid':bid_p,'ask':ask_p,'bid_qty':bq,'ask_qty':aq,'updated':time.time(),'buy_qty':old.get('buy_qty','0'),'sell_qty':old.get('sell_qty','0'),'liq_long':old.get('liq_long','0'),'liq_short':old.get('liq_short','0')})
                            await persist(con,s,'bookTicker',{'price':(bid_p+ask_p)/2,'bid_qty':bq,'ask_qty':aq})
                        elif e=='forceOrder':
                            o=d.get('o',{}); s=o.get('s'); q=float(o.get('q',0)); p=float(o.get('ap') or o.get('p') or 0); side=o.get('S')
                            st=await r.hgetall('market:'+s); lb=float(st.get('liq_long',0)); ls=float(st.get('liq_short',0))
                            if side=='SELL': lb+=q*p
                            elif side=='BUY': ls+=q*p
                            await r.hset('market:'+s,mapping={'liq_long':lb,'liq_short':ls,'updated':time.time()})
                            await persist(con,s,'forceOrder',{'price':p,'qty':q,'side':side})
                        elif e=='aggTrade':
                            s=d['s']; q=float(d['q']); p=float(d['p']); buy=q*p if d.get('m') is False else 0; sell=q*p if d.get('m') is True else 0
                            st=await r.hgetall('market:'+s); b=float(st.get('buy_qty',0))+buy; se=float(st.get('sell_qty',0))+sell
                            await r.hset('market:'+s,mapping={'price':p,'buy_qty':b,'sell_qty':se,'updated':time.time()})
                            await persist(con,s,'aggTrade',{'price':p,'qty':q,'side':'BUY' if buy else 'SELL'})
            except Exception as ex:
                print('collector reconnect:',repr(ex),flush=True); await asyncio.sleep(5)
            finally:
                await con.close()

if __name__=='__main__': asyncio.run(run())
