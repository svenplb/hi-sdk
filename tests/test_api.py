import unittest
from sdk.client import HiClient, ModelNotFoundError, InvalidConfigError, ConnectionError
import time
from unittest.mock import MagicMock, patch
import requests
from colorama import init, Fore, Style

init()  # Initialize colorama


class ColorTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _makeResult(self):
        return ColorTestResult(self.stream, self.descriptions, self.verbosity)


class ColorTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        test_name = test.shortDescription() or str(test)
        # Remove the class name prefix if it exists
        if "(__main__.TestAPI)" in test_name:
            test_name = test_name.split("(__main__.TestAPI)")[0].strip()
        self.stream.write(f'\n{Fore.GREEN}✓ {test_name}{Style.RESET_ALL}\n')

    def addError(self, test, err):
        test_name = test.shortDescription() or str(test)
        if "(__main__.TestAPI)" in test_name:
            test_name = test_name.split("(__main__.TestAPI)")[0].strip()
        self.stream.write(f'\n{Fore.RED}✗ {test_name}{Style.RESET_ALL}\n')
        self.stream.write(
            f'{Fore.RED}{self._exc_info_to_string(err, test)}{Style.RESET_ALL}\n')

    def addFailure(self, test, err):
        test_name = test.shortDescription() or str(test)
        if "(__main__.TestAPI)" in test_name:
            test_name = test_name.split("(__main__.TestAPI)")[0].strip()
        self.stream.write(f'\n{Fore.RED}✗ {test_name}{Style.RESET_ALL}\n')
        self.stream.write(
            f'{Fore.RED}{self._exc_info_to_string(err, test)}{Style.RESET_ALL}\n')

    def printErrors(self):
        if self.errors or self.failures:
            self.stream.write(f'\n{Fore.RED}Failed Tests:{Style.RESET_ALL}\n')
        super().printErrors()

    def printTotal(self):
        run = self.testsRun
        failed = len(self.failures)
        errors = len(self.errors)
        passed = run - failed - errors

        self.stream.write('\n')
        self.stream.write('Test Summary:\n')
        self.stream.write(f'{Fore.GREEN}✓ {passed} passed{Style.RESET_ALL}\n')
        if failed:
            self.stream.write(
                f'{Fore.RED}✗ {failed} failed{Style.RESET_ALL}\n')
        if errors:
            self.stream.write(
                f'{Fore.RED}✗ {errors} errors{Style.RESET_ALL}\n')


class TestAPI(unittest.TestCase):
    """Test suite for the HiClient SDK"""

    def setUp(self):
        self.client = HiClient()
        self.client.load_model("qwen:1.8b")

    def test_load_model(self):
        """Should successfully load a model"""
        self.assertEqual(
            self.client.model_manager.model_config.model_name, "qwen:1.8b")

    def test_invalid_model(self):
        """Should raise ModelNotFoundError when loading invalid model"""
        with self.assertRaises(ModelNotFoundError):
            self.client.load_model("nonexistent_model")

    def test_empty_message(self):
        """Test that empty messages raise InvalidConfigError"""
        with self.assertRaises(InvalidConfigError):
            self.client.chat("")

    def test_chat_without_model(self):
        """Test that chatting without loading a model raises InvalidConfigError"""
        client = HiClient()
        with self.assertRaises(InvalidConfigError):
            client.chat("Hello")

    def test_callbacks(self):
        on_token = MagicMock()
        on_response = MagicMock()
        on_error = MagicMock()

        self.client.register_callback("on_token", on_token)
        self.client.register_callback("on_response", on_response)
        self.client.register_callback("on_error", on_error)

        response = self.client.chat("Test message")

        self.assertTrue(on_token.called)
        self.assertTrue(on_response.called)
        self.assertFalse(on_error.called)

    def test_model_parameters(self):
        self.client.set_model_parameters(temperature=0.7, top_p=0.9)
        self.assertEqual(
            self.client.model_manager.model_config.parameters["temperature"], 0.7)
        self.assertEqual(
            self.client.model_manager.model_config.parameters["top_p"], 0.9)

    def test_conversation_tracking(self):
        client = HiClient(track_conversation=True)
        client.load_model("qwen:1.8b")

        response = client.chat("Hello")
        self.assertEqual(len(client.conversation.messages), 2)

        client.clear_conversation()
        self.assertEqual(len(client.conversation.messages), 0)

    def test_system_prompt(self):
        prompt = "You are a helpful assistant"
        self.client.set_system_prompt(prompt)
        self.assertEqual(self.client.system_prompt, prompt)

    def test_role(self):
        response = self.client.chat("Hello", role="comedian")
        self.assertIsNotNone(response)

    def test_connection_error(self):
        """Test that connection errors are properly handled"""
        client = HiClient(base_url="http://localhost:9999")
        client.load_model("qwen:1.8b")
        with self.assertRaises(ConnectionError):
            client.chat("Test message")

    def test_continuous_chat(self):
        on_listening = MagicMock(return_value="Hello")
        self.client.register_callback("on_listening", on_listening)

        self.client.start_continuous_chat(interval=0.1)
        time.sleep(0.3)
        self.client.stop_continuous_chat()

        self.assertTrue(on_listening.called)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAPI)
    runner = ColorTestRunner(verbosity=2)
    result = runner.run(suite)
    result.printTotal()  # Print the color summary
