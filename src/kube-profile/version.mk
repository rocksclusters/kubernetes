-include 	$(CURDIR)/../../k8s-version.mk
NAME		= kube-profile
RELEASE		= 0
VERSION		= $(K8SVERSION)
PKGROOT		= /etc/profile.d
RPM.FILES	= $(PKGROOT)/*
RPM.DESCRIPTION = profile scripts for kubernetes 
RPM.ARCH	= noarch
