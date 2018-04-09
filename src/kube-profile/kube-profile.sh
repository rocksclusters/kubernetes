#!/bin/bash
KUBEADMIN=/etc/kubernetes/admin.conf
if [ $(/usr/bin/id -u) == "0" ]; then
	if [ "x$KUBECONFIG" == "x" ]; then 
		export KUBECONFIG=$KUBEADMIN
	fi
else
	if [ ! -d $HOME/.kube ]; then
		export KUBECONFIG=$KUBEADMIN
	fi
fi
