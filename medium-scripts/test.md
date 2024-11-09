# I used OpenAI’s o1 model to develop a trading strategy. It is DESTROYING the market

Member-only story

# I used OpenAI’s o1 model to develop a trading strategy. It is DESTROYING the market

## It literally took one try. I was shocked.

![Austin Starks](images/da6f02a126dff924957b15d3d07d8551.jpeg)

![DataDrivenInvestor](images/673fbd15cf48bca32f0f83175d8901c3.png)

Austin Starks

Follow

DataDrivenInvestor

--

142

Listen

Share

More

All of my articles are free to read. If you don’t have a Medium subscription, you can still read by clicking this link.

When I first tried the new OpenAI o1 (“strawberry”) model, I wasn’t initially impressed. Unlike traditional large language models where we can expect a response instantly, the new OpenAI models take longer to process and generate responses — a process we might metaphorically call “thinking”. And, it takes forever.

In fact, it took so long that I had to update my application code because I kept hitting timeouts throughout my application. I didn’t know the new norm would be to wait 5 minutes before getting a response.

But this thinking is worth it. Because I created an algorithmic trading strategy that significantly outperforms the market.

And I did it on accident… on my first try. I am shocked.

# How I created an algorithmic trading strategy using an LLM

First, let’s talk about how I created an algorithmic trading strategy using strawberry.

I built my algorithmic trading platform NexusTrade to work with any Large Language Model. While the backend allowes it to work with Gemini, open-source models like Llama, and other LLMs, the frontend only supports OpenAI and Anthropic models right now.

The way it works is a multi-step process.

1. Send Request: The message from the user is sent to the server
2. Classify Request: From a list of prompts, such as the “AI Stock Screener Prompt”, “Create Portfolio Prompt”, and “Analyze Fundamentals” prompt, the model determines the most relevant prompt to process the request
3. Forward to Prompt: Send the message to the most relevant prompt and get a response
4. Post-Process Response: Depending on the prompt, we’ll perform additional actions. For example, with the “AI Stock Screener Prompt” prompt, we’ll generate a SQL query, and we’ll then in the post-process step, we’ll execute the query against the database.

## Here is what makes NexusTrade's Agent Aurora the most powerful financial assistant

### In the age of AI, it's easy to assume that every chatbot is just another ChatGPT clone. But what if I told you there's…

nexustrade.io

When the model interprets the user to want to create trading strategies, it creates a “prompt chain”.

First, we create the outline of the portfolio, including its name, the initial value, and a description of the strategies.

Then, from the description of the strategies, we create an outline of the strategy. This includes a strategy name, an action (“buy” or “sell”), the asset we want to buy, an amount (for example 10% of your buying power or 100 shares), and a description of when we want to perform the action.

Finally, we repeat this process for the conditions, and transform the description into a condition that can be interpreted by the backtesting and live-trading features of NexusTrade.

This process allows us to create portfolios using AI.

Now, before OpenAI’s strawberry models, the AI was highly literal. It would create what you ask, but it wasn’t very good at generating its own ideas. It was the full responsibility of the user to fully articulate what they wanted and iterate on their idea.

Which is why I was shocked when I saw this new model create a HIGHLY profitable trading strategy on its first try.

## Can this Simple Trading Strategy Really 4x Your Returns? 🤔 Find out!

### Synopsis Hey You, When I first shared my trading strategy that consistently beats the market, I was met with a wave of…

nexustrade.io

# The difference “thinking” makes when developing algorithmic trading strategies

To show just how insane this is, I will use the exact same prompts to create two portfolios. The first portfolio will be created by GPT-4. The second portfolio will be created with GPT-o1-mini. There is no difference in the prompts I use to create these portfolios.

## Creating a portfolio with GPT-4

To create a portfolio, I went to the AI Chat and said the following:

1. Me: Create a portfolio called Omni with an initial value of $10,000
2. Aurora: What strategy would you like to implement in your portfolio named “Omni”? For example, you can specify conditions for buying or selling a particular stock or cryptocurrency.
3. Me: I want a SMA crossover strategy on TQQQ. I want a take profit strategy, but no stop losses — I’m bullish on tech long-term and don’t want to be stop lossed out. I also want to space out my buys and not go all-in at once.

On my first try, here’s the portfolio I created with GPT-4.

