NAME		= calicoctl
RELEASE		= 0
VERSION		= 3.1.0
CALICOCTLHTML 	= https://github.com/projectcalico/calicoctl/releases/download/v$(VERSION)/calicoctl
PKGROOT		= /etc/profile.d
RPM.FILES	= \
$(PKGROOT)/*\\n\
/usr/sbin/*

RPM.DESCRIPTION = profile scripts for calicoctl and binary downloaded from $(CALICOCTLHTML)
