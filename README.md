# Post 5x a day on Instagram/Youtube/Tiktok by automating content creation 🚀

I made a Reddit post explaining why I did this and how it helped me as a solopreneur who's struggling to stay consistent with content creation → (LINK TO BE ADDED)  

Demo video: [Youtube](https://youtube.com/shorts/nJI9Lmy-y7k)

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

## Work with me 👋

You are free to use my tool to create videos. If you'd would like to work with me, here's my offer:

1. 30 videos for USD1,000
2. 1 free video demo
3. Reach out to me/understand more:- 
- [Calendly - book a call]()
- [X]()