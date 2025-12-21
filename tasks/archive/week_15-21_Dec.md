# This Week Plan (15–21 Dec 2025)

## Legal & Finance

- [ ] Create consolidated registry of all obligations  
  - Credits, debts, court cases, banks, MFIs, UBKI, gov cabinets  
  - Fields: type, amount, deadline, status, link, comments  

- [ ] Check актуальні статуси по ключових сервісах  
  - cabinet.court.gov.ua  
  - bank.gov.ua  
  - основні кредит-сервіси та банки  
  - Update registry with deadlines / risks  

- [ ] Add all legal/finance deadlines to Proton Calendar  
  - Create separate events per item  
  - Add links to cabinets/docs into descriptions  
  - Set reminders (1–3 days before)  

- [ ] Configure monitoring for legal/finance  
  - UBKI доступ і регулярна перевірка  
  - Email notifications from banks / credit services to Proton Mail  
  - Filters + labels: `Legal`, `Finance`  

---

## Infra & Privacy (Proton + Domains)

- [ ] Organize Proton Mail & Drive  
  - Folders/labels: `Legal`, `Finance`, `Infra`, `Projects/Bakhmach-Business-Hub`  
  - Move key emails and files into corresponding folders  

- [ ] Structure Proton Pass  
  - Records for: banks, gov cabinets, Cloudflare, GitHub, Unstoppable Domains, other critical services  
  - Add tags by category (e.g. `bank`, `gov`, `infra`, `project`)  

- [ ] Audit Cloudflare zones & DNS  
  - List all zones and active domains  
  - Check DNS records, SSL, redirects  
  - Create `docs/DNS.md` with current schema (what domain → what service)  

- [ ] Review Unstoppable Domains usage  
  - List purchased domains and current bindings  
  - Decide which domains to actively use in next 1–3 months  
  - Ideas: wallet card, project landing, identity  

---

## Bakhmach-Business-Hub (Product & Code)

- [ ] Create `ROADMAP.md`  
  - Describe MVP scope (core features)  
  - Infra integrations: Cloudflare, Proton (Mail/Drive/Calendar/Pass), possible AI agents  
  - Outline 2–3 stages: `MVP 0.1`, `Infra setup`, `Automation`  

- [ ] Create `tasks/` structure  
  - `tasks/this_week.md` (this file)  
  - `tasks/backlog.md` for future ideas  
  - `tasks/infra.md` for infra-specific tasks  

- [ ] Create 5–10 GitHub issues  
  - Split MVP into small actionable tasks  
  - Labels idea: `infra`, `mvp`, `automation`, `legal/finance`, `docs`  
  - Link issues back to `ROADMAP.md` where relevant  

- [ ] Create milestones  
  - `MVP 0.1` — базовий функціонал  
  - `Infra setup` — домени, DNS, інтеграції з Proton  
  - `Automation` — перші автоматизації/агенти  

---

## Automation Ideas (Draft)

- [ ] Describe 3–5 automation scenarios  
  - Notifications for courts/banks/credits changes  
  - Daily/weekly digest from Mail + Calendar  
  - Automatic financial status snapshot  

- [ ] Decide tech for each scenario  
  - Zapier / Make / custom Python scripts / AI agents  
  - Rough priority: what saves the most time / зменшує ризики  

---

## Weekly Review

- [ ] Weekly review (Sun)  
  - What is done in Legal & Finance  
  - What is done in Infra & Privacy  
  - What is done in Bakhmach-Business-Hub (product + code)  
  - Update `tasks/next_week.md` and Proton Calendar
