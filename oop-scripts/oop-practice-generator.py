import json
import re

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import BaseOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tracers import ConsoleCallbackHandler
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatAnthropic(model='claude-3-opus-20240229')
# model = ChatOpenAI(model='gpt-4o')


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
                raise ValueError(f"无法解析为有效的 JSON: {json_content}")
        else:
            raise ValueError("找不到符合 ` ```json ... ``` ` 模式的内容")


def load_prompt(path) -> PromptTemplate:
    # with open(path, "r") as f:
    #     template = f.read()

    generator_template = """
    You are an AI assistant tasked with creating structured content for object-oriented programming exercises. Your goal is to generate exercises of varying difficulty levels, complete with questions, answers, and explanations. Follow these instructions carefully to produce high-quality, structured output.

Input variables:
<difficulty_level>
{DIFFICULTY_LEVEL}
</difficulty_level>
This variable specifies the desired difficulty level of the exercise (e.g., beginner, intermediate, advanced).

<programming_language>
{PROGRAMMING_LANGUAGE}
</programming_language>
This variable specifies the programming language for the exercise (e.g., Python, Java, C++).

<topic>
{TOPIC}
</topic>
This variable specifies the object-oriented programming topic for the exercise (e.g., inheritance, polymorphism, encapsulation).

Instructions for generating the exercise:
1. Based on the given difficulty level, programming language, and topic, create a challenging and relevant object-oriented programming exercise.
2. The exercise should be clear, concise, and appropriate for the specified difficulty level.
3. Ensure that the exercise tests the understanding of the given object-oriented programming topic.
4. Include any necessary class definitions, method signatures, or code snippets required for the exercise.

Instructions for generating the answer:
1. Provide a complete and correct solution to the exercise you created.
2. The answer should be in the form of code that solves the problem presented in the exercise.
3. Ensure that the code follows best practices and conventions for the specified programming language.
4. If multiple solutions are possible, provide the most efficient or idiomatic solution.

Instructions for generating the explanation:
1. Write a detailed explanation of the solution you provided.
2. Break down the key concepts and techniques used in the solution.
3. Explain why certain design choices were made and how they relate to object-oriented principles.
4. If applicable, mention any alternative approaches and why the chosen solution is preferred.

Output format:
Generate your response in markdown format with the following structure:

<output_format>
```json
  {{
  "exercise": "The complete text of the exercise question",
  "answer": "The complete code solution to the exercise",
  "explanation": "A detailed explanation of the solution and related concepts, and why do this design cons and props",
  "level": "how hard of  this  exercise,  beginner: a basic practice  intermediate: one part of system, advanced: a complex system oop design e.g kubernetes, google engine",
  }}
```
</output_format>

Ensure that each field contains the appropriate content as described in the instructions above. The JSON should be valid and properly formatted.

Remember to tailor the difficulty and complexity of the exercise to match the specified difficulty level, and use appropriate syntax and features of the given programming language.
    """
    return PromptTemplate(input_variables=["DIFFICULTY_LEVEL", "PROGRAMMING_LANGUAGE", "TOPIC"], template=generator_template)


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
    # outputParser = GeneratorOutputParser()
    outputParser = JsonOutputParser()
    res = generate_practice(50, "inherent", "advanced", "golang", prompt, outputParser)
    with open("result.json", 'w') as f:
        json.dump(res, f, indent=4)
