import asyncio
from httpx import AsyncClient
import uuid

async def test_workflow():
    async with AsyncClient(base_url="http://localhost:8000", timeout=60.0) as client:
        # 1. Register/Login
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "testpassword"
        print(f"Registering user {email}...")
        resp = await client.post("/api/auth/register", json={"email": email, "password": password, "full_name": "Test User"})
        assert resp.status_code == 200, f"Register failed: {resp.text}"
        
        print("Logging in...")
        resp = await client.post("/api/auth/login", json={"email": email, "password": password})
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        token = resp.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Discovery
        print("Running discovery...")
        resp = await client.post("/api/businesses/discover", json={"query": "coffee", "region": "Seattle"}, headers=headers)
        resp = await client.post("/api/businesses/discover", json={"query": "coffee", "region": "Seattle"}, headers=headers)
        assert resp.status_code == 200, f"Discovery failed: {resp.text}"
        print(resp.json())
        
        print("Fetching businesses...")
        resp = await client.get("/api/businesses", headers=headers)
        assert resp.status_code == 200, f"Get businesses failed: {resp.text}"
        discovered = resp.json()["results"]
        print(f"Total businesses: {resp.json()['total']}")
        if not discovered:
            print("No businesses discovered, try another query.")
            return

        biz_id = discovered[0]["id"]
        
        # 3. Create/Link Lead (discovery automatically creates leads)
        print("Fetching leads...")
        resp = await client.get("/api/crm/leads", headers=headers)
        assert resp.status_code == 200, f"Get leads failed: {resp.text}"
        leads = resp.json()["results"]
        
        lead = next((l for l in leads if l["business_id"] == biz_id), None)
        assert lead, "Lead was not created for discovered business."
        lead_id = lead["id"]
        print(f"Lead ID: {lead_id}")
        
        # 4. Qualification
        print("Qualifying lead...")
        resp = await client.put(f"/api/crm/leads/{lead_id}", json={"status": "contacted"}, headers=headers)
        assert resp.status_code == 200, f"Qualify failed: {resp.text}"
        print("Lead qualified.")
        
        # 5. Business Intelligence & Opportunity
        print("Fetching business intelligence...")
        slug = discovered[0]["slug"]
        
        # We need to trigger an analysis first to make sure there's intelligence data
        print("Triggering analysis...")
        resp = await client.post(f"/api/businesses/{slug}/intelligence/analyze", headers=headers)
        assert resp.status_code == 200, f"Analysis failed: {resp.text}"
        bi_id = resp.json()["id"]
        
        print("Generating opportunity...")
        resp = await client.post(f"/api/businesses/{slug}/intelligence/{bi_id}/opportunity/generate", headers=headers)
        assert resp.status_code == 200, f"Opportunity generation failed: {resp.text}"
        opp_id = resp.json()["id"]

        # 6. Outreach
        print("Generating outreach...")
        resp = await client.get(f"/api/businesses/{slug}/opportunity/{opp_id}/outreach?strategy=value_first&channel=email", headers=headers)
        assert resp.status_code == 200, f"Outreach failed: {resp.text}"
        print("Outreach generated.")
        
        # 7. Proposal
        print("Generating proposal...")
        resp = await client.post(f"/api/businesses/{slug}/opportunity/{opp_id}/proposal/generate?template_type=standard", headers=headers)
        assert resp.status_code == 200, f"Proposal failed: {resp.text}"
        print("Proposal generated.")
        
        # 8. Analytics
        print("Fetching stats...")
        resp = await client.get("/api/businesses/stats", headers=headers)
        assert resp.status_code == 200, f"Stats failed: {resp.text}"
        print(f"Stats: {resp.json()}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
