-include        $(CURDIR)/../../docker-ce-version.mk
NAME		= docker-ce-repo
RELEASE		= 0
VERSION         = $(DOCKERCEVERSION)
PKGROOT		= /etc/yum.repos.d
RPM.FILES	= $(PKGROOT)/*
RPM.DESCRIPTION = Yum repository definition for docker-ce 
RPM.ARCH	= noarch
