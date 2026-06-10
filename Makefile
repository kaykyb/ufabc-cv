.PHONY: serve build clean

serve:
	hugo server --source site --buildDrafts --navigateToChanged

build:
	hugo --source site --minify

clean:
	rm -rf site/public site/resources site/.hugo_build.lock

deploy: clean build
	rm -rf /tmp/cv-deploy-gh-branch && cp -r site/public /tmp/cv-deploy-gh-branch
	git checkout gh-pages-deploy
	cp -r /tmp/cv-deploy-gh-branch/. .
