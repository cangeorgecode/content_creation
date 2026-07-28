#!/usr/bin/env python3
"""
Script Generator — AI-powered, conversion-optimized script generation
for the ContentReel content creation pipeline.

Usage:
    python script_generator.py                           # Interactive mode
    python script_generator.py --count 5 --hook problem  # Generate 5 scripts
    python script_generator.py --topic "video marketing" --count 3

Output: swipe_files/generated_<timestamp>.json (compatible with factory3.py)
"""

import os
import json
import time
import random
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Product Identity ───────────────────────────────────────────────
# Edit these or set via .env to match your SaaS
SAAS_NAME = os.getenv("SAAS_NAME", "ContentReel")
SAAS_URL = os.getenv("SAAS_URL", "")
SAAS_TAGLINE = "AI-Powered Content Creation — Post 5x a Day Without the Grind"

PRODUCT_DESCRIPTION = f"""
{SAAS_NAME} is an AI-powered content automation platform. It lets solopreneurs,
creators, and busy professionals create professional short-form videos at scale.

What it does:
- AI talking avatar delivers your script naturally (no face recording needed)
- Auto-adds relevant b-roll footage to keep viewers engaged
- Generates animated captions with word-by-word highlighting
- Produces platform-optimized video formats (Instagram, YouTube Shorts, TikTok)

Target users: Solopreneurs, creators, founders who need consistent content but don't
have time for production. People who know they should post 5x a day but can't.

Value props:
- From script to finished video in ~15 minutes
- No filming, no editing skills, no production anxiety
- Professional quality without hiring a video editor
- Consistent posting = algorithm loves you
"""

# ─── Hook Templates ─────────────────────────────────────────────────
HOOK_TEMPLATES = {
    "problem": [
        "You're spending {hours} hours editing one video. Stop.",
        "Here's why your content isn't growing {audience}.",
        "The real reason you're not posting daily isn't lack of time.",
        "Stop doing this if you want to grow on {platform}.",
        "Most creators waste {hours} hours a week on production.",
        "You don't need to be a video editor to grow on {platform}.",
        "This is why your {platform} content isn't converting.",
    ],
    "curiosity": [
        "What if you could post 5 videos/day and never touch a camera?",
        "The tool that made this video is about to save you {hours} hours/week.",
        "I made this video in 15 minutes. Here's how.",
        "This video was made by AI. Can you tell?",
        "The secret to posting daily without burning out.",
        "How I went from 0 to consistent content without showing my face.",
        "This is the easiest way to create content in 2025.",
    ],
    "result": [
        "I grew my {audience} by {percent}% posting {count}x a day.",
        "{count} videos in {days} days. Here's exactly what happened.",
        "I automated my content and gained {count} {audience} in {days} days.",
        "How I post {count}x a day and still have time for my business.",
        "From zero to {count} {platform} subscribers in {days} days.",
    ],
    "comparison": [
        "Professional video production vs a {price}/video AI tool.",
        "Most creators spend ${price_month}/mo on production. I spend ${price_tool}.",
        "The old way: {hours} hours editing. The new way: {minutes} minutes.",
        "Video editors charge ${price_edit}/video. AI does it for {price_tool}.",
        "What if your competitor is posting 5x a day and you're posting once a week?",
    ],
    "direct": [
        "You. Yeah you. The one who keeps saying 'I'll start posting next week.'",
        "If you've been putting off content creation, watch this.",
        "This is your sign to automate your content creation.",
        "You have something valuable to say. Here's how to say it without anxiety.",
        "Stop overthinking. Here's the system.",
    ],
}

# ─── Call-to-Action Templates ───────────────────────────────────────
CTA_TEMPLATES = {
    "soft": [
        f"Try {SAAS_NAME} and see how easy content can be.",
        f"{SAAS_NAME} turns your ideas into videos. No fuss.",
        f"Stop grinding. Start creating. With {SAAS_NAME}.",
        f"{SAAS_NAME}. Content creation, automated.",
    ],
    "hard": [
        f"Sign up for {SAAS_NAME} today and get your first videos free.",
        f"Stop wasting time editing. Join {SAAS_NAME} and automate your content.",
        f"Ready to post 5x a day? {SAAS_NAME} makes it possible. Link in bio.",
        f"This video was made with {SAAS_NAME}. You can do it too. Sign up free.",
        f"Don't let content creation hold you back. Try {SAAS_NAME}.",
    ],
    "proof": [
        f"This entire video was created with {SAAS_NAME}. No camera, no editor.",
        f"See that avatar? That script? Those captions? All {SAAS_NAME}.",
        f"What you just watched took 15 minutes and {SAAS_NAME}.",
        f"If you're wondering how this video was made — it's {SAAS_NAME}.",
    ],
}

