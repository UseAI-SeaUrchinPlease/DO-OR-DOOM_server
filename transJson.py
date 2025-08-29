def format_tasks_from_json(string) -> str:
    """
    Parses a JSON string, extracts task contents, and formats them.

    Args:
        json_string: A string containing the JSON data.

    Returns:
        A formatted string with a header and a list of tasks.
    """
    # Parse the JSON string into a Python dictionary
    data = string
    
    # Extract the list of tasks
    tasks = data.get("tasks", [])
    
    # Get just the "contents" from each task dictionary
    contents_list = [task.get("contents", "") for task in tasks]
    
    # Format the list into the desired string
    # Join the items with a newline, a tab, and a hyphen
    formatted_tasks = "\n\t- ".join(contents_list)
    
    # Add the header and the first task's indentation
    final_string = f"#タスク\n\t- {formatted_tasks}"
    
    return final_string
def _get_content_from_response(data) -> dict:

    choices = data.get("choices")
    if isinstance(choices, list) and len(choices) > 0:
        first = choices[0]
        if isinstance(first, dict):
            msg = first.get("message")
            if isinstance(msg, dict):
                contents = msg.get("content")

    if contents is None:
        # 取り出せなければ元のdataをそのまま返す（デバッグ用）
        contents = data
    
    return {"reply": contents}