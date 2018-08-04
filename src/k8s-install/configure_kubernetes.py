#!/usr/bin/env python

import re
import subprocess
import sys
import time

COMMENT_LENGTH=80
KUBE_CIDR="192.168.0.0/16"
WAIT_PERIOD=30
CALICO_URL="https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/hosted/kubeadm/1.7/calico.yaml"
CALICO_TMP_YAML="/tmp/calico-node.yaml"
CALICO_EXTRA = """
        - name: IP_AUTODETECTION_METHOD
          value: can-reach=10.1.1.1"""
SHELL_URL="https://k8s.io/examples/application/shell-demo.yaml"


def printDescription(desc):
	print
	print "#"*COMMENT_LENGTH
	print "# %s" % desc
	print "#"*COMMENT_LENGTH

def runCommand(cmd, desc):
	printDescription(desc)
	print "COMMAND: %s" % cmd
	status = subprocess.call(cmd, shell=True)
	if status != 0:
		sys.stderr.write("Error: %s, cmd = %s" % (desc, cmd))
		sys.exit(1)
	print "\n==> Success"

def getOutput(cmd, desc=None):
	if desc:
		printDescription(desc)
	print "COMMAND: %s" % cmd
	p = subprocess.Popen(
		cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT, shell=True)
	grep_stdout = p.communicate()[0]
	p.wait()
	if p.returncode != 0:
		sys.stderr.write("Error: %s, cmd = %s" % (desc, cmd))
		sys.exit(1)
	return grep_stdout.strip()

def waitTillState(proc_type, status_cmd, proc_regex, desired_state, *procs):
	printDescription("Waiting for these %ss to be running: %s" % (proc_type, ", ".join(procs)))
	while True:
		print "Sleeping for %i seconds" % WAIT_PERIOD
		time.sleep(WAIT_PERIOD)
		status = getOutput("%s" % status_cmd)
		proc_state = {}
		num_running = 0
		for proc in procs:
			m = re.search(proc_regex % proc, status, re.MULTILINE)
			if m:
				proc_state[proc] = m.group(1)
				if proc_state[proc] == desired_state:
					num_running += 1
		print "Status: %s" % ", ".join(["%s is %s" % (k, proc_state[k]) for k in proc_state.keys()])
		if num_running == len(procs):
			return num_running

def waitTillPodRunning(namespace, *pods):
	cmd = "kubectl %s get pods"
	option = ""
	if namespace:
		option = "-n %s" % namespace
	cmd = cmd % option
	waitTillState("pod", cmd, "%s\S*\s+\d+\/\d+\s+\s+(\S+)", "Running", *pods)
		
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

# first configure k8 on frontend
starttime = time.time()
runCommand("swapoff -a", "Turning of swap for Kubernetes")
runCommand("systemctl daemon-reload", "Reloading systemctl files")
runCommand("systemctl stop kubelet", "Stopping kubelet")
runCommand("systemctl start docker", "Checking docker status and start if not running")
runCommand("yes | kubeadm reset", "Resetting kubernetes")
fe_private_ip = getOutput("rocks report host attr localhost attr=Kickstart_PrivateAddress", "Getting private IP of frontend")
runCommand("kubeadm init --pod-network-cidr=%s --apiserver-advertise-address=%s" % (KUBE_CIDR, fe_private_ip), "Configuring kubernetes")
waitTillPodRunning("kube-system", "kube-apiserver", "kube-scheduler", "kube-proxy")
runCommand("kubectl apply -f %s" % CALICO_URL, "Configuring calico network for kubernetes")
waitTillPodRunning("kube-system", "dns")
fixCalicoYaml()

# then configure k8 on compute nodes which will be become k8 nodes
runCommand('rocks run host compute "swapoff -a"', "Turning swap off on kubernetes nodes")
runCommand('rocks run host compute "systemctl start docker"', "Checking docker status on kubernetes  nodes and start if not running")
runCommand('rocks run host compute "yes | kubeadm reset"', "Resetting kubernetes")
join_cmd = getOutput("kubeadm token create --print-join-command", "Getting unique token to allow to kubernetes  nodes join")
runCommand('rocks run host compute "%s"' % join_cmd, "Configuring container nodes")
computes = getOutput("rocks list host | grep Compute | cut -f 1 -d:", "Getting Rocks compute node names")
waitTillState("node", "kubectl get nodes", "^%s\S+\s+(\S+)", "Ready", *computes.split("\n"))

# deploy demo and print status
runCommand("kubectl create -f %s" % SHELL_URL, "Deploying shell-demo example container")
waitTillPodRunning(None, "shell-demo")
printDescription("Kubernetes is ready! (took %i secs)" % (time.time() - starttime))
print "Please use the following command to login to the shell-demo container:"
print "kubectl exec -it shell-demo /bin/bash"
