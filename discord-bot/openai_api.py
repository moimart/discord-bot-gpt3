from Prompts import language_map
from Errors import *
from config import OPENAI_TOKEN
import aiohttp
import re


def handle_status(status_code):
    if status_code == 429:
        raise TokenExhaustedError
    elif status_code == 400:
        raise TokenInvalidError
    elif status_code == 500:
        raise OpenAIError


# TODO: Remove the need
def serialize_answer(char_list):
    out = ""
    for i in char_list:
        out += i
    return out


# TODO: Fix this monstrosity
def prep_sentiment(results):
    [r.pop("object", None) for r in results]
    scores = [(r["document"], r["score"]) for r in results]
    res = {}
    for score in scores:
        if score[0] == 0:
            res["Pozitif"] = score[1]
        if score[0] == 1:
            res["Negatif"] = score[1]
        if score[0] == 2:
            res["Nötr"] = score[1]
    ns = []
    for k in res.keys():
        ns.append(res[k])
    for k in res.keys():
        if res[k] == max(ns):
            res[k] = str(res[k]) + " ✅"
        else:
            res[k] = str(res[k]) + " :x:"
    out = """
    Sentiment:
    Positive: {}
    Negative: {}
    Neutral: {}
    """.format(res["Pozitif"], res["Negatif"], res["Nötr"])
    return out


class ApiHandler:
    def __init__(self, logger):
        self.__logger = logger
        self.__api_key = OPENAI_TOKEN

    async def complete(self, prompt, language="EN"):
        try:
            cue = " ".join(str(x) for x in prompt)
            prompt = language_map[language]["complete"].format(cue)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": prompt,
                "max_tokens": 100,
                "temperature": 0.8,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "stop": ["###", "\n\n\n"],
                "echo": False
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        out = text['choices'][0]['text']
                        return cue + out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Completion failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def generate(self, question, language="EN"):
        try:
            question = " ".join(str(x) for x in question)
            prompt = question
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                'completions': 1,
                'context': prompt,
                'length': 64,
                'temperature': 0.8,
                'top_p': 1,
                'frequency_penalty': 0,
                'presence_penalty': 0,
                "stream": False,
                'best_of': 2,
                "stop": ["###", "\n\n\n"]
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/generate', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        out = serialize_answer(text['data'][0]['text'])
                        return out.strip()
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Answer failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def answer(self, question, language="EN"):
        try:
            question = " ".join(str(x) for x in question)
            prompt = language_map[language]["answer"].format(question)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                'completions': 1,
                'context': prompt,
                'length': 100,
                'temperature': 0.6,
                'top_p': 1,
                'frequency_penalty': 0,
                'presence_penalty': 0,
                "stream": False,
                'best_of': 1,
                "stop": ["###", "Question:"]
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/generate', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        out = serialize_answer(text['data'][0]['text'])
                        answer = out.split(prompt)[-1].strip()
                        result = "{}".format(answer)
                        return answer
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Answer failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def song(self, song_name, language="EN"):
        try:
            song_name = " ".join(str(x) for x in song_name)
            prompt = language_map[language]["song"].format(song_name, user_name)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": prompt,
                "max_tokens": 120,
                "temperature": 0.5,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        out = prompt + text
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Sing failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def ad(self, prompt, language="EN"):
        try:
            items = " ".join(str(x) for x in prompt).split(";")
            scaffold = language_map[language]["ad"].format(items[1],items[0])

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 64,
                "temperature": 0.5,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "frequency_penalty": 0,
                "presence_penalty":0,
                'stop': '""""""'
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci-instruct-beta/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = language_map[language]["ad_out"].format(text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Ad failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    def parse_products(self, product_string):
        text = re.split(",+",product_string)
        text[0] = text[0].split("Product names:")[1]
        striped_names = []
        for x in text:
            striped_names.append(x.strip())
        names = list(set(striped_names))
        names = ", ".join(str(x) for x in names)
        return "Product names: {}".format(names)

    async def product(self, prompt, language="EN"):
        try:
            items = " ".join(str(x) for x in prompt).split(";")
            scaffold = language_map[language]["product"].format(items[0],items[1])
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 60,
                "temperature": 0.5,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "frequency_penalty": 0,
                "presence_penalty":0,
                'stop': '\n'
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = language_map[language]["product_out"].format(text)
                        return self.parse_products(result)
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Product names failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def recipe(self, prompt, language="EN"):
        try:
            items = " ".join(str(x) for x in prompt).split(";")
            scaffold = language_map[language]["recipe"].format(items[0],items[1])

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 120,
                "temperature": 0,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "frequency_penalty": 0,
                "presence_penalty":0,
                'stop': 'Ingredients:'
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci-instruct-beta/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = language_map[language]["recipe_out"].format(items[0],text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Recipes names failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def personality(self, prompt, person, language="EN", stops=[]):
        try:
            item = " ".join(str(x) for x in prompt)
            scaffold = language_map[language][person].format(item)
            real_stops = [ '###', '\n\n', 'Interviewer:' ] + stops

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 120,
                "temperature": 0.8,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "frequency_penalty": 0,
                "presence_penalty":0,
                'stop': real_stops
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci-instruct-beta/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = "{}".format(text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("{} failed with error: {}".format(person, e))
            return "Something went wrong: {} Robots too have problems...".format(e)

    async def tldr(self, prompt, language="EN"):
        try:
            item = " ".join(str(x) for x in prompt)
            scaffold = language_map[language]["tldr"].format(item)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 60,
                "temperature": 0.3,
                "top_p": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "frequency_penalty": 0,
                "presence_penalty":0,
                'stop': '\n\n'
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = "{}".format(text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("TLDR failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def headline(self, prompt, language="EN"):
        try:
            topics = ", ".join(str(x) for x in prompt)
            scaffold = language_map[language]["headline"].format(topics)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                'stop': '\n'
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = language_map[language]["headline_out"].format(text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Headline failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def sentiment(self, prompt, language="EN"):
        try:
            prompt = " ".join(str(x) for x in prompt)
            data = {"documents": language_map[language]["sentiment"],
                    "query": "{}.".format(prompt)}
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/search', headers=headers,
                                        json=data) as r:
                    if r.status == 200:
                        results = await r.json()
                        results = results["data"]
                        out = prep_sentiment(results)
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Sentiment failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def emojify(self, prompt, language="EN"):
        try:
            topics = " ".join(str(x) for x in prompt)
            scaffold = language_map[language]["emojify"].format(topics)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 1,
                "n": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "stop": "\n"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = """{}: {}""".format(topics, text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Emojify failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def sarcastic_answer(self, prompt, language="EN"):
        try:
            q = " ".join(str(x) for x in prompt)
            scaffold = language_map[language]["sarcasm"].format(q)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 64,
                "temperature": 0.6,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stop": "\n"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        out = "Q: {} \n A: {}".format(q, text)
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Sarcasm failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def foulmouth_answer(self, prompt, language="EN"):
        try:
            q = " ".join(str(x) for x in prompt)
            scaffold = language_map[language]["foulmouth"].format(q)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__api_key
            }
            params = {
                "prompt": scaffold,
                "max_tokens": 60,
                "temperature": 0.1,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "logprobs": None,
                "echo": False,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stop": "\n"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        out = "Q: {} \n A: {}".format(q, text)
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Foulmouth failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."
