import os

import anthropic
import dotenv

dotenv.load_dotenv()


client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

prompt = """
You are an experienced software architect and technical interviewer. Your task is to analyze a basic project description, expand upon it, increase its complexity to match real-world business scenarios, and identify potential technical challenges that might be asked about in an interview, with a focus on backend technologies.\n\nHere's the project description you'll be working with:\n\n<project_description>\n{{PROJECT_DESCRIPTION}}\n</project_description>\n\nPlease follow these steps to complete the task:\n\n1. Carefully read and analyze the given project description.\n\n2. Expand and enrich the project description:\n   - Identify key components and features that are implied but not explicitly stated.\n   - Add realistic details about the system architecture, data flow, and user interactions.\n   - Consider scalability, performance, and security aspects that would be relevant in a production environment.\n\n3. Increase the system's complexity:\n   - Introduce additional features or requirements that align with the project's goals and real-world business needs.\n   - Consider integration with other systems or third-party services that would be common in similar projects.\n   - Add constraints or challenges that the system might face in a real-world scenario (e.g., high concurrency, data volume, regulatory compliance).\n\n4. Identify potential technical interview questions:\n   - Think about challenging aspects of the expanded system design, focusing on backend technologies.\n   - Consider questions related to databases, distributed systems, scalability, performance optimization, data consistency, and fault tolerance.\n   - Include questions about specific backend technologies, algorithms, or architectural patterns that might be relevant to the project.\n\nBefore providing your final response, break down your thought process for each step in <analysis> tags. For each step:\n- List key components or features you've identified or added\n- Provide justifications for your additions or changes\n- Consider potential challenges or implications of your decisions\n\nThis will help ensure a thorough analysis and consideration of all aspects of the project.\n\nYour final output should be structured as follows:\n\n<expanded_description>\n[Provide the expanded and enriched project description here, including key components, architectural details, and considerations for scalability, performance, and security.]\n</expanded_description>\n\n<increased_complexity>\n[Describe the additional features, integrations, and challenges that increase the system's complexity, focusing on real-world business needs and technical constraints.]\n</increased_complexity>\n\n<potential_interview_questions>\n[List 5-7 potential technical interview questions related to the expanded project, with a focus on backend technologies, databases, distributed systems, and implementation challenges. Each question should be challenging and relevant to the technical aspects of the expanded project.]\n</potential_interview_questions>\n\nEnsure that your expansion and complexity increase are realistic and align with current industry practices. The potential interview questions should be challenging and relevant to the technical aspects of the expanded project, with a particular emphasis on backend technologies and system design.\n\nExample output structure (do not copy the content, only the format):\n\n<expanded_description>\nThe project is a distributed e-commerce platform that... [continue with detailed description]\n</expanded_description>\n\n<increased_complexity>\nTo increase complexity, we can introduce the following features and challenges:\n1. Multi-region deployment for improved latency and redundancy...\n2. Real-time inventory management across multiple warehouses...\n3. Integration with third-party payment gateways and fraud detection services...\n[continue with more complexity factors]\n</increased_complexity>\n\n<potential_interview_questions>\n1. How would you design the database schema to efficiently handle product catalogs, user data, and order information at scale?\n2. Describe a strategy for maintaining data consistency across multiple microservices in this distributed e-commerce system.\n3. What approach would you take to implement a real-time inventory management system that can handle high concurrency during flash sales?\n[continue with more questions, focusing on backend and distributed systems challenges]\n</potential_interview_questions>
"""

PROJECT_DESCRIPTION="""
我现在做的是一个全球的牙科系统，它部署在云端上。支持gcp和阿里云两朵云。 其主要业务包含：
- 下订单
- 病人管理
- 文件分享和渲染 等
主要技术栈是golang grpc
"""

prompt = prompt.replace("{{PROJECT_DESCRIPTION}}", PROJECT_DESCRIPTION)

# Replace placeholders like {{PROJECT_DESCRIPTION}} with real values,
# because the SDK does not support variables.
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text":  prompt
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "<analysis>"
                }
            ]
        }
    ]
)
print(message.content)

# save the response to a file
with open("output.txt", "w") as f:
    data = message.content[0].text
    f.write(data)