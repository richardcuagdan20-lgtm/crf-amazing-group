
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = "http://127.0.0.1:4321"
SHOTS = Path("/workspace/mamcris-site/site/screenshots")
SHOTS.mkdir(parents=True, exist_ok=True)
ISSUES = []

def shot(page, name):
    page.screenshot(path=str(SHOTS / name), full_page=True)

def collect_a11y_issues(page, label):
    missing_alt = page.locator("img:not([alt])").count()
    if missing_alt:
        ISSUES.append(f"{label}: {missing_alt} img(s) missing alt")
    # empty buttons
    for loc in page.locator("button").all():
        text = (loc.inner_text() or "").strip()
        aria = loc.get_attribute("aria-label") or ""
        if not text and not aria:
            ISSUES.append(f"{label}: button without accessible name")

def check_contacts(page, label):
    html = page.content()
    needed = [
        "tel:+639776821438",
        "viber://chat?number=%2B639776821438",
        "https://wa.me/639776821438",
        "mailto:crystalflores.rpmmc@gmail.com",
    ]
    for href in needed:
        if href not in html:
            ISSUES.append(f"{label}: missing {href}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Desktop Home
        desktop = browser.new_context(viewport={"width": 1440, "height": 900})
        page = desktop.new_page()
        page.goto(f"{BASE}/", wait_until="networkidle")
        expect(page.get_by_role("heading", name="Crystal Flores")).to_be_visible()
        expect(page.get_by_role("heading", name="Handover Releases")).to_be_visible()
        expect(page.get_by_text("0977 682 1438").first).to_be_visible()
        expect(page.get_by_role("link", name="Browse projects")).to_be_visible()
        expect(page.get_by_role("heading", name="Global CRF teams")).to_be_visible()
        expect(page.get_by_text("independent", exact=False)).to_be_visible()
        page.screenshot(path=str(SHOTS / "home-desktop-fold.png"), full_page=False)
        rfo = page.locator(".release-card")
        count = rfo.count()
        print(f"Handover cards: {count}")
        if count != 0:
            ISSUES.append(f"Home: handover should be empty until Crystal sends the list, got {count} cards")
        handover = page.locator("#handover-title").locator("xpath=ancestor::section[1]")
        htext = handover.inner_text()
        if "coming soon" not in htext.lower():
            ISSUES.append("Home: missing handover placeholder copy")
        if "AmiSa" in htext or "Aurora Escalades" in htext or "Trion" in htext:
            ISSUES.append("Home: auto-filled project names still appear in Handover Releases")
        if "invented" in htext.lower() or "as published" in htext.lower():
            ISSUES.append("Home: internal wording still in handover section")
        viber = handover.get_by_role("link", name="Viber")
        wa = handover.get_by_role("link", name="WhatsApp")
        if viber.count() < 1 or wa.count() < 1:
            ISSUES.append("Home: placeholder missing Viber/WhatsApp")
        check_contacts(page, "Home")
        collect_a11y_issues(page, "Home desktop")
        shot(page, "home-desktop.png")

        # Projects
        page.goto(f"{BASE}/projects", wait_until="networkidle")
        expect(page.get_by_role("heading", name="Projects")).to_be_visible()
        items = page.locator("#project-dir .dir-item")
        all_count = items.count()
        print(f"Projects all: {all_count}")
        if all_count != 18:
            ISSUES.append(f"Projects: expected 18, got {all_count}")
        # Filter Pasig City
        page.get_by_role("navigation", name="Filter by location").get_by_role("link", name="Pasig City").click()
        page.wait_for_timeout(200)
        visible = page.locator("#project-dir .dir-item:not([hidden])").count()
        print(f"Pasig filter visible: {visible}")
        if visible != 5:
            ISSUES.append(f"Projects Pasig filter: expected 5, got {visible}")
        # House and lot from all locations
        page.get_by_role("navigation", name="Filter by location").get_by_role("link", name="All locations").click()
        page.get_by_role("navigation", name="Filter by type").get_by_role("link", name="House and lot").click()
        page.wait_for_timeout(200)
        visible = page.locator("#project-dir .dir-item:not([hidden])").count()
        print(f"House-and-lot visible: {visible}")
        if visible != 4:
            ISSUES.append(f"Projects house-and-lot filter: expected 4, got {visible}")
        page.get_by_role("navigation", name="Filter by type").get_by_role("link", name="All types").click()
        page.wait_for_timeout(200)
        shot(page, "projects-desktop.png")

        # Project page
        page.goto(f"{BASE}/projects/aurora-escalades", wait_until="networkidle")
        expect(page.get_by_role("heading", name="Aurora Escalades", exact=True)).to_be_visible()
        expect(page.get_by_role("heading", name="Gallery")).to_be_visible()
        expect(page.get_by_role("link", name="Inquire on WhatsApp")).to_be_visible()
        wa = page.get_by_role("link", name="Inquire on WhatsApp").get_attribute("href") or ""
        if "wa.me/639776821438" not in wa or "Aurora" not in wa:
            ISSUES.append(f"Project inquire WhatsApp href unexpected: {wa}")
        check_contacts(page, "Project")
        shot(page, "project-aurora-escalades-desktop.png")

        # About / Careers / Contact
        page.goto(f"{BASE}/about", wait_until="networkidle")
        expect(page.get_by_text("fourteen years", exact=False)).to_be_visible()
        expect(page.get_by_text("Registered Nurse", exact=False)).to_be_visible()
        shot(page, "about-desktop.png")

        page.goto(f"{BASE}/careers", wait_until="networkidle")
        expect(page.get_by_role("heading", name="Join Global CRF Amazing")).to_be_visible()
        shot(page, "careers-desktop.png")

        page.goto(f"{BASE}/contact", wait_until="networkidle")
        expect(page.get_by_role("heading", name="Contact Crystal")).to_be_visible()
        page.fill("#name", "Test Buyer")
        page.fill("#reach", "09171234567")
        page.select_option("#project", "Aurora Escalades")
        page.fill("#message", "I would like a unit walkthrough.")
        hrefs = page.evaluate("""() => {
          const form = document.getElementById("inquiry-form");
          const fd = new FormData(form);
          const name = String(fd.get("name") || "").trim();
          const reach = String(fd.get("reach") || "").trim();
          const country = String(fd.get("country") || "").trim();
          const project = String(fd.get("project") || "").trim();
          const message = String(fd.get("message") || "").trim();
          const lines = [
            `Hi Crystal, my name is ${name || "(name)"}.`,
            reach ? `You can reach me at ${reach}.` : "",
            country ? `I am based in ${country}.` : "",
            project ? `I am inquiring about ${project}.` : "I would like to inquire about a home.",
            message,
          ].filter(Boolean);
          const body = lines.join(" ");
          const subject = encodeURIComponent(project ? `Inquiry: ${project}` : "Inquiry from the CRF Amazing Group website");
          return {
            email: `mailto:crystalflores.rpmmc@gmail.com?subject=${subject}&body=${encodeURIComponent(body)}`,
            whatsapp: `https://wa.me/639776821438?text=${encodeURIComponent(body)}`,
          };
        }""")
        if "mailto:crystalflores.rpmmc@gmail.com" not in hrefs["email"] or "Aurora" not in hrefs["email"]:
            ISSUES.append(f"Contact form email payload unexpected: {hrefs['email'][:200]}")
        else:
            print("mailto payload ok")
        if "wa.me/639776821438" not in hrefs["whatsapp"] or "Aurora" not in hrefs["whatsapp"]:
            ISSUES.append(f"Contact form WhatsApp payload unexpected: {hrefs['whatsapp'][:200]}")
        else:
            print("whatsapp payload ok")
        shot(page, "contact-desktop.png")
        desktop.close()

        # Mobile Home + sticky
        mobile = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            has_touch=True,
        )
        m = mobile.new_page()
        m.goto(f"{BASE}/", wait_until="networkidle")
        expect(m.get_by_role("button", name="Contact Crystal")).to_be_visible()
        # sticky should be visible; header call buttons hidden
        if m.locator(".header-actions").is_visible():
            ISSUES.append("Mobile: header-actions still visible (should hide under 720px)")
        m.locator("#sticky-toggle").click(force=True)
        expect(m.locator("#sticky-panel").get_by_role("link", name="Viber")).to_be_visible()
        collect_a11y_issues(m, "Home mobile")
        shot(m, "home-mobile.png")

        m.goto(f"{BASE}/projects", wait_until="networkidle")
        shot(m, "projects-mobile.png")
        m.goto(f"{BASE}/projects/aurora-escalades", wait_until="networkidle")
        shot(m, "project-aurora-escalades-mobile.png")
        mobile.close()
        browser.close()

    report = SHOTS / "qa-report.txt"
    text = "ISSUES:\n" + ("\n".join(ISSUES) if ISSUES else "none")
    report.write_text(text)
    print(text)
    if ISSUES:
        raise SystemExit(1)

if __name__ == "__main__":
    run()
