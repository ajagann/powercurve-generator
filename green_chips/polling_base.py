from abc import ABC

class Polling(ABC):
    @ABC.abstractmethod
    def run_polling(self):
        pass

    @ABC.abstractmethod
    def send_signal(self):
        pass
