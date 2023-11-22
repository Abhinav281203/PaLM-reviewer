import asyncio
from pyppeteer import launch
import google.generativeai as gen_ai


async def fetch_reviews(url):
    fetched_reviews = []

    browser = await launch({"headless": True, "args": ["--window-size=800,3000"]})
    page = await browser.newPage()

    await page.setViewport({"width": 800, "height": 3000})
    await page.goto(url)
    await page.waitForSelector(".jftiEf")

    reviews = await page.querySelectorAll(".jftiEf")

    for review in reviews:
        try:
            await page.waitForSelector(".w8nwRe")
            more = await review.querySelector(".w8nwRe")
            await page.evaluate("button => button.click()", more)
            await page.waitFor(5000)
        except:
            pass

        await page.waitForSelector(".MyEned")
        snippet = await review.querySelector(".MyEned")
        text = await page.evaluate("selected => selected.textContent", snippet)
        fetched_reviews.append(text)

    await browser.close()
    return fetched_reviews


def generate_summary(reviews, text_model):
    prompt = """Here are some reviews of a place I want to visit. 
    Breifly summarize the reviews for me. I want to know what people 
    like and dislike, and some speciality of the place. The reviews are:\n"""

    for i in range(len(reviews)):
        prompt += f"\n{i+1}. " + reviews[i]
    # print(prompt)

    completion = gen_ai.generate_text(
        model=text_model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=500,
    )

    return completion.result


if __name__ == "__main__":
    gen_ai.configure(api_key="PaLM_API_KEY")
    available_models = [
        model for model in gen_ai.list_models() if "generateText" in model.supported_generation_methods
    ]
    selected_model = available_models[0].name  # "models/text-bison-001"
    while 1:
        try:
            ip = input(
                "Enter the URL(Google Maps) of the place or type 'exit' to exit:\n"
            )
            if ip == "exit":
                break
            reviews = asyncio.get_event_loop().run_until_complete(fetch_reviews(ip))
            result = generate_summary(reviews, selected_model)
            print(result)
        except:
            pass
