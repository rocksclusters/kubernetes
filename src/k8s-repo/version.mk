-include 	$(CURDIR)/../../k8s-version.mk
NAME		= k8s-repo
RELEASE		= 0
VERSION		= $(K8SVERSION)
PKGROOT		= /etc/yum.repos.d
RPM.FILES	= $(PKGROOT)/*
RPM.DESCRIPTION = Yum repository definition for Kubernetes
RPM.ARCH	= noarch
