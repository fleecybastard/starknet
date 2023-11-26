from fake_useragent import UserAgent


def generate_user_agent():
    return UserAgent().random
