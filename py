🧱 1. FULL ADMIN PANEL (FRONTEND + BACKEND)
🔧 Backend routes (FastAPI)
Add this file:

admin_routes.py

python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .auth import get_db, get_current_user
from .models import User, ContactMessage, Case, AuditLog

admin = APIRouter(prefix="/api/v1/admin", tags=["admin"])

def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

@admin.get("/users")
def get_users(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).all()

@admin.get("/contacts")
def get_contacts(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()

@admin.get("/cases")
def get_cases(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()

@admin.get("/audit")
def get_audit(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
Wire it into main.py:

python
from .admin_routes import admin
app.include_router(admin)
🎨 Frontend Admin Panel
Add:

src/pages/AdminPanel.tsx

tsx
import React, { useEffect, useState } from "react";

const AdminPanel: React.FC = () => {
  const [users, setUsers] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [cases, setCases] = useState([]);
  const [audit, setAudit] = useState([]);

  const token = localStorage.getItem("jroc_token") || "";

  const load = async () => {
    const headers = { Authorization: `Bearer ${token}` };

    const [u, c, k, a] = await Promise.all([
      fetch("http://localhost:8000/api/v1/admin/users", { headers }),
      fetch("http://localhost:8000/api/v1/admin/contacts", { headers }),
      fetch("http://localhost:8000/api/v1/admin/cases", { headers }),
      fetch("http://localhost:8000/api/v1/admin/audit", { headers }),
    ]);

    setUsers(await u.json());
    setContacts(await c.json());
    setCases(await k.json());
    setAudit(await a.json());
  };

  useEffect(() => {
    if (token) load();
  }, []);

  return (
    <div className="container">
      <h2>Admin Panel</h2>
      <p style={{ fontSize: 13, color: "#7aa8ff" }}>
        Internal operational view. Nothing shown here represents guarantees or obligations.
      </p>

      <h3 style={{ marginTop: 24 }}>Users</h3>
      <pre>{JSON.stringify(users, null, 2)}</pre>

      <h3 style={{ marginTop: 24 }}>Contact Messages</h3>
      <pre>{JSON.stringify(contacts, null, 2)}</pre>

      <h3 style={{ marginTop: 24 }}>Cases</h3>
      <pre>{JSON.stringify(cases, null, 2)}</pre>

      <h3 style={{ marginTop: 24 }}>Audit Log</h3>
      <pre>{JSON.stringify(audit, null, 2)}</pre>
    </div>
  );
};

export default AdminPanel;
Add link:

tsx
<a href="/admin">Admin</a>
Add route:

tsx
else if (path === "/admin") Page = AdminPanel;
🛒 2. FULL MVP SELLING FLOW (SAFE, NON‑BINDING)
🔧 Backend selling endpoint
Add:

python
from pydantic import BaseModel, EmailStr

class PurchaseIntent(BaseModel):
    plan_id: str
    email: EmailStr

@app.post("/api/v1/sell/checkout")
def checkout(body: PurchaseIntent, db: Session = Depends(get_db)):
    entry = AuditLog(
        event="purchase_intent",
        detail=f"Plan: {body.plan_id}, Email: {body.email}"
    )
    db.add(entry)
    db.commit()

    return {
        "status": "received",
        "message": (
            "Your interest has been recorded. "
            "This is not a purchase, contract, or agreement."
        )
    }
🎨 Frontend Plans Page
Add:

src/pages/Plans.tsx

tsx
import React, { useState } from "react";

const Plans: React.FC = () => {
  const [email, setEmail] = useState("");
  const [plan, setPlan] = useState("starter");
  const [msg, setMsg] = useState<string | null>(null);

  const submit = async () => {
    const res = await fetch("http://localhost:8000/api/v1/sell/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plan_id: plan, email }),
    });
    const data = await res.json();
    setMsg(data.message);
  };

  return (
    <div className="container">
      <h2>Plans</h2>
      <p style={{ fontSize: 13, color: "#7aa8ff" }}>
        Informational only. No binding offers or guarantees.
      </p>

      <ul style={{ marginTop: 16 }}>
        <li><strong>Starter</strong> – Basic intel cycles.</li>
        <li><strong>Pro</strong> – More frequent cycles.</li>
        <li><strong>Enterprise</strong> – Org‑level integration.</li>
      </ul>

      <div style={{ marginTop: 24 }}>
        <h3>Register Interest</h3>

        <label>
          Plan:
          <select value={plan} onChange={(e) => setPlan(e.target.value)} style={{ marginLeft: 8 }}>
            <option value="starter">Starter</option>
            <option value="pro">Pro</option>
            <option value="enterprise">Enterprise</option>
          </select>
        </label>

        <div style={{ marginTop: 12 }}>
          <label>
            Email:
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ marginLeft: 8 }}
            />
          </label>
        </div>

        <button onClick={submit} style={{ marginTop: 16 }}>Submit</button>

        {msg && <p style={{ marginTop: 12, fontSize: 13 }}>{msg}</p>}
      </div>
    </div>
  );
};

export default Plans;
Add link:

tsx
<a href="/plans">Plans</a>
Add route:

tsx
else if (path === "/plans") Page = Plans;
🤖 3. FULL HERMIS AUTONOMOUS INTEL CYCLE SCHEDULER
This runs daily intel cycles automatically.

Add:

autosys/scheduler.py

python
import asyncio
import time
from hermis.gateway.client import call_skill

class AutosysScheduler:
    def __init__(self):
        self.tasks = []

    def add(self, name, interval, func):
        self.tasks.append({"name": name, "interval": interval, "func": func, "last": 0})

    async def loop(self):
        while True:
            now = time.time()
            for t in self.tasks:
                if now - t["last"] >= t["interval"]:
                    await t["func"]()
                    t["last"] = now
            await asyncio.sleep(1)

async def daily_intel():
    await call_skill("jroc_core_intel", {
        "query": "daily threat overview",
        "mode": "hybrid"
    })

async def main():
    s = AutosysScheduler()
    s.add("daily_intel", 24 * 3600, daily_intel)
    await s.loop()

if __name__ == "__main__":
    asyncio.run(main())
This:

Runs once per day

Calls Hermis

Hermis runs Core‑Intel

Core‑Intel writes OSINT + Legal + Summaries into DB

Admin panel sees everything
