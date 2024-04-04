from abc import ABC

class Polling(ABC):
    @ABC.abstractmethod
    def run(self):
        pass

    @ABC.abstractmethod
    def run_polling(self):
        pass
