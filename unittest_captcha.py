import unittest
from captcha import generate_captcha, check_answer


class TestCaptcha(unittest.TestCase):

    def test_generate_captcha(self):
        num1, num2, answer = generate_captcha()
        self.assertEqual(num1 + num2, answer)

    def test_check_answer_correct(self):
        self.assertTrue(check_answer(5, 5))

    def test_check_answer_incorrect(self):
        self.assertFalse(check_answer(4, 5))

    def test_check_answer_string(self):
        self.assertTrue(check_answer("7", 7))

    def test_check_answer_error(self):
        with self.assertRaises(ValueError):
            check_answer("abc", 5)


if __name__ == '__main__':
    unittest.main()