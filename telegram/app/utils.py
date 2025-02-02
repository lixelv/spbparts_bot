import re

from config import OPENAI_ASSISTANT_ID
from functions import client


def clear_context(text):
    return re.sub(r"【.*】", "", text)


async def get_answer_async(request, thread_id: str, context: any) -> str:
    return clear_context(
        await client.run_with_tool_by_thread_id(
            f"USER_INFO: {context}\n\n{request}",
            thread_id=thread_id,
            assistant_id=OPENAI_ASSISTANT_ID,
            use_tools=False,
        )
    )
