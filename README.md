# Machine Learning for Trading

## Description
The main objective of this project is to research how ML can be applied to financial markets by identifying predictive signals and evaluating their usefulness in trading strategies. The project follows an iterative approach, where each stage builds on the previous one to improve data quality, feature engineering, model performance and strategy evaluation.
Initially, data is sourced from the Argentine stock market, using only instruments selected according to their trading volume.
The resulting platform is intended to provide an Open Source API and Dashboard exposing instrument rankings, trading strategies, portfolio management insights, risk analysis, and other market-related information.

## Project Path
It includes several stages that are developed iteratively. This way, it is possible to obtain an early global view of the project and gain a better understanding of the real scope and challenges to plan the next development steps.
The aim of each iteration is to perform a deeper data analysis, a finer ML model tuning and also apply more advanced ML/DL technologies to get better results.

Below is a summary path to follow to develop the project:

- Develop a client to source data from different providers and store it in a database.
- Evaluate ML models to predict returns based on some indicators over historical data to detect alpha factors.
- Porfolio management and evaluation based on alpha, beta and risk factors obtained from the previous stage.
- Apply **Sentiment Analysis** to convert text to quantitative signals to fit ML models.
- Use **Topic Modeling** to extract topics from news and social media to use them as features in ML models. 
- Generate synthetic training data using **Generative Adversarial Networks** to improve ML model performance.
- Create an API to expose the generated signals and features.
- Create a dashboard to visualize the results.

## Methodology
This project uses the ML4T (ML For Trading) workflow, which basically consists of a structured process to:
- Source, evaluate and combine data for an investing objective.
- Design and tune ML models to extract predictive signals from data.
- Develop and evaluate strategies based on the results.

ML4T is described in detail in [Machine Learning for Algorithmic Trading](https://www.amazon.com/Machine-Learning-Algorithmic-Trading-alternative/dp/1839217715) by **Stefan Jansen**

