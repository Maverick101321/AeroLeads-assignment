import re
import json
from bs4 import BeautifulSoup


WS_RE = re.compile(r'\s+')

def clean_text(s: str) -> str:
    if not s: return ""
    return WS_RE.sub(" ", s).strip()

def get_text(el) -> str:
    return clean_text(el.get_text(" ", strip=True)) if el else ""

def get_section_by_anchor(soup: BeautifulSoup, anchor_id: str):
    """Finds <div id="{anchor_id}"> then climbs to its nearest <section> wrapper."""
    anchor = soup.select_one(f'div#{anchor_id}')
    if not anchor:
        return None
    return anchor.find_parent("section")

def dedupe_phrase(s: str) -> str:
    # remove immediate duplicate tokens like "Founder Founder"
    parts = [p for p in s.split() if p]
    out = []
    for i, p in enumerate(parts):
        if i > 0 and p == parts[i-1]:
            continue
        out.append(p)
    return " ".join(out).strip()

def dedupe_neighbor_strings(a: str, b: str) -> tuple[str, str]:
    # if a and b are identical, blank b
    if a and b and a.strip().lower() == b.strip().lower():
        return a, ""
    return a, b

def extract_header(soup: BeautifulSoup):
    name = ""
    headline = ""
    location = ""

    h1 = soup.select_one("main h1") or soup.select_one("h1")
    name = get_text(h1)

    # grab up to ~3 short lines under h1
    lines = []
    if h1:
        # walk a limited set of following siblings looking for short text blocks
        sib = h1.parent
        seen = 0
        while sib and seen < 8 and len(lines) < 3:
            sib = sib.find_next_sibling()
            if not sib: break
            txt = get_text(sib)
            if txt and 2 <= len(txt) <= 140:
                lines.append(txt)
            seen += 1

    # heuristic: line with a comma & no digits -> location; the other -> headline
    for line in lines:
        if ("," in line) and not re.search(r"\d", line):
            location = line if not location else location
        else:
            headline = line if not headline else headline

    return clean_text(name), clean_text(headline), clean_text(location)

def extract_about(soup: BeautifulSoup) -> str:
    # find a node whose text is exactly "About" (normalized), then take its next block of text
    hdr = None
    for el in soup.select("section *"):
        if clean_text(el.get_text()) == "About":
            hdr = el
            break
    if not hdr:
        return ""
    # grab the next block-level container with meaningful text
    cur = hdr
    for _ in range(6):
        cur = cur.find_next()
        if not cur: break
        txt = clean_text(cur.get_text(" ", strip=True))
        if txt and txt.lower() != "about":
            return txt
    return ""

MONTH_RE = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
DATE_HINT = re.compile(rf"{MONTH_RE}|\b\d{{4}}\b|Present|Current", re.I)

def extract_experiences(soup: BeautifulSoup):
    section = get_section_by_anchor(soup, "experience")
    if not section:
        return []
    ul = section.find("ul")
    if not ul:
        return []
    experiences = []
    for li in ul.find_all("li", recursive=False):
        entity = li.select_one('[data-view-name="profile-component-entity"]') or li
        block_texts = [clean_text(t) for t in entity.stripped_strings if clean_text(t)]
        if not block_texts:
            continue

        # pick bolds if present
        bolds = [get_text(b) for b in entity.select(".t-bold, strong, b") if get_text(b)]
        title = ""
        company = ""

        if len(bolds) >= 2:
            title = bolds[0]
            company = bolds[1]
        elif len(bolds) == 1:
            # try to infer the other from surrounding lines
            title = bolds[0]
            # company is next distinct line differing from title
            for line in block_texts:
                if line != title and len(line) <= 100:
                    company = line
                    break
        else:
            # fallback: first lines heuristic
            title = block_texts[0]
            if len(block_texts) > 1:
                company = block_texts[1]
        
        #Dedupe title and company
        title = dedupe_phrase(title)
        company = dedupe_phrase(company)
        title, company = dedupe_neighbor_strings(title, company)

        # dates: first small line containing month/year/present/current
        dates = ""
        for line in block_texts[:8]:
            if DATE_HINT.search(line):
                dates = line
                break

        experiences.append({
            "title": clean_text(title),
            "company": clean_text(company),
            "dates": clean_text(dates),
        })
    return experiences

def current_from_experiences(experiences):
    if not experiences:
        return "", "", ""
    for exp in experiences:
        if re.search(r"Present|Current", exp.get("dates",""), re.I):
            return exp["title"], exp["company"], exp["dates"]
    # fallback: first item
    exp = experiences[0]
    return exp["title"], exp["company"], exp["dates"]

def extract_education(soup: BeautifulSoup):
    section = get_section_by_anchor(soup, "education")
    if not section:
        return []
    ul = section.find("ul")
    if not ul:
        return []
    edu = []
    for li in ul.find_all("li", recursive=False):
        entity = li.select_one('[data-view-name="profile-component-entity"]') or li
        block_texts = [clean_text(t) for t in entity.stripped_strings if clean_text(t)]
        bolds = [get_text(b) for b in entity.select(".t-bold, strong, b") if get_text(b)]

        school = bolds[0] if bolds else (block_texts[0] if block_texts else "")
        degree = ""
        dates = ""

        # degree often appears in the next short line under school
        for line in block_texts[1:5]:
            if DATE_HINT.search(line):
                dates = line
            elif not degree and 2 <= len(line) <= 120:
                degree = line

        #Dedupe school and degree
        school = dedupe_phrase(school)
        degree = dedupe_phrase(degree)
        school, degree = dedupe_neighbor_strings(school, degree)
        
        edu.append({"school": school, "degree": degree, "dates": dates})
    return edu

def extract_skills(soup: BeautifulSoup):
    section = get_section_by_anchor(soup, "skills")
    if not section:
        return []
    items = [get_text(a) for a in section.select('a[data-field="skill_card_skill_topic"]') if get_text(a)]
    # light dedupe, keep order
    seen, out = set(), []
    for s in items:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:20]

def parse_profile(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    full_name, headline, location = extract_header(soup)
    about = extract_about(soup)
    experiences = extract_experiences(soup)
    cur_title, cur_company, cur_dates = current_from_experiences(experiences)
    education = extract_education(soup)
    skills = extract_skills(soup)

    return {
        "profile_url": "",
        "full_name": full_name,
        "headline": headline,
        "location": location,
        "about": about,
        "current_position_title": cur_title,
        "current_position_company": cur_company,
        "current_position_dates": cur_dates,
        "experiences_json": experiences,   # json.dumps later in writer
        "education_json": education,       # json.dumps later in writer
        "skills": ";".join(skills),
        "last_scraped_at": "",
    }


# === TEST HARNESS ===
if __name__ == "__main__":
    import pathlib, json
    for name in ["warikoo.html", "riteshagar.html", "nikhilkamathcio.html"]:
        fp = pathlib.Path("html_dumps")/name
        html = fp.read_text(encoding="utf-8", errors="ignore")
        d = parse_profile(html)
        print(name, "→", d["full_name"], "| exp:", len(d["experiences_json"]), "| edu:", len(d["education_json"]), "| skills:", len(d["skills"].split(";")) if d["skills"] else 0)
        if d["experiences_json"]:
            print(" sample exp:", d["experiences_json"][0])
        if d["education_json"]:
            print(" sample edu:", d["education_json"][0])