# ─── Body Templates (video structure) ───────────────────────────────
BODY_STRUCTURES = {
    "problem-solution": {
        "structure": [
            ("hook", "Grab attention with a pain point"),
            ("problem", "Describe the struggle (time, consistency, quality)"),
            ("solution", "Introduce how the tool solves it"),
            ("demo", "Briefly explain how it works (script → avatar → b-roll → captions)"),
            ("social-proof", "Results other users have seen"),
            ("cta", "Call to action"),
        ],
        "description": "Pain point → solution flow. Best for cold audience.",
    },
    "story": {
        "structure": [
            ("hook", "Curiosity or result hook"),
            ("before", "What life was like before the tool (struggling to post)"),
            ("after", "How everything changed after automating"),
            ("how", "Briefly how it works (the system)"),
            ("cta", "Call to action with proof"),
        ],
        "description": "Before/after narrative. Best for relatable storytelling.",
    },
    "feature-spotlight": {
        "structure": [
            ("hook", "Direct or curiosity hook"),
            ("feature", "One specific feature (AI avatar, b-rolls, captions)"),
            ("benefit", "Why this matters for the viewer"),
            ("demo", "Show it in action"),
            ("cta", "Call to action"),
        ],
        "description": "Deep dive on one feature. Best for product awareness.",
    },
    "comparison": {
        "structure": [
            ("hook", "Comparison hook"),
            ("old-way", "The expensive/time-consuming approach"),
            ("new-way", "How the tool makes it easy and cheap"),
            ("proof", "Results side by side"),
            ("cta", "Call to action"),
        ],
        "description": "Before/after comparison. Best for value demonstration.",
    },
}

# ─── Provider Functions ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert short-form video scriptwriter specializing in SaaS marketing. Your scripts drive conversions by making the viewer feel the pain of NOT using the product, then showing a clear path to relief.

RULES:
1. Each script must be 45-90 seconds of spoken content (~110-220 words)
2. Every script STARTS with a hook that grabs attention in the first 3 seconds
3. Every script ENDS with a clear CTA (call to action)
4. Use natural, conversational language — no corporate jargon
5. Read the script aloud mentally — it should flow naturally
6. Focus on BENEFITS not features (e.g. "save 4 hours a week" not "has an AI pipeline")
7. Use social proof, specificity, and pain points
8. Never say "um", "like", "you know" — but DO use contractions and natural phrasing
9. The avatar speaks in first person or directly to the viewer ("you")
10. Make the viewer feel like they're missing out if they don't use the tool"""


def build_generation_prompt(
    hook_style="problem",
    body_style="problem-solution",
    cta_style="hard",
    niche="content creation",
    audience="solopreneurs and creators",
    platform="social media",
    saas_name=SAAS_NAME,
):
    """Build a prompt for script generation with specific parameters."""

    hook_examples = random.sample(HOOK_TEMPLATES.get(hook_style, HOOK_TEMPLATES["problem"]), min(3, len(HOOK_TEMPLATES[hook_style])))
    cta_examples = random.sample(CTA_TEMPLATES.get(cta_style, CTA_TEMPLATES["hard"]), min(2, len(CTA_TEMPLATES[cta_style])))
    body_info = BODY_STRUCTURES.get(body_style, BODY_STRUCTURES["problem-solution"])

    prompt = f"""Generate ONE short-form video script for {saas_name}, a SaaS platform that automates AI avatar video creation.

TARGET AUDIENCE: {audience}
PLATFORM: {platform}
NICHE: {niche}
TONE: Conversational, direct, slightly urgent but not pushy

HOOK STYLE: {hook_style.title()}
Use hooks like:
{chr(10).join(f'  • "{h}"' for h in hook_examples)}

BODY STRUCTURE: {body_style} ({body_info['description']})
Sections (in order):
{chr(10).join(f'  • {label}' for label, desc in body_info['structure'])}

CTA STYLE: {cta_style.title()}
End with a CTA like:
{chr(10).join(f'  • "{c}"' for c in cta_examples)}

OUTPUT FORMAT (JSON ONLY — no other text):
{{"id": 1, "script": "Full script text here...", "niche": "{niche}", "hook_style": "{hook_style}", "body_style": "{body_style}", "hook": "The hook sentence only", "cta": "The CTA sentence only"}}

