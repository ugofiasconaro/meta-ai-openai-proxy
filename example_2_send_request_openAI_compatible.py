# Author: Ugo Fiasconaro
from openai import OpenAI

from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

# Costruisci manualmente la risposta senza chiamata HTTP
response = ChatCompletion(
    id="chatcmpl-123",
    object="chat.completion",
    created=int(time.time()),
    model="meta-ai-openai-proxy",
    choices=[
        Choice(
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                content="def hello_world():\n    print('Hello World')\n\nhello_world()"
            ),
            finish_reason="stop"
        )
    ],
    usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
)

print(response.choices[0].message.content)
print("############# New")
import json
print(response.model_dump_json(indent=4))