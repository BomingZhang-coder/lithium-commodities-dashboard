## Lithium Price

#### Data
2 main Lithium price series
Lithium Carbonate (Li2CO3): https://github.com/globalaiorg/NLP-LITHIUM-COMMODITIES/blob/main/jerry/lithium_dataset/Lithium%20Carbonate%20(wind%20database).csv 
Lithium Hydroxide (LiOH): https://github.com/globalaiorg/NLP-LITHIUM-COMMODITIES/blob/main/jerry/lithium_dataset/Lithium%20Hydroxide%20(wind%20database).csv 

#### Unsmoothing Methods
Due to illiquidity of Lithium price, we need to do Unsmoothing Process with AR & MA model
Instructions:  https://drive.google.com/drive/u/1/folders/1M7Fzb_CyFdeqfdZdKF1Rl3LTATyabs9O 

#### Regression 
After unsmoothing or recovering true series, doing the Regression Analysis with mining companies
instructions: https://docs.google.com/document/u/1/d/1YAz7q6jrPTlZOP45TCrM2-oySiO1JckQ/edit?usp=drive_web&ouid=109765196100323927209&rtpof=true 
code
Task2: https://github.com/globalaiorg/NLP-LITHIUM-COMMODITIES/blob/main/birdy/Li2CO3-Task2-time-series-regression.ipynb 
Task3: https://github.com/globalaiorg/NLP-LITHIUM-COMMODITIES/blob/main/birdy/Task3_LiOH_time-series-regression.ipynb 

#### News Data
News Feature Creation with Gdelt Dataset: 
the most updated code: https://drive.google.com/drive/u/1/folders/1vpOS17rPoQ_ncd0Evp5LEtYXDLdlbFO9 
**how to run this code:** 
before running, open get_raw_data.py, set the `end date` and `start date` and period for each record.
open terminal and run python get_raw_data.py. 
more detail, please contact me. 


#### Other Features 
Google Trend: 
https://drive.google.com/drive/u/1/folders/1hctRupe-OCfhroj8I6rONre2swHBCWNj 
website to create this data on your own: https://trends.google.com/trends/explore?date=now%201-d&q=lithium,EV&hl=en 

#### Papers on Models I am reading: 
https://drive.google.com/drive/u/1/folders/1CjgIyBTEmBvg-YeYdZGLPK0rXqUVtVjt 


