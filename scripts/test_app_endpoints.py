import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ai-engine"))
import asyncio
import httpx
from app import app

async def test_endpoints():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Test normal payload
        r = await client.post(
            "/api/v1/pipeline/run",
            json={
                "story_id": "test_echo_story",
                "title": "The Echo of Station 9",
                "content_or_path": "A mysterious radio signal on station 9.",
                "duration_presets": ["quick"],
                "languages": ["hi", "mr"],
            },
        )
        print("Normal payload response:", r.status_code, r.json())
        assert r.status_code == 200, f"Expected 200 but got {r.status_code}"

        # 2. Test empty payload
        r_empty = await client.post("/api/v1/pipeline/run", json={})
        print("Empty payload response:", r_empty.status_code, r_empty.json())
        assert r_empty.status_code == 200, f"Expected 200 for empty body, got {r_empty.status_code}"

        # 3. Test null payload / empty content
        r_none = await client.post("/api/v1/pipeline/run", content=b"")
        print("No-content payload response:", r_none.status_code, r_none.json())
        assert r_none.status_code == 200, f"Expected 200 for no content, got {r_none.status_code}"

    print("\nALL FASTAPI ENDPOINT TESTS PASSED WITH 200 OK!")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
