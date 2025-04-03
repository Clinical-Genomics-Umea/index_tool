import logging

from modules.view.logging.message_toast import MessageToast


class LogToastHandler(logging.Handler):
    """ Custom log handler to send warning messages to the status bar. """
    def __init__(self, message_toast: MessageToast):
        super().__init__()
        self.message_toast = message_toast

    def emit(self, record):

        msg = record.getMessage()

        if record.levelno >= logging.WARNING:
            self.message_toast.show_message(self, msg, warn=True)

        else:
            self.message_toast.show_message(self, msg, warn=False)