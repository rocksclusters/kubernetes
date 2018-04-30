#!/usr/bin/env python

import re
import subprocess
import sys
import time

KUBE_CIDR="192.168.0.0/16"
POD_WAIT_PERIOD=30
CALICO_URL="https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/hosted/kubeadm/1.7/calico.yaml"
CALICO_TMP_YAML="/tmp/calico-node.yaml"
CALICO_EXTRA = """
        - name: IP_AUTODETECTION_METHOD
          value: can-reach=10.1.1.1"""

def runCommand(cmd, desc):
	print "\n---- %s ----\n" % desc
	print cmd
	status = subprocess.call(cmd, shell=True)
	if status != 0:
		sys.stderr.write("Error: %s, cmd = %s" % (desc, cmd))
		sys.exit(1)
	print "\n==> Success"

def getOutput(cmd, desc):
	p = subprocess.Popen(
		cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT, shell=True)
	grep_stdout = p.communicate()[0]
	p.wait()
	if p.returncode != 0:
		sys.stderr.write("Error: %s, cmd = %s" % (desc, cmd))
		sys.exit(1)
	return grep_stdout.strip()

def waitTillPodRunning(*pods):
	while True:
		status = getOutput("kubectl -n kube-system get pods", "Getting pod status")
		pod_state = {}
		num_running = 0
		for pod in pods:
			m = re.search("%s\S+\s+\d+\/\d+\s+\s+(\S+)" % pod, status)
			if m:
				pod_state[pod] = m.group(1)
				if pod_state[pod] == "Running":
					num_running += 1
		print pod_state
		if num_running != len(pods):
			print "Sleeping %i seconds" % POD_WAIT_PERIOD
			time.sleep(POD_WAIT_PERIOD)
		else:
			return num_running
		
def fixCalicoYaml():
	calico_yaml = getOutput("kubectl get daemonset -n kube-system calico-node -o yaml", "Getting calico yaml")
	calico_yaml_replace = re.sub("name:\s+IP\n\s+value:\s+autodetect", "\g<0>%s" % CALICO_EXTRA, calico_yaml)
	try:
		f = open(CALICO_TMP_YAML, "w")
		f.write(calico_yaml_replace)
		f.close()
	except:
		sys.stderr.write("Error fixing calico yaml")
		sys.exit(1)
	runCommand("kubectl apply -f %s" % CALICO_TMP_YAML, "Applying new calico config")

# main
runCommand("swapoff -a", "Turning of swap for Kubernetes")
runCommand("systemctl daemon-reload", "Reloading systemctl files")
runCommand("systemctl stop kubelet", "Stopping kubelet")
runCommand("systemctl start docker", "Checking docker status")
runCommand("kubeadm reset", "Resetting kubernetes")
fe_private_ip = getOutput("rocks report host attr localhost attr=Kickstart_PrivateAddress", "Getting private IP of frontend")
runCommand("kubeadm init --pod-network-cidr=%s --apiserver-advertise-address=%s" % (KUBE_CIDR, fe_private_ip), "Configuring kubernetes")
waitTillPodRunning("kube-apiserver", "kube-scheduler", "kube-proxy")
runCommand("kubectl apply -f %s" % CALICO_URL, "Configuring calico")
waitTillPodRunning("kube-dns")
fixCalicoYaml()
runCommand('rocks run host compute "swapoff -a"', "Turning swap off on compute nodes")
