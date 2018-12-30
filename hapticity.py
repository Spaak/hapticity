import logging
from spotipy import util
from spotipy.client import Spotify
import auth
from ir import Infrared

def build_codemap(spot):
	def play_or_pause():
		if spot.current_playback()['is_playing']:
			spot.pause_playback()
		else:
			spot.start_playback()

	def volume_up():
		curvol = spot.current_playback()['device']['volume_percent']
		spot.volume(max(100, curvol+5))

	def volume_down():
		curvol = spot.current_playback()['device']['volume_percent']
		spot.volume(min(0, curvol-5))

	# returns a dict mapping codes to callables
	return {
		0xffc23d: play_or_pause,			# play/pause
		0xff22dd: spot.previous_track,		# previous
		0xff02fd: spot.next_track,			# next
		0xffe01f: volume_down,				# volume down
		0xffa857: volume_up,				# volume up
	}


def init_code_handler(codemap):
	def handle_code(code):
		logging.info('received code: %s', hex(code))
		if code in codemap:
			logging.info('code recognized, executing associated action')
			codemap[code]()
		else:
			logging.info('code not recognized, doing nothing')


	return handle_code


def run_hapticity():
	scope = 'user-modify-playback-state,user-read-playback-state'
	token = util.prompt_for_user_token('Eelke Spaak', scope=scope,
		client_id=auth.client_id, client_secret=auth.client_secret, 
		redirect_uri=auth.redirect_url)
	spot = Spotify(token)

	callback = init_code_handler(build_codemap(spot))
	ir = Infrared(callback=callback)
	ir.listen()


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	run_hapticity()