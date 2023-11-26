from faker import Faker


faker = Faker()


def generate_email_address() -> str:
    return faker.free_email()


def generate_email_subject() -> str:
    return faker.sentence(nb_words=4)
