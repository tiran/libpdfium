SPEC = libpdfium.spec

.PHONY: srpm rpm getsource
getsource:
	spectool -g $(SPEC)
srpm: getsource
	rpmbuild --define "_sourcedir $(CURDIR)" --define "_srcrpmdir $(CURDIR)" --define "dist .el9" -bs $(SPEC)

rpm: getsource
	rpmbuild --define "_sourcedir $(CURDIR)" --define "_rpmdir $(CURDIR)" -bb $(SPEC)
