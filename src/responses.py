def error_response(message, status_code=400):
    return ({"status": f"ERROR ({status_code})", "message": message}, status_code)


def success_response(message, status_code=200):
    return ({"status": f"SUCCESS ({status_code})", "message": message}, status_code)
