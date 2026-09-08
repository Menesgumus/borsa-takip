import asyncio
import time
import httpx

async def load_test():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8002") as client:
        # Register a test user if doesn't exist
        await client.post("/api/v1/auth/register", json={"email": "profiler@example.com", "password": "password", "full_name": "Profiler"})
        
        # First login to get token
        resp = await client.post("/api/v1/auth/login", json={"email": "profiler@example.com", "password": "password"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
        
        token = resp.headers.get("X-Session-Token")
        cookies = {"session_token": token} if token else {}
            
        start = time.time()
        tasks = []
        for _ in range(50):
            tasks.append(client.get("/api/v1/opportunities", cookies=cookies))
            tasks.append(client.get("/api/v1/instruments", cookies=cookies))
            tasks.append(client.get("/api/v1/portfolios", cookies=cookies))
        
        responses = await asyncio.gather(*tasks)
        end = time.time()
        print(f"Executed {len(tasks)} requests in {end - start:.2f}s")
        print(f"Req/sec: {len(tasks)/(end - start):.2f}")
        for r in responses:
            if r.status_code >= 400:
                print("Error:", r.status_code, r.url, r.text)
                break

if __name__ == "__main__":
    asyncio.run(load_test())
