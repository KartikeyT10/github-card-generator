from mcp.server.fastmcp import FastMCP
import httpx
import os
import json
from typing import Dict, List, Any
from pathlib import Path
from google import generativeai as genai
from dotenv import load_dotenv

load_dotenv()

CARD_DIR = Path(os.getenv("CARD_DIR") or ("/tmp/cards" if os.getenv("VERCEL") else "static/cards"))

# Initialize FastMCP
mcp = FastMCP("GitHub Card Generator")

# Configure Gemini for analyze_profile (Using Gemini 2.5 Flash Lite)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

@mcp.tool()
async def scrape_github(username: str) -> str:
    """
    Fetch GitHub user statistics and top repositories.
    Returns: name, bio, location, public_repos, followers, top 6 repos, and languages.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
        
    async with httpx.AsyncClient(headers=headers) as client:
        # User Profile
        user_res = await client.get(f"https://api.github.com/users/{username}")
        user_res.raise_for_status()
        user_data = user_res.json()

        # Repositories (sort by stars to get top ones)
        repos_res = await client.get(f"https://api.github.com/users/{username}/repos?sort=stars&per_page=100")
        repos_res.raise_for_status()
        repos_data = repos_res.json()

    # Top 6 repos by stars
    top_repos_raw = sorted(repos_data, key=lambda x: x.get('stargazers_count', 0), reverse=True)[:6]
    top_repos = [{
        "name": r["name"],
        "stars": r["stargazers_count"],
        "language": r["language"],
        "description": r["description"]
    } for r in top_repos_raw]

    # Aggregate Languages
    languages = {}
    for r in repos_data:
        lang = r.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    
    # Sort languages by usage
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    most_used_languages = [l[0] for l in sorted_langs[:5]]

    return json.dumps({
        "name": user_data.get("name") or username,
        "avatar_url": user_data.get("avatar_url"),
        "bio": user_data.get("bio"),
        "location": user_data.get("location"),
        "public_repos": user_data.get("public_repos"),
        "followers": user_data.get("followers"),
        "top_repos": top_repos,
        "languages": most_used_languages
    })

@mcp.tool()
async def analyze_profile(github_data: str) -> str:
    """
    Analyze GitHub data using Gemini 2.5 Flash.
    Returns: developer_vibe, top_skills, fun_fact, card_theme.
    """
    prompt = f"""
    Analyze this GitHub profile data and return a strict JSON object.
    
    Required Fields:
    1. "developer_vibe": A witty 1-sentence personality description.
    2. "top_skills": A list of exactly 3 technical skills or areas of expertise.
    3. "fun_fact": A clever or surprising observation inferred from their repositories.
    4. "card_theme": Exactly one of: "hacker", "builder", "researcher", "designer", "open-source-hero".

    Developer Data: {json.dumps(github_data)}
    
    Return ONLY the JSON.
    """
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Simple JSON extraction from markdown if necessary
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
        
    # Ensure it's valid JSON before returning
    parsed = json.loads(text)
    return json.dumps(parsed)

@mcp.tool()
async def generate_card_html(username: str, github_data: str, analysis: str) -> str:
    """
    Generate a self-contained, beautifully styled HTML string for the dev card.
    Supports themes: hacker (dark), builder (light), researcher, designer, open-source-hero.
    """
    try:
        github_data_parsed = json.loads(github_data)
    except Exception:
        github_data_parsed = {}
        
    try:
        analysis_parsed = json.loads(analysis)
    except Exception:
        analysis_parsed = {}
        
    theme_name = analysis_parsed.get("card_theme", "builder")
    
    themes = {
        "hacker": {
            "bg": "radial-gradient(circle at top left, #0b0f19, #020408)",
            "card_bg": "rgba(13, 17, 23, 0.75)",
            "card_glow": "rgba(46, 164, 79, 0.15)",
            "text": "#f0f6fc",
            "text_secondary": "#8b949e",
            "accent": "#2ea44f",
            "accent_glow": "rgba(46, 164, 79, 0.4)",
            "border": "1px solid rgba(48, 54, 61, 0.8)",
            "badge_bg": "rgba(46, 164, 79, 0.15)",
            "badge_color": "#2ea44f",
            "fun_fact_bg": "rgba(46, 164, 79, 0.05)"
        },
        "builder": {
            "bg": "radial-gradient(circle at top left, #f8fafc, #f1f5f9)",
            "card_bg": "rgba(255, 255, 255, 0.85)",
            "card_glow": "rgba(37, 99, 235, 0.1)",
            "text": "#1e293b",
            "text_secondary": "#64748b",
            "accent": "#2563eb",
            "accent_glow": "rgba(37, 99, 235, 0.3)",
            "border": "1px solid rgba(226, 232, 240, 0.8)",
            "badge_bg": "rgba(37, 99, 235, 0.1)",
            "badge_color": "#2563eb",
            "fun_fact_bg": "rgba(37, 99, 235, 0.03)"
        },
        "researcher": {
            "bg": "radial-gradient(circle at top left, #f0fdf4, #dcfce7)",
            "card_bg": "rgba(255, 255, 255, 0.85)",
            "card_glow": "rgba(22, 163, 74, 0.1)",
            "text": "#0f172a",
            "text_secondary": "#475569",
            "accent": "#16a34a",
            "accent_glow": "rgba(22, 163, 74, 0.3)",
            "border": "1px solid rgba(222, 247, 236, 0.8)",
            "badge_bg": "rgba(22, 163, 74, 0.1)",
            "badge_color": "#16a34a",
            "fun_fact_bg": "rgba(22, 163, 74, 0.03)"
        },
        "designer": {
            "bg": "radial-gradient(circle at top left, #faf5ff, #f3e8ff)",
            "card_bg": "rgba(255, 255, 255, 0.85)",
            "card_glow": "rgba(147, 51, 234, 0.1)",
            "text": "#1e293b",
            "text_secondary": "#64748b",
            "accent": "#9333ea",
            "accent_glow": "rgba(147, 51, 234, 0.3)",
            "border": "1px solid rgba(243, 232, 255, 0.8)",
            "badge_bg": "rgba(147, 51, 234, 0.1)",
            "badge_color": "#9333ea",
            "fun_fact_bg": "rgba(147, 51, 234, 0.03)"
        },
        "open-source-hero": {
            "bg": "radial-gradient(circle at top left, #fffbeb, #fef3c7)",
            "card_bg": "rgba(255, 255, 255, 0.85)",
            "card_glow": "rgba(217, 119, 6, 0.1)",
            "text": "#1e293b",
            "text_secondary": "#64748b",
            "accent": "#d97706",
            "accent_glow": "rgba(217, 119, 6, 0.3)",
            "border": "1px solid rgba(254, 243, 199, 0.8)",
            "badge_bg": "rgba(217, 119, 6, 0.1)",
            "badge_color": "#d97706",
            "fun_fact_bg": "rgba(217, 119, 6, 0.03)"
        }
    }
    
    c = themes.get(theme_name, themes["builder"])
    
    skills_html = "".join([f'<div class="badge">{skill}</div>' for skill in analysis_parsed.get("top_skills", [])])
    
    repos_html = "".join([
        f'''<div class="repo">
            <div class="repo-header">
                <span class="repo-name">{r["name"]}</span>
                <span class="stars">Stars: {r["stars"]}</span>
            </div>
            <div class="repo-lang">{r["language"] or "Mixed"}</div>
        </div>'''
        for r in github_data_parsed.get("top_repos", [])[:3]
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ 
            margin: 0; 
            padding: 40px 20px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            background: {c['bg']}; 
            min-height: 100vh;
            font-family: 'Outfit', sans-serif;
            box-sizing: border-box;
        }}
        .card {{
            width: 440px; 
            background: {c['card_bg']}; 
            border: {c['border']};
            border-radius: 24px; 
            padding: 32px; 
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.02), inset 0 1px 0 rgba(255,255,255,0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            color: {c['text']};
            position: relative;
            overflow: hidden;
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
        }}
        .card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, {c['card_glow']} 0%, transparent 70%);
            z-index: 0;
            pointer-events: none;
        }}
        .card:hover {{
            transform: translateY(-8px) scale(1.01);
            box-shadow: 0 30px 60px {c['card_glow']}, 0 4px 10px rgba(0, 0, 0, 0.05);
        }}
        .header {{ 
            display: flex; 
            align-items: center; 
            gap: 20px; 
            margin-bottom: 24px;
            position: relative;
            z-index: 1;
        }}
        .avatar-container {{
            position: relative;
        }}
        .avatar {{ 
            width: 80px; 
            height: 80px; 
            border-radius: 22px; 
            border: 3px solid {c['accent']};
            box-shadow: 0 8px 16px {c['accent_glow']};
            object-fit: cover;
        }}
        .header-text {{
            flex: 1;
        }}
        .name {{ 
            margin: 0; 
            font-size: 26px; 
            font-weight: 800; 
            color: {c['text']}; 
            letter-spacing: -0.5px;
            line-height: 1.2;
        }}
        .theme-pill {{
            display: inline-block;
            margin-top: 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: {c['badge_color']};
            background: {c['badge_bg']};
            padding: 3px 10px;
            border-radius: 20px;
        }}
        .vibe {{ 
            margin: 0 0 24px 0; 
            font-size: 15px; 
            color: {c['text_secondary']}; 
            line-height: 1.6;
            position: relative;
            z-index: 1;
            font-weight: 400;
        }}
        .badges {{ 
            display: flex; 
            gap: 8px; 
            margin-bottom: 28px; 
            flex-wrap: wrap;
            position: relative;
            z-index: 1;
        }}
        .badge {{ 
            background: {c['badge_bg']}; 
            color: {c['badge_color']}; 
            padding: 6px 14px; 
            border-radius: 100px; 
            font-size: 12px; 
            font-weight: 600;
            transition: transform 0.2s ease, background 0.2s ease;
        }}
        .badge:hover {{
            transform: translateY(-2px);
            background: {c['accent']};
            color: #ffffff;
        }}
        .stats {{ 
            display: flex; 
            gap: 32px; 
            margin-bottom: 28px; 
            border-top: 1px solid rgba(0,0,0,0.06);
            border-bottom: 1px solid rgba(0,0,0,0.06); 
            padding: 20px 0;
            position: relative;
            z-index: 1;
        }}
        .stat-item {{ 
            font-size: 13px; 
            color: {c['text_secondary']};
            font-weight: 500;
        }}
        .stat-val {{ 
            font-weight: 800; 
            font-size: 22px; 
            color: {c['text']}; 
            line-height: 1;
            display: inline-block;
            margin-bottom: 4px;
        }}
        .repos-title {{ 
            font-size: 12px; 
            font-weight: 800; 
            text-transform: uppercase; 
            color: {c['text_secondary']}; 
            margin-bottom: 16px; 
            letter-spacing: 1px;
            position: relative;
            z-index: 1;
        }}
        .repos-list {{
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .repo {{ 
            background: rgba(0,0,0,0.015);
            border: 1px solid rgba(0,0,0,0.03);
            border-radius: 14px;
            padding: 12px 16px; 
            transition: all 0.2s ease;
        }}
        .repo:hover {{
            background: {c['card_bg']};
            border-color: {c['accent']};
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            transform: translateX(4px);
        }}
        .repo-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }}
        .repo-name {{
            font-weight: 600;
            font-size: 14px;
            color: {c['text']};
        }}
        .stars {{ 
            color: {c['accent']}; 
            font-size: 12px; 
            font-weight: 700; 
            background: {c['badge_bg']};
            padding: 2px 8px;
            border-radius: 8px;
        }}
        .repo-lang {{
            font-size: 12px;
            color: {c['text_secondary']};
        }}
        .fun-fact {{ 
            margin-top: 28px; 
            padding: 16px; 
            background: {c['fun_fact_bg']}; 
            border-radius: 16px; 
            font-size: 13px; 
            line-height: 1.6;
            border: 1px dashed {c['accent_glow']};
            position: relative;
            z-index: 1;
            color: {c['text']};
        }}
        .fun-fact strong {{
            color: {c['badge_color']};
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="avatar-container">
                <img src="{github_data_parsed['avatar_url']}" alt="{username}" class="avatar">
            </div>
            <div class="header-text">
                <h1 class="name">{github_data_parsed['name']}</h1>
                <div class="theme-pill">{theme_name.replace('-', ' ')}</div>
            </div>
        </div>
        <p class="vibe">{analysis_parsed['developer_vibe']}</p>
        <div class="badges">{skills_html}</div>
        <div class="stats">
            <div class="stat-item"><span class="stat-val">{github_data_parsed['public_repos']}</span><br>Repositories</div>
            <div class="stat-item"><span class="stat-val">{github_data_parsed['followers']}</span><br>Followers</div>
        </div>
        <div class="repos-title">Top Repositories</div>
        <div class="repos-list">{repos_html}</div>
        <div class="fun-fact">
            <strong>Fun Fact:</strong> {analysis_parsed['fun_fact']}
        </div>
    </div>
</body>
</html>"""
    
    # Save the card
    base_path = CARD_DIR
    base_path.mkdir(parents=True, exist_ok=True)
    file_name = f"{username}.html"
    file_path = base_path / file_name
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    return f"/card/{username}"

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """
    Save the HTML dev card to the static directory.
    Returns the relative URL path.
    """
    base_path = CARD_DIR
    base_path.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{username}.html"
    file_path = base_path / file_name
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return f"/card/{username}"

if __name__ == "__main__":
    mcp.run()
