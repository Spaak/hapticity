import logging
from ir import Infrared


def handle_code(code):
	logging.info('received code: %s', hex(code))


def run_hapticity():
	ir = Infrared(callback=handle_code)
	ir.listen()


if __name__ == '__main__':
	run_hapticity()