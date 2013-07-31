CHROOT_LINUX=chroot --userspec 65543:65534
CHROOT_DARWIN=chroot -u nobody -g nobody

PLATFORM=`python -c 'import sys; print sys.platform'`
ifeq ($(PLATFORM),darwin)
	CHROOT=$(CHROOT_DARWIN)
else
	CHROOT=$(CHROOT_LINUX)
endif

.PHONY: test clean

test: alcatraz
	sudo $(CHROOT) alcatraz bin/sh

alcatraz:
	sudo ./mkjail.py alcatraz /bin/* /sbin/* /usr/bin/* /usr/sbin/* /usr/local/bin/* /usr/local/sbin/*

clean:
	sudo rm -r alcatraz ; true
