
async def is_number_in_range(s):
    try:
        num = float(s)
        return True
    except ValueError:
        return False
