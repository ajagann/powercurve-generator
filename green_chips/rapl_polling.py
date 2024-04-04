from polling import Polling
import logging

class RAPLPolling(Polling):
    def run(self):
        pass

    def run_polling(self):
        pass

if __name__ == "__main__":
    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.DEBUG)