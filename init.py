import asyncio, os, asyncpg
async def main():
    con=await asyncpg.connect(os.getenv('DATABASE_URL','postgresql://hashim:hashim@postgres:5432/hashim'))
    sql=open('/app/db/schema.sql').read(); await con.execute(sql); await con.close()
if __name__=='__main__': asyncio.run(main())
