# kubernetes
Kubernetes Support  Rocks 7

## Table of contents

1. [Building a roll](#buildroll)
2. [Install a roll on a live server](#liveinstall)
3. [Configure Kubernetes](#config)
    1. [Step1: Install Kubernetes using kubeadm](#step1)
    2. [Step2: Install calico network CNI](#step2)
    3. [Step3: Update Calico configuration](#step3)
    4. [Step4: Add compute nodes to kubernetes cluster](#step4)
4. [Start a demo container](#sample)

### Building a roll <a name="buildroll"></a>
Check out roll source from github
```bash
git clone https://github.com/rocksclusters/kubernetes
cd kubernetes
```
To build a roll:
```bash
./bootstrap.sh
make roll
```
The successfull build results in creating kubernetes-VERSION-0.x86_64.disk1.iso
where VERSION is a current version of kubernetes source.

### Install a roll on a live server <a name="liveinstall"></a>

```bash
rocks add roll  kubernetes-VERSION-0.x86_64.disk1.iso
rocks enable roll kubernetes
(cd /export/rocks/install; rocks create distro)
```
Create a script with instructions to add roll to a frontend and run it:
```bash
rocks run roll kubernetes > add-k.sh
bash  add-k.sh
```

To install kubernetes on compute ndoes  create a scirpt with instructions
in a directory NFS-mounted on all nodes:	
```bash
rocks run roll kubernetes host=compute-0-0 > /share/apps/add-k-compute.sh

```
Run the script on all compute nodes (or a subset):
```bash
rocks run host compute "bash /share/apps/add-k-compute.sh"
```

### Configure Kubernetes <a name="config"></a>
This section explains configuring kubernetes after the roll is installed. 

1. Frontend is the kubernetes master
2. MUST be connected to the internet to download kubernetes pods.


#### Step1: Install Kubernetes using kubeadm <a name="step1"></a>
```bash
kubeadm init --pod-network-cidr=192.168.0.0/16 --apiserver-advertise-address=$(rocks report host attr localhost attr=Kickstart_PrivateAddress)
```
Wait until all pods are in running state (except kube-dns). To verify state run a command:
```bash
kubectl -n kube-system get pods
NAMESPACE     NAME                                    READY     STATUS    RESTARTS   AGE
kube-system   etcd-pc-171.co.net                      1/1       Running   0          26s
kube-system   kube-apiserver-pc-171.co.net            1/1       Running   0          45s
kube-system   kube-controller-manager-pc-171.co.net   1/1       Running   0          43s
kube-system   kube-dns-86f4d74b45-lk89c               0/3       Pending   0          1m
kube-system   kube-proxy-txj5v                        1/1       Running   0          1m
kube-system   kube-scheduler-pc-171.co.net            1/1       Running   0          42s
```
#### Step2: Install  calico network CNI <a name="step2"></a>
```bash
kubectl apply -f https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/hosted/kubeadm/1.7/calico.yaml
```
Wait until kube-dns us Running 
```bash
kubectl -n kube-system get pods | grep dns | grep Running
```
#### Step3: Update Calico configuration <a name="step3"></a>
Edit the daemonset configuration of Calico so that the it will use the local interface.
First, get the current configuration and save in a file:
```bash
kubectl get daemonset -n kube-system calico-node -o yaml > /tmp/calico-node.yaml
```

Edit the resulting yaml file, and find lines that look like:
```text
        - name: IP
          value: autodetect
        - name: FELIX_HEALTHENABLED
          value: "true"
```

Add the IP_AUTODETECTION_METHOD so that the lines look like (assuming your frontend local ip is 10.1.1.1). (Please note that
consistent indentation is important):
```text
        - name: IP
          value: autodetect
        - name: IP_AUTODETECTION_METHOD
          value: can-reach=10.1.1.1
        - name: FELIX_HEALTHENABLED
          value: "true"
```
Apply your changes:
```bash
kubectl apply -f /tmp/calico-node.yaml
```

The output should look like:
```text
daemonset.extensions "calico-node" configured
```

#### Step4: Add compute nodes to kubernetes cluster <a name="step4"></a>
Add compute nodes to the kubernetes cluster:
```bash
rocks run host compute "swapoff -a"
rocks run host compute "$(kubeadm token create --print-join-command)"
```

Check which nodes are running:
```bash
kubectl get nodes
```
The output will be similar to:
``` text
NAME                          STATUS    ROLES     AGE       VERSION
compute-0-0.local             Ready     <none>    1m        v1.10.2
pc-171.co.net                 Ready     master    9m        v1.10.2
```

### Start a demo container <a name="sample"></a>
Start a simple demo container:
```bash
kubectl create -f https://k8s.io/docs/tasks/debug-application-cluster/shell-demo.yaml
```
Get a bash shell inside the container :
```bash 
kubectl exec -it shell-demo /bin/bash
```
Once on a container, run a few commands to install extra packages, test network and the like:

```bash
apt-get update
apt-get install iproute2
apt-get install dnsutils
apt-get install iputils-ping
ping 8.8.8.8
ip addr show
```

