# HASHIM MARKET INTELLIGENCE V31.1 — MCP

تم تحديث طبقة MCP لتستخدم **MCP Python SDK v2**، وهو خط الإصدار المستقر الحالي.

## البنية

V30.1 يبقى محرك جمع وتحليل البيانات:
Binance → Collector → Redis/PostgreSQL → Intelligence → snapshots

V31.1 يضيف:
PostgreSQL → MCP Server → MCP Client/Host

## الأدوات

- `get_top_opportunities`
- `analyze_symbol`
- `get_signal_history`
- `get_market_health`
- `get_binance_price`
- `get_pattern_stats`

الخادم Read-only ولا يرسل أوامر تداول.

## تشغيل مستقل

```bash
pip install -r requirements-mcp.txt
python -m mcp_server.server
```

نقطة MCP:
`http://HOST:8001/mcp`

## دمج Docker

أضف محتوى `docker-compose.mcp.yml` إلى ملف Docker Compose الرئيسي في V30.1
أو شغّله مع نفس مشروع Compose، بشرط أن يكون `postgres` اسم خدمة قاعدة البيانات.

لا نغيّر Collector أو Intelligence في هذه المرحلة.

## ملاحظة أمان

عند نشره على الإنترنت يجب وضع HTTPS ومصادقة مناسبة قبل ربطه بعميل خارجي.
