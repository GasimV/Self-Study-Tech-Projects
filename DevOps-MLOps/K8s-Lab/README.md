# K8s-Lab — Hands-On Kubernetes Journey

This folder is my hands-on lab log while working through **_Mastering Kubernetes_ by Gigi Sayfan**. The goal is to actually build, run, break, and inspect Kubernetes clusters on my own machine — not just read about them — and to keep a running record of the commands I ran, the output I got, and what each step actually did under the hood.

I'm following the book's progression, starting from a local single-node cluster and moving toward more advanced multi-node and production-style setups.

---

## Table of Contents

1. [Creating a single-node cluster with Minikube](#1-creating-a-single-node-cluster-with-minikube)
   - [Quick introduction to Minikube](#quick-introduction-to-minikube)
   - [Installing Minikube on Windows](#installing-minikube-on-windows)
   - [Setting up shortcuts and verifying the install](#setting-up-shortcuts-and-verifying-the-install)
   - [Starting the cluster](#starting-the-cluster)
   - [Checking status, stopping, and restarting](#checking-status-stopping-and-restarting)
   - [What Minikube does behind the scenes](#what-minikube-does-behind-the-scenes)
2. [Checking out the cluster](#2-checking-out-the-cluster)
   - [SSH into the node VM](#ssh-into-the-node-vm)
   - [Cluster info and nodes with kubectl](#cluster-info-and-nodes-with-kubectl)
   - [Listing the default addons](#listing-the-default-addons)
3. [Doing work — deploy, expose, and call a service](#3-doing-work--deploy-expose-and-call-a-service)
4. [Examining the cluster with the dashboard](#4-examining-the-cluster-with-the-dashboard)
5. [Tearing the cluster down](#5-tearing-the-cluster-down)

---

## 1. Creating a single-node cluster with Minikube

In this first section I create a local **single-node** cluster using Minikube.

A local cluster is the most useful tool for fast **edit → test → deploy → debug** cycles on my own machine before committing changes. It's also great for experimenting with Kubernetes without the risk of breaking a shared environment, or spinning up expensive cloud resources and forgetting to tear them down.

Kubernetes is typically deployed on Linux in production, but a lot of development happens on Windows or macOS. I'm on Windows here, and the differences from a Linux install are minimal.

### Quick introduction to Minikube

Minikube is the most mature local Kubernetes option. It runs the latest stable Kubernetes release and supports **Windows, macOS, and Linux**. Despite being a "local" tool, it exposes a surprising amount of real Kubernetes functionality:

| Capability | How it's exposed |
| --- | --- |
| `LoadBalancer` service type | `minikube tunnel` |
| `NodePort` service type | `minikube service` |
| Multiple clusters | profiles |
| Filesystem mounts | mount support |
| GPU support (for ML) | driver-dependent |
| RBAC | enabled |
| Persistent Volumes | enabled |
| Ingress | addon |
| Dashboard | `minikube dashboard` |
| Custom container runtimes | `start --container-runtime` flag |
| API server / kubelet options | command-line flags |
| Addons | addon system |

### Installing Minikube on Windows

The canonical install guide is the official one: <https://minikube.sigs.k8s.io/docs/start/>

On Windows I use the **Chocolatey** package manager (<https://chocolatey.org/>). If you'd rather not use Chocolatey, the official guide lists alternatives.

With Chocolatey installed, the install is a one-liner (run from an elevated PowerShell):

```powershell
choco install minikube -y
```

This pulls in both `minikube` and `kubernetes-cli` (which provides `kubectl`) and creates shims so both are on the `PATH`. In my run it installed **Minikube v1.25.2** and **kubernetes-cli v1.24.0**.

> **Console / shell notes:** On Windows you can drive Minikube from either **PowerShell** or **WSL** — both work, and some operations need an elevated (Administrator) shell. I use the official **Windows Terminal**, which can also be installed via Chocolatey:
>
> ```powershell
> choco install microsoft-windows-terminal --pre
> ```

### Setting up shortcuts and verifying the install

To save keystrokes I alias `kubectl` to `k` and `minikube` to `mk`.

**PowerShell** — add to your `$profile`:

```powershell
function k  { kubectl.exe $args }
function mk { minikube.exe $args }
```

**WSL** — add to `.bashrc`:

```bash
alias k='kubectl.exe'
alias mk='minikube.exe'
```

Verify the install:

```console
$ mk version
minikube version: v1.25.2
commit: 362d5fdc0a3dbee389b3d3f1034e8023e72bd3a7
```

### Starting the cluster

Create the cluster with `mk start`:

```console
$ mk start
  minikube v1.25.2 on Microsoft Windows 10 Pro
  Automatically selected the docker driver. Other choices: hyperv, ssh
  Starting control plane node minikube in cluster minikube
  Pulling base image ...
  Downloading Kubernetes v1.23.3 preload ...
  Creating docker container (CPUs=2, Memory=8100MB) ...
  Downloading VM boot image ...
  Starting control plane node minikube in cluster minikube
  Creating hyperv VM (CPUs=2, Memory=6000MB, Disk=20000MB) ...
  Preparing Kubernetes v1.23.3 on Docker 20.10.12 ...
    ▪ Generating certificates and keys ...
    ▪ Booting up control plane ...
    ▪ Configuring RBAC rules ...
  Verifying Kubernetes components...
  Enabled addons: storage-provisioner, default-storageclass
  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

Even the **default** setup is a fairly involved process, and Minikube transparently retries steps that fail (for example, image pulls that have trouble reaching `k8s.gcr.io`). The whole thing is highly customizable — `mk start -h` lists the full set of flags for tuning drivers, CPU/memory, Kubernetes version, container runtime, and more.

### Checking status, stopping, and restarting

Check cluster status:

```console
$ mk status
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

Stop the cluster:

```console
$ mk stop
 Stopping node "minikube" ...
 Powering off "minikube" via SSH ...
 1 node stopped.
```

Restart it, timing how long a warm restart takes:

```console
$ time mk start
  minikube v1.25.2 on Microsoft Windows 10 Pro
  Using the hyperv driver based on existing profile
  Restarting existing hyperv VM for "minikube" ...
  Preparing Kubernetes v1.23.3 on Docker 20.10.12 ...
  Verifying Kubernetes components...
  Enabled addons: storage-provisioner, default-storageclass
  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
real    1m8.666s
```

A warm restart reuses the existing profile/VM, so it's much faster than the first cold start — a little over a minute in my case.

### What Minikube does behind the scenes

The reason `mk start` is worth appreciating is that it automates everything you'd otherwise have to do by hand when building a cluster from scratch. Behind the curtain it:

1. Started a **Hyper-V VM**.
2. Created **certificates** for the local machine and the VM.
3. **Downloaded** the required images.
4. Set up **networking** between the local machine and the VM.
5. Ran the local **Kubernetes cluster** on the VM.
6. **Configured** the cluster.
7. Started all the **control plane** components.
8. Configured the **kubelet**.
9. Enabled **addons** (for storage).
10. Configured **`kubectl`** to talk to the cluster.

Keeping this list in mind is useful — every one of these steps reappears (manually) when provisioning a cluster the hard way later in the book.

---

## 2. Checking out the cluster

With a cluster running, the next thing I do is poke around inside it.

### SSH into the node VM

Minikube runs the cluster inside a VM, and I can drop into a shell on that VM directly:

```console
$ mk ssh
        _             _
   _         _ ( )           ( )
 ___ ___  (_)  ___  (_)| |/')  _   _ | |_      __
... (ASCII art spelling "minikube") ...

$ uname -a
Linux minikube 4.19.202 #1 SMP Tue Feb 8 19:13:02 UTC 2022 x86_64 GNU/Linux
```

The banner is just ASCII art spelling out "minikube." `uname -a` confirms I'm on the Linux node that actually hosts the cluster. To get back to the host, disconnect with **Ctrl+D** or `logout`.

From here on I lean on **`kubectl`** — the Swiss Army knife of Kubernetes, and the one tool that works against every cluster regardless of how it was provisioned.

### Cluster info and nodes with kubectl

Check that the control plane is healthy:

```console
$ k cluster-info
Kubernetes control plane is running at https://172.26.246.89:8443
CoreDNS is running at https://172.26.246.89:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

`k cluster-info dump` gives a full JSON dump of every object in the cluster — useful but overwhelming, so I prefer narrower commands for exploring.

List the nodes:

```console
$ k get nodes
NAME       STATUS   ROLES                  AGE   VERSION
minikube   Ready    control-plane,master   62m   v1.23.3
```

One node, `minikube`, acting as both control plane and worker. For the full, verbose breakdown of a single node (capacity, conditions, allocated resources, events):

```console
$ k describe node minikube
```

### Listing the default addons

Before putting the cluster to work, I check which addons Minikube ships with and which are on by default:

```console
$ mk addons list
```

The list is long (Ingress, dashboard, metrics-server, registry, Istio, MetalLB, gVisor, and many more), but **only two are enabled out of the box** — both for storage:

| Addon | Status | Maintainer |
| --- | --- | --- |
| `default-storageclass` | **enabled** | kubernetes |
| `storage-provisioner` | **enabled** | google |

Everything else is disabled until I explicitly turn it on (I enable the `dashboard` addon in [section 4](#4-examining-the-cluster-with-the-dashboard)).

---

## 3. Doing work — deploy, expose, and call a service

> **Note:** if a VPN is running, it may interfere with image pulls — shutting it down temporarily helps.

The cluster isn't completely empty (DNS and other system services already run as pods in the `kube-system` namespace), but it's time to deploy something of my own.

Create a deployment from the `echoserver` image:

```console
$ k create deployment echo --image=k8s.gcr.io/e2e-test-images/echoserver:2.5
deployment.apps/echo created
```

Watch the pod come up — the `-w` flag streams a new line on every status change:

```console
$ k get po -w
NAME                    READY   STATUS              RESTARTS   AGE
echo-7fd7648898-6hh48   0/1     ContainerCreating   0          5s
echo-7fd7648898-6hh48   1/1     Running             0          6s
```

Expose the deployment as a `NodePort` service:

```console
$ k expose deployment echo --type=NodePort --port=8080
service/echo exposed
```

`NodePort` publishes the service on a port on the node — but **not** the `8080` the pod listens on. Kubernetes maps it to a high-numbered port. To reach the service I need the cluster IP plus that mapped port:

```console
$ mk ip
172.26.246.89

$ k get service echo -o jsonpath='{.spec.ports[0].nodePort}'
32649
```

Now I can call the echo service, which reflects back request details:

```console
$ curl http://172.26.246.89:32649/hi
Hostname: echo-7fd7648898-6hh48
...
Request Information:
        client_address=172.17.0.1
        method=GET
        real path=/hi
        request_scheme=http
        request_uri=http://172.26.246.89:8080/hi
...
```

Notice `request_uri` still shows port `8080` (the pod's port) while the `host` header shows `32649` (the NodePort) — a nice illustration of the port mapping. That's a full round trip: **a local cluster, a deployed service, and external access to it.**

---

## 4. Examining the cluster with the dashboard

Kubernetes ships a well-designed web UI — itself deployed as a service in a pod. It gives a high-level overview of the cluster and lets me drill into individual resources, view logs, and edit resource files. It's the go-to option when I want to inspect things visually and don't have desktop tools like **KUI** or **Lens** handy. Minikube provides it as an addon.

Enable it:

```console
$ mk addons enable dashboard
    ▪ Using image kubernetesui/dashboard:v2.3.1
    ▪ Using image kubernetesui/metrics-scraper:v1.0.7
  Some dashboard features require the metrics-server addon. To enable all features please run:
        minikube addons enable metrics-server
  The 'dashboard' addon is enabled
```

Launch it (Minikube opens the UI in the default browser via a local proxy):

```console
$ mk dashboard
  Verifying dashboard health ...
  Launching proxy ...
  Verifying proxy health ...
  Opening http://127.0.0.1:63200/.../proxy/ in your default browser...
```

The **Workloads** view shows Deployments, Replica Sets, and Pods (and can also display DaemonSets, StatefulSets, and Jobs — none of which exist in this cluster yet).

---

## 5. Tearing the cluster down

When I'm done experimenting, deleting the cluster removes the VM/container and all traces of it:

```console
$ mk delete
  Deleting "minikube" in docker ...
  Deleting container "minikube" ...
  Removing .../.minikube/machines/minikube ...
  Removed all traces of the "minikube" cluster.
```

**Recap of this section:** I created a local single-node cluster on Windows, explored it with `kubectl`, deployed and exposed a service, called it over HTTP, browsed it in the web dashboard, and finally tore it down. Next up: building a **multi-node** cluster.

---

## Reference

- **Book:** _Mastering Kubernetes_ — Gigi Sayfan
- **Minikube docs:** <https://minikube.sigs.k8s.io/docs/start/>
- **Chocolatey:** <https://chocolatey.org/>