The script must be 110-220 words. Start with the hook, build the body, end with the CTA. Make it sound like a real person talking, not a marketing brochure."""

    return prompt


def get_api_key(key_name):
    """Get API key from environment (loaded via dotenv from .env).
    
    Returns the key if non-empty, otherwise empty string.
    """
    from dotenv import dotenv_values
    # First check system environment (most reliable in shell sessions)
    val = os.environ.get(key_name, "")
    if val:
        return val
    # Fallback: directly read from .env file (handles venv isolation edge cases)
    env_vals = dotenv_values()
    return env_vals.get(key_name, "")


def generate_scripts_openai(
    count=1,
    hook_style="problem",
    body_style="problem-solution",
    cta_style="hard",
    niche="content creation",
    audience="solopreneurs and creators",
    platform="social media",
):
    """Generate scripts using OpenAI API."""
    from openai import OpenAI

    api_key = get_api_key("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set in .env or environment")
        return []

    client = OpenAI(api_key=api_key)
    scripts = []

    for i in range(count):
        # Vary hook style if generating multiple
        actual_hook = hook_style
        if count > 1 and hook_style == "auto":
            actual_hook = random.choice(list(HOOK_TEMPLATES.keys()))

        actual_body = body_style
        if count > 1 and body_style == "auto":
            actual_body = random.choice(list(BODY_STRUCTURES.keys()))

        prompt = build_generation_prompt(
            hook_style=actual_hook,
            body_style=actual_body,
            cta_style=cta_style,
            niche=niche,
            audience=audience,
            platform=platform,
        )

        print(f"  [{i+1}/{count}] Generating {actual_hook} hook / {actual_body} body...")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=600,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            script_data = json.loads(content)

            script_data["id"] = i + 1
            scripts.append(script_data)

            # Rate limit buffer
            time.sleep(1)

        except Exception as e:
            print(f"  Error generating script {i+1}: {e}")
            continue

    return scripts


def generate_scripts_anthropic(
    count=1,
    hook_style="problem",
    body_style="problem-solution",
    cta_style="hard",
    niche="content creation",
    audience="solopreneurs and creators",
    platform="social media",
):
    """Generate scripts using Anthropic API."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        return []

    api_key = get_api_key("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set in .env or environment")
        return []

    client = anthropic.Anthropic(api_key=api_key)
    scripts = []

    for i in range(count):
        actual_hook = hook_style
        if count > 1 and hook_style == "auto":
            actual_hook = random.choice(list(HOOK_TEMPLATES.keys()))

        actual_body = body_style
        if count > 1 and body_style == "auto":
            actual_body = random.choice(list(BODY_STRUCTURES.keys()))

        prompt = build_generation_prompt(
            hook_style=actual_hook,
            body_style=actual_body,
            cta_style=cta_style,
            niche=niche,
            audience=audience,
            platform=platform,
        )

        print(f"  [{i+1}/{count}] Generating {actual_hook} hook / {actual_body} body...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                temperature=0.8,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                script_data = json.loads(json_match.group())
                script_data["id"] = i + 1
                scripts.append(script_data)

            time.sleep(0.5)

        except Exception as e:
            print(f"  Error generating script {i+1}: {e}")
            continue

    return scripts


def generate_scripts_deepseek(
    count=1,
    hook_style="problem",
    body_style="problem-solution",
    cta_style="hard",
    niche="content creation",
    audience="solopreneurs and creators",
    platform="social media",
    model="deepseek-chat",
):
    """Generate scripts using DeepSeek API (OpenAI-compatible)."""
    from openai import OpenAI

    api_key = get_api_key("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set in .env or environment")
        return []

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    scripts = []

    for i in range(count):
        actual_hook = hook_style
        if count > 1 and hook_style == "auto":
            actual_hook = random.choice(list(HOOK_TEMPLATES.keys()))

        actual_body = body_style
        if count > 1 and body_style == "auto":
            actual_body = random.choice(list(BODY_STRUCTURES.keys()))

        prompt = build_generation_prompt(
            hook_style=actual_hook,
            body_style=actual_body,
            cta_style=cta_style,
            niche=niche,
            audience=audience,
            platform=platform,
        )

        print(f"  [{i+1}/{count}] Generating {actual_hook} hook / {actual_body} body (DeepSeek)...")

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=600,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            script_data = json.loads(content)

            script_data["id"] = i + 1
            scripts.append(script_data)

            # Rate limit buffer
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error generating script {i+1}: {e}")
            continue

    return scripts


def save_scripts(scripts, output_dir="swipe_files"):
    """Save generated scripts to a JSON file in swipe_files/."""
    if not scripts:
        print("No scripts to save.")
        return None

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/generated_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(scripts, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Saved {len(scripts)} scripts to {filename}")
    print(f"   Run: python factory3.py {filename}")
    return filename


def show_info():
    """Display available templates and styles."""
    print(f"\n{'='*60}")
    print(f"  {SAAS_NAME} — AI Script Generator")
    print(f"{'='*60}")
    print(f"\nProduct: {SAAS_TAGLINE}")
    print(f"\nAvailable Hook Styles:")
    for name, examples in HOOK_TEMPLATES.items():
        print(f"  {name:15s} e.g. \"{examples[0]}\"")
    print(f"\nAvailable Body Structures:")
    for name, info in BODY_STRUCTURES.items():
        print(f"  {name:20s} {info['description']}")
    print(f"\nAvailable CTA Styles:")
    for name, examples in CTA_TEMPLATES.items():
        print(f"  {name:15s} e.g. \"{examples[0]}\"")
    print()


def main():
    saas_name = os.getenv("SAAS_NAME", "ContentReel")
    parser = argparse.ArgumentParser(
        description=f"{saas_name} Script Generator — AI-powered, conversion-optimized video scripts"
    )
    parser.add_argument("--count", "-c", type=int, default=5,
                        help="Number of scripts to generate (default: 5)")
    parser.add_argument("--hook", "-k", type=str, default="auto",
                        choices=["auto"] + list(HOOK_TEMPLATES.keys()),
                        help="Hook style (default: auto — mixes styles)")
    parser.add_argument("--body", "-b", type=str, default="auto",
                        choices=["auto"] + list(BODY_STRUCTURES.keys()),
                        help="Body structure (default: auto — mixes styles)")
    parser.add_argument("--cta", type=str, default="hard",
                        choices=list(CTA_TEMPLATES.keys()),
                        help="CTA style (default: hard)")
    parser.add_argument("--niche", "-n", type=str, default="content automation",
                        help="Content niche/topic (default: content automation)")
    parser.add_argument("--audience", "-a", type=str, default="solopreneurs and creators",
                        help="Target audience description")
    parser.add_argument("--platform", "-p", type=str, default="social media",
                        help="Target platform (social media, YouTube, LinkedIn, X/Twitter)")
    parser.add_argument("--provider", type=str, default="deepseek",
                        choices=["deepseek", "openai", "anthropic"],
                        help="AI provider (default: deepseek)")
    parser.add_argument("--model", type=str, default="deepseek-chat",
                        help="Model name (default: deepseek-chat)")
    parser.add_argument("--info", action="store_true",
                        help="Show available templates and exit")
    parser.add_argument("--name", type=str,
                        help=f"Override SaaS name (default: {saas_name})")
    parser.add_argument("--output", "-o", type=str, default="swipe_files",
                        help="Output directory (default: swipe_files)")

    args = parser.parse_args()

    if args.info:
        show_info()
        return

    # Override SaaS name if provided
    if args.name:
        saas_name = args.name

    print(f"\n{'='*60}")
    print(f"  {saas_name} Script Generator")
    print(f"  Generating {args.count} scripts")
    print(f"  Niche: {args.niche}")
    print(f"  Audience: {args.audience}")
    print(f"  Platform: {args.platform}")
    print(f"  Provider: {args.provider}")
    print(f"{'='*60}\n")

    if args.provider == "deepseek":
        scripts = generate_scripts_deepseek(
            count=args.count,
            hook_style=args.hook,
            body_style=args.body,
            cta_style=args.cta,
            niche=args.niche,
            audience=args.audience,
            platform=args.platform,
            model=args.model,
        )
    elif args.provider == "openai":
        scripts = generate_scripts_openai(
            count=args.count,
            hook_style=args.hook,
            body_style=args.body,
            cta_style=args.cta,
            niche=args.niche,
            audience=args.audience,
            platform=args.platform,
        )
    else:
        scripts = generate_scripts_anthropic(
            count=args.count,
            hook_style=args.hook,
            body_style=args.body,
            cta_style=args.cta,
            niche=args.niche,
            audience=args.audience,
            platform=args.platform,
        )

    if scripts:
        save_scripts(scripts, args.output)
        # Show preview
        print(f"\n📋 Preview:")
        print(f"  {'─'*58}")
        for s in scripts[:3]:
            preview = s.get("script", "")[:80] + "..." if len(s.get("script", "")) > 80 else s.get("script", "")
            print(f"  [{s.get('id')}] {s.get('hook_style', '?')} / {s.get('body_style', '?')}")
            print(f"      \"{preview}\"")
            print(f"  {'─'*58}")
        if len(scripts) > 3:
            print(f"  ...and {len(scripts) - 3} more")
    else:
        print("\n❌ No scripts were generated. Check your API key.")


if __name__ == "__main__":
    main()
