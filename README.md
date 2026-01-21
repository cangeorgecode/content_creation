# Post 5x a day on Instagram/Youtube/Tiktok by automating content creation 🚀

I made a Reddit post explaining why I did this and how it helped me as a solopreneur who's struggling to stay consistent with content creation → (LINK TO BE ADDED)  

## Demo

<video src="https://raw.githubusercontent.com/cangeorgecode/content_creation/main/docs/demo.mp4" controls width="640"></video>

Or direct link [Youtube](https://youtube.com/shorts/nJI9Lmy-y7k)

&nbsp;

## Prerequisites 👷 

This program relies on Heygen API. Unfortunately, I can't find a free alternatives to animate a picture.  

Sign up here → [Heygen, not affiliated](https://heygen.com/)  

Obtain the api key and put it in the .env file 

### .env  
Create a .env file and input the heygen api key:  

```
HEYGEN_API_KEY=''
```  

### Assets 📽️
After installation, you will need to add the following assets. Create the folders with the exact name:

1. Create a 'brolls' folder. This is where you put your b-rolls
2. Create a 'media' folder. This will be needed by the program
3. Create an 'output' folder. This is where the finished clip goes
4. Create a 'swipe_files' folder. This is where the speech goes (Please follow the sample speech json format below)  

You can create all required folders with this command:

```
mkdir -p brolls media output swipe_files
```

### Speech 💬
Sample speech in json format:

```json
[
    {
        "id": 1,
        "script": "Bear facts you didn't know part 1. Fact 1, Black bears are not always black. They can be cinnamon, blonde, blue-gray, or even white. This is a strategic color variation for thriving in diverse biomes. It is not for fashion. Fact 2, A bear's sense of smell is approximately 2,100 times better than a human's. They can detect a carcass from 20 miles away. This makes them nature's most efficient sanitation crew. Fact 3, During hibernation, a bear does not defecate. Their body forms a fecal plug. It is a logical, waste-not-want-not system."
    }
]
```

&nbsp;

## Installation 🏗️
1. Activate virtual environment (I am running WSL2 on Windows 11, so I will use Linux commands)  
```
python3 -m venv venv
source venv/bin/activate
```

2. Clone this repo  
```
git clone 
```

3. Install requirements.txt
```
pip install -r requirements.txt
```  

4. You might need chromium
Pycaps might require chromium to be installed, but you can do this easily by following the instructions on [Pycaps Repo](https://github.com/francozanardi/pycaps)

&nbsp;

## How to use it  

Run:
```
python factory3.py swipe_files/bear_facts.json
```

If it runs successfully, your finished video will be inside the 'output' folder

&nbsp;

## Services for Non-Technical Founders & Creators 👋

You are free to use and modify this tool. However, if you don't code and just want the **output**, I can be your production engine.

**Let's be 100% clear about what I offer:**

**I solve one problem: The Time vs. Output Problem.**
- **I do NOT guarantee** that these videos will make you go viral, grow your followers, or improve your brand.
- **I do NOT provide** marketing strategy, audience analysis, or content coaching.
- **I am NOT** a social media expert.

**What I AM is a technical builder who automated his own video grind.**
- **I DO guarantee** that I can turn your topics/scripts into consistent, AI-presented short-form videos **at scale**.
- **I DO provide** a reliable system that removes filming, editing, and production headaches.
- **I AM the guy** you hire when you need to **post 5 times a day without it taking over your life.**

Think of me as your **Short-Form Video Factory**. You provide the raw material (ideas), I handle the manufacturing (production).

---

### **Managed Production Package**

**For $1,000 USD, you will receive 30 completed short-form videos.** This includes:

1.  **Input & Requirements (What You Provide):**
    *   **Topics/Scripts:** You can provide your own scripts, or I can generate them for you using AI based on your topics.
    *   **B-Roll Clips:** You provide the B-roll video clips you want featured. (This ensures the content matches your brand/style).
    *   **Avatar (Optional):** For a personalized AI avatar, you can provide 4-5 clear selfies. If not, I'll use a default avatar.

2.  **Production & Delivery (What I Do):**
    *   **1 Free Sample Video:** So you can approve the style, avatar, and quality with zero risk.
    *   **Full Production:** Script-to-final-video for 30 clips (AI avatar, your B-rolls, captions, platform-ready formatting).
    *   **Pure Output:** Consistent, ready-to-post content delivered on schedule.

**This is for you if:** You believe in the "law of volume" and just need the content created, or you're testing a content channel and need bulk material fast.

**This is NOT for you if:** You're looking for a marketing partner to strategize your viral growth or need me to source custom B-roll footage.

---

### **Next Steps**

If you need **volume** and want to **outsource the production grind**, let's talk.
- **Book a quick 10-min clarity call:** [Calendly Link](https://calendly.com/georgedjangodev/content-creation-talk)
- **Follow my build-in-public journey:** [X / Twitter](https://x.com/georgedevz)