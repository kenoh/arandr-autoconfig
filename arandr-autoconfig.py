#!/usr/bin/env python3
import click
import time
import os.path
import subprocess
import re


def parse_xrandr_output(text):
	pattern = re.compile(r"^([^ ]+) connected")
	ret = filter(lambda x: pattern.match(x), text.decode('utf-8').splitlines())
	ret = map(lambda x: pattern.match(x).group(1), ret)
	return sorted(ret)

def current_connected_displays():
	proc = subprocess.run(["xrandr"], stdout=subprocess.PIPE)
	return parse_xrandr_output(proc.stdout)

def script_name(displays):
	return os.path.expanduser(os.path.join("~",
	                                       ".screenlayout",
	                                       "_".join(displays) + ".sh"))

def run_script(path):
	try:
		subprocess.run([path])
		return True
	except Exception as e:
		print("Could not run script:", e)
		return False

def set_xrandr_with_script(path):
	if not run_script(path):
		subprocess.run(["xrandr", "-s", "0"])


def loop(post):
	previous = current_connected_displays()
	while True:
		new = current_connected_displays()
		if new != previous:
			previous = new
			script = script_name(new)
			print("changed:", new, ", calling:", script)
			set_xrandr_with_script(script)
			if post:
				print("calling post:", post)
				run_script(post)
		time.sleep(1)


@click.option("--post", default=None, help="program to run after a change")
@click.command()
def main(post):
	print("startup:", current_connected_displays())
	loop(post)


if __name__ == '__main__':
	main()
