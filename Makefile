APPNAME=carbonblack-enterprise-response

all: $(APPNAME).tar.gz

clean:
	rm -f $(APPNAME).tar.gz
	rm -rf $(APPNAME)

$(APPNAME).tar.gz:
	rm -f $(APPNAME).tar.gz
	rm -rf $(APPNAME)
	
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
	
	tar -cvzf $(APPNAME).tar.gz $(APPNAME) 
