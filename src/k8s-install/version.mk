-include 	$(CURDIR)/../../k8s-version.mk
NAME		= k8s-install
RELEASE		= 0
VERSION		= $(K8SVERSION)
PKGROOT		= /opt/rocks
RPM.FILES	= $(PKGROOT)/doc/*\n\
		  $(PKGROOT)/sbin/*
RPM.DESCRIPTION = install instructions for kubernetes
RPM.ARCH	= noarch
