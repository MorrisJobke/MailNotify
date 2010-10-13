.PHONY: deb-package clean
DEB_PACKAGE_PATH=./deb-build/

deb-package:
	mkdir -P ${DEB_PACKAGE_PATH}

clean:
	rm -rf ${DEB_PACKAGE_PATH}
	