As we can see, this… isn’t very good. The percent return is much worse than holding SPY, the risk-adjusted returns is much worse, and it made a huge number of trades (which in real-life, has tax implications, further decreasing your actual realized profits).

In contrast, here’s the portfolio I created with the new strawberry model.

## How to use LLMs to help with financial analysis and algorithmic trading

### An algorithm is a cookbook. Synopsis Imagine a world where financial analysis and trading strategies are powered by…

nexustrade.io

## The outstanding portfolio created with GPT-o1

The process of creating this portfolio is literally the exact same. The only difference between these two requests is that I used a stronger model.

The results though are nothing short of outstanding.

This portfolio is so much better that it’s almost unbelievable. This strategy outperforms the market in almost every way imaginable.

1. The percent change is 3x higher than holding SPY, at 268%
2. The sharpe ratio is much higher, at 0.71 compared to 0.51
3. The maximum drawdown is 37%, compared to the drawdown of holding SPY of 34%
4. But, the average drawdown is somehow less, at 4.35%, compared to the average drawdown of holding SPY of nearly 7%

This is… just wow. Not only is it massively more profitable, but it’s somehow less risky? This is amazing.

## Do companies that make more money have higher stock prices years later?

### Can high net income growth guarantee higher stock prices in the future?I recently conducted an intriguing experiment…

nexustrade.io

# Deeper Discussion of these results

After seeing these results for the first time, I was dumbfounded and decided to do a bit of digging – what was this model doing that GPT-4 wasn’t?

I found this critical detail: when generating the selling condition for this strategy, GPT-4 was selling if the positions were up even a little bit at 0.15%.

In contrast, the portfolio created by OpenAI’s strawberry model would sell if the 14 day average price of the stock was up 15% or more.

I imagine the model created by GPT-4 was just selling too early. I made a small adjustment to the portfolio created with GPT-4.

In the end, this portfolio also had outstanding market-beating returns.

Clearly, the o1-mini model had a better understanding of how to create a valid portfolio for my app without the need for iteration. In contrast, the GPT-4 model needed a little bit more help from an expert user. In the end, both portfolios had outstanding market-beating returns.

# Next Steps with this experiment

Right now, these results are purely backtesting results – they show what would’ve happened if we had deployed this portfolio in the past. This is useful, but it’s not enough. We need to see what would happen if we deployed these portfolios right now.

Thus, I’m deploying these strategies live to the market and monitoring how they will perform in the future.

In NexusTrade, deploying an algorithmic trading strategy is literally the click of a button. Over the next few weeks, I’m going to put AI to the test – can it really create profitable trading strategies, or was it just dumb lucky during the backtest.

Only time will tell.

## I used NexusTrade to Identify Fundamentally Strong AI Stocks. They are DEMOLISHING the Market

### No Exaggeration. These 5 stocks are leaving the rest of the market in the dust. 🤔 How can we harness the power of AI…

nexustrade.io

# Concluding Thoughts

AI will revolutionize every industry and finance is no exception. This experiment proves that, at the very least, AI can help augment your trading decisions. It’s too early to conclude that purely AI-generated portfolios are inherently superior, but the mind-blowing thing about this experiment is that these portfolios were generated in just minutes.

This article shows that both language models from OpenAI can create highly profitable algorithmic trading strategies. The o1 model did so without the need for any manual intervention, while the GPT-4 model needed the help of a human expert. In the end, both models have backtesting returns that leaves the S&P500 in the dust.

But these backtest results are not enough. Over the next few weeks, we’ll see the actual efficacy of AI-generated portfolios. I’m excited to see where this technology goes.

Stay tuned for the results — this could be a game-changer for algorithmic trading.

Thank you for reading! By using NexusTrade, you can create your own algorithmic trading strategies using natural language. Want to try it out for yourself? Create a free account on NexusTrade today.

## NexusTrade - AI-Powered Algorithmic Trading Platform

### Learn to conquer the market by deploying no-code algorithmic trading strategies.

nexustrade.io

Follow me: LinkedIn | X (Twitter) | TikTok | Instagram | Newsletter

Listen to me: Spotify | Amazon Music | Apple Podcasts

Visit us at DataDrivenInvestor.com

Subscribe to DDIntel here.

Join our creator ecosystem here.

DDI Official Telegram Channel: https://t.me/+tafUp6ecEys4YjQ1

Follow us on LinkedIn, Twitter, YouTube, and Facebook.