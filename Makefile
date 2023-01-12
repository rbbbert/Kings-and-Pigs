FILES=main.py enemy.py game_data.py level.py overworld.py particles.py\
player.py settings.py support.py tiles.py ui.py

run: $(FILES)
	python3 main.py
