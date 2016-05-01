APPNAME=carbonblack-enterprise-response
VERSION=0.9.1
all: $(APPNAME).spl

clean:
	rm -f $(APPNAME).spl
	rm -rf $(APPNAME)

$(APPNAME).spl:

	mkdir $(APPNAME)

	cp -r ./appserver $(APPNAME)
	cp -r ./bin $(APPNAME)
	cp -r ./default $(APPNAME)
	cp -r ./metadata $(APPNAME)
	cp -r ./static $(APPNAME)
	cp LICENSE $(APPNAME)
	cp README.md $(APPNAME)

	find $(APPNAME) -name ".*" -delete
	find $(APPNAME) -name "*.pyc" -delete

	tar -cvzf $(APPNAME).spl $(APPNAME)
