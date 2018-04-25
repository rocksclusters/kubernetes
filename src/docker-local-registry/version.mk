NAME		= docker-local-registry
RELEASE		= 0
PKGROOT		= /etc/systemd/system
RPM.SCRIPTLETS.FILE = scriptlets
RPM.FILES	= $(PKGROOT)/*\n\
/opt/rocks/sbin/*
