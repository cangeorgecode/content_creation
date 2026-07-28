# ContentReel — AI Avatar Content Automation 🚀

**Automated content creation platform. Post 5x a day on Instagram, YouTube, TikTok, LinkedIn, and X.**

The content this tool creates IS the marketing for the tool. The AI avatar talks about how ContentReel automates content creation — so every video is a living demo that funnels viewers into subscribers.

Built on the [original content_creation](https://github.com/cangeorgecode/content_creation) pipeline by cangeorgecode.

## How It Works

```
Script → HeyGen Avatar Video → B-Rolls → Captions → Multi-Platform Export
  ↑
AI Script Generator (with hooks + CTAs)
```

The pipeline has 4 stages:
1. **Script Generation** (optional) — AI writes conversion-optimized scripts with hooks and CTAs
2. **HeyGen Avatar** — AI avatar delivers your script (costs HeyGen credits)
3. **B-Rolls** — Random b-rolls fill the middle 77% of the video
4. **Captions** — Animated word-by-word captions via PyCaps
5. **Multi-Platform** (optional) — Export to YouTube (16:9), LinkedIn (1:1), X (16:9)

## Prerequisites 👷

- **HeyGen API Key** — Required for avatar video generation. [Sign up here](https://heygen.com/)
- **OpenAI API Key** — Required for AI script generation (can also use Anthropic)
- **B-Roll Footage** — Put `.mp4` clips in the `brolls/` folder

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install openai anthropic  # for AI script generation
mkdir -p brolls media output swipe_files
```

### .env

```env
HEYGEN_API_KEY='your_key_here'
OPENAI_API_KEY='your_key_here'
SAAS_NAME='ContentReel'
```

## Usage

### Quick Start (Generate + Process)

```bash
# Generate 5 scripts and process them all at once
python factory3.py --generate 5

# Generate 10 scripts with curiosity hooks
python factory3.py --generate 10 --hook curiosity --niche "content marketing"

# Use Anthropic instead of OpenAI
python factory3.py --generate 5 --provider anthropic
```

### Process Existing Scripts

```bash
python factory3.py swipe_files/demo_contentreel.json
```

### Multi-Platform Export

After generating your captioned video:

```bash
# Create all platform variants
python platform_formatter.py output/your_video_captioned.mp4 --all

# Or specific platforms
python platform_formatter.py output/your_video_captioned.mp4 --platforms youtube,linkedin,x
```

### Pipeline Management

```bash
# Check what's been done and what failed
python factory3.py --status

# Retry any failed scripts
python factory3.py swipe_files/scripts.json --retry

# Reset a specific script to reprocess it
python factory3.py --reset 5

# Setup check (creates folders, verifies b-rolls)
python factory3.py --setup
```

## AI Script Generator

The script generator creates conversion-optimized scripts using AI. It understands the SaaS product and writes scripts that drive signups.

```bash
# See all available templates
python script_generator.py --info

# Generate scripts with specific styles
python script_generator.py --count 10 --hook curiosity --body story --cta hard
python script_generator.py --count 5 --provider anthropic --niche "video marketing"
```

### Hook Styles
| Style | Description | Example |
|-------|-------------|---------|
| `problem` | Pain point hook | "You're spending 4 hours editing one video. Stop." |
| `curiosity` | Curiosity gap | "What if you could post 5x a day and never touch a camera?" |
| `result` | Results-driven | "I grew my audience 300% posting 5x a day." |
| `comparison` | Before/after | "$500/video production vs $0.05 with AI." |
| `direct` | Direct address | "You. The one who keeps saying 'I'll start next week.'" |

### Body Structures
| Structure | Best For |
|-----------|----------|
| `problem-solution` | Cold audience pain point → solution |
| `story` | Relatable before/after narrative |
| `feature-spotlight` | Deep dive on one feature |
| `comparison` | Value demonstration |

## Script Queue Format

```json
[
    {
        "id": 1,
        "script": "Your video script here... (110-220 words)",
        "niche": "content automation",
        "hook_style": "problem",
        "body_style": "problem-solution",
        "hook": "First attention-grabbing sentence",
        "cta": "Final call-to-action sentence"
    }
]
```

## Pipeline Resilience

The factory tracks every script's progress in `.pipeline_state.json`. If something fails:

1. **HeyGen credits are NOT wasted** — the pipeline won't re-generate an avatar video that already exists
2. **Resume where you left off** — re-run the same command and it skips completed steps
3. **Retry failures** — `python factory3.py scripts.json --retry`

### State Tracking

```
"new"         → Not started
"heygen_done" → Avatar video downloaded (SAVED — won't regenerate)
"broll_done"  → B-rolls added
"completed"   → All steps done, captioned video ready
"failed"      → Something went wrong at a specific step
```

## Voice Options

Default voice is **Chloe - Lifelike** (HeyGen voice). You can override:

```bash
python factory3.py scripts.json --voice 6e4d89218fa24eb3b3fe4faa16a15895
```

Available voices are in `voices.json` (collected from the HeyGen API).

## Architecture

```
content_creation/
├── factory3.py              # Main pipeline orchestrator
├── script_generator.py      # AI script generation with hooks
├── platform_formatter.py    # Multi-platform export tool
├── pipeline_state.py        # State manager for resume/skip
├── heygen6.py               # HeyGen API integration
├── broll2.py                # B-roll overlay system
├── pycaps2.py               # Caption rendering
├── templates/centered/      # PyCaps caption styling
├── brolls/                  # Your b-roll .mp4 clips
├── media/                   # Downloaded HeyGen videos
├── output/                  # Finished videos
└── swipe_files/             # Script queue JSON files
```

## TODO (Upcoming)

- [x] AI Script Generator with hook system
- [x] Pipeline resilience (resume/skip/retry)
- [x] Multi-platform export (YT, LinkedIn, X)
- [ ] ElevenLabs voice integration
- [ ] Custom avatar upload
- [ ] Self-serving SaaS with 2 subscription tiers
- [ ] Web dashboard
- [ ] Stripe billing integration
- [ ] Batch processing dashboard

## License

Original MIT License. Free to use and modify.
