# HASHIM MARKET INTELLIGENCE V30.1

نسخة تدقيق وتقوية لـ V30. الهدف هنا ليس إضافة مؤشرات جديدة، بل التأكد من أن السلسلة تعمل بشكل صحيح: Binance → WebSocket Collector → Redis → PostgreSQL → Scanner → Master Score → Dashboard/Alerts.

## ما تم تقويته
- إعادة محاولة اتصال PostgreSQL عند بدء الخدمات.
- Health endpoint يفحص PostgreSQL وRedis فعليًا.
- إعادة اتصال Collector بعد انقطاع WebSocket.
- إغلاق اتصال قاعدة البيانات عند إعادة تشغيل Collector.
- إعادة استخدام HTTP client داخل Scanner بدل إنشاء عميل لكل عملة.
- تجاهل حالة السوق القديمة إذا لم يصل حدث خلال 120 ثانية.
- حدود API للاستعلامات لمنع طلبات ضخمة.
- تنظيف ملفات الاختبار والكاش من الحزمة.
- لا توجد بيانات صناعية للحيتان أو Smart Money.
- Read-only؛ لا توجد أوامر تداول.

## التشغيل
```bash
cp .env.example .env
docker compose up --build
```
ثم افتح المنفذ 8000 على الخادم.

## اختبارات
```bash
python -m pytest -q
```

## ملاحظة تشغيلية
V30.1 لا تعني أن الإشارة مضمونة. يجب أولًا تشغيل النظام وتسجيل بيانات حقيقية، ثم تقييم الأداء خارج العينة قبل استخدام النتائج لاتخاذ قرارات تداول.
