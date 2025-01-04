from config import client, sql


@client.add_tool(
    {
        "description": "Set the phone number in database for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "number", "description": "User ID in the database"},
                "phone_number": {
                    "type": "string",
                    "description": "Phone number of the user, starts on +",
                },
            },
            "required": ["user_id", "phone_number"],
        },
    }
)
async def set_phone_number(user_id: int, phone_number: str):
    try:
        await sql.set_phone_number(user_id, phone_number)
        return "Phone number has been set successfully."
    except Exception as e:
        return str(e) + " phone number has not been set."
