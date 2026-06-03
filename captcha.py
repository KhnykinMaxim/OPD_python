import random

def generate_captcha():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    return num1, num2, num1 + num2

def check_answer(user_answer, correct_answer):
    return int(user_answer) == correct_answer


