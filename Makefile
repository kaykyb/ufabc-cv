.PHONY: serve build clean

serve:
	hugo server --source site --buildDrafts --navigateToChanged

build:
	hugo --source site --minify

clean:
	rm -rf site/public site/resources site/.hugo_build.lock
