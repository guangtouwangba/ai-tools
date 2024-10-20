import json
import re

from dotenv import load_dotenv
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tracers import ConsoleCallbackHandler
from langchain_openai import ChatOpenAI

load_dotenv()

# model = ChatAnthropic(model='claude-3-opus-20240229')
model = ChatOpenAI(model='gpt-4o')


class GeneratorOutputParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        """
        解析文本中的 Markdown JSON 部分。

        Args:
            text (str): 需要解析的文本，假定包含一个 ` ```json ... ``` `代码块.

        Returns:
            dict: 解析后的 JSON 数据（如果找到）。
        """
        # 使用正则表达式提取 ```json ``` 包裹的部分
        regex = r'```json\s*([\s\S]+?)```'

        # Using re.search instead of re.match
        match = re.search(regex, text)

        if not match:
            raise ValueError(f"cannot parse the response {text}")

        # Extracting JSON content from the matched group
        json_content = match.group(1)

        if match:
            try:
                content = json.loads(json_content)
                return content
            except json.JSONDecodeError as e:
                raise ValueError(f"无法解析为有效的 JSON: {e}")
        else:
            raise ValueError("找不到符合 ` ```json ... ``` ` 模式的内容")


def load_prompt(path) -> PromptTemplate:
    with open(path, "r") as f:
        template = f.read()
    return PromptTemplate(input_variables=["DIFFICULTY_LEVEL", "PROGRAMMING_LANGUAGE", "TOPIC"], template=template)


def generate_practice(number, topic, level, language, prompt, outputParser):
    result = []
    for i in range(number):
        # prompt.format(DIFFICULTY_LEVEL=level, PROGRAMMING_LANGUAGE=language, TOPIC=topic)
        chain = prompt | model | outputParser
        current_result = chain.invoke(
            {
                "DIFFICULTY_LEVEL": level,
                "PROGRAMMING_LANGUAGE": language,
                "TOPIC": topic
            },
            config={"callbacks": [ConsoleCallbackHandler()]},
        )
        current_result['level'] = level
        result.append(current_result)
    return result


if __name__ == '__main__':
    prompt = load_prompt("prompt.txt")
    outputParser = GeneratorOutputParser()
    res = generate_practice(50, "inherent", "advanced", "golang", prompt, outputParser)
    with open("result.json", 'w') as f:
        json.dump(res, f, indent=4)
