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
   - [SSH into the node](#ssh-into-the-node)
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

This pulls in both `minikube` and `kubernetes-cli` (which provides `kubectl`) and creates shims so both are on the `PATH`.

> **My actual run (June 2026):** the book uses Minikube v1.25.2, but Chocolatey installed the current versions for me — **Minikube v1.38.1** and **kubernetes-cli v1.36.2**. The flow is identical; only the version numbers differ.
>
> ```console
> PS C:\Users\Lenovo> choco install minikube -y
> Chocolatey v2.7.2
> Installing the following packages:
> minikube
>
> kubernetes-cli v1.36.2 [Approved]
> ...
>  ShimGen has successfully created a shim for kubectl.exe
>  The install of kubernetes-cli was successful.
>
> Minikube v1.38.1 [Approved]
> ...
>  ShimGen has successfully created a shim for minikube.exe
>  The install of Minikube was successful.
>
> Chocolatey installed 2/2 packages.
> ```

> **Console / shell notes:** On Windows you can drive Minikube from either **PowerShell** or **WSL** — both work, and some operations need an elevated (Administrator) shell. I use the official **Windows Terminal**, which can also be installed via Chocolatey:
>
> ```powershell
> choco install microsoft-windows-terminal --pre
> ```

### Setting up shortcuts and verifying the install

The shortcuts below are **optional**. They save keystrokes by aliasing `kubectl` to `k` and `minikube` to `mk`, but they aren't required to follow along.

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

> **Note on scope:** these go in your PowerShell `$profile` (or `.bashrc`), so they apply to **every** session for your user account — system-wide, not tied to this folder. Windows PowerShell (`powershell.exe`) and PowerShell 7 (`pwsh.exe`) use separate profile files, so set them in whichever shell you use.

> **Proceeding without the aliases:** I'm choosing to skip them and type the full commands instead. In that case, just substitute throughout the rest of this README:
>
> | Shortcut | Full command |
> | --- | --- |
> | `mk ...` | `minikube ...` |
> | `k ...` | `kubectl ...` |
>
> For example, `mk start` becomes `minikube start`, and `k get nodes` becomes `kubectl get nodes`.

Verify the install (using the full command, since I skipped the aliases):

```console
PS C:\Users\Lenovo> minikube version
minikube version: v1.38.1
commit: c93a4cb9311efc66b90d33ea03f75f2c4120e9b0
```

### Starting the cluster

Create the cluster with `minikube start`. Here's my actual run:

```console
PS C:\Users\Lenovo> minikube start
😄  minikube v1.38.1 on Microsoft Windows 11 Pro 25H2
✨  Automatically selected the docker driver. Other choices: hyperv, virtualbox, ssh
❗  Starting v1.39.0, minikube will default to "containerd" container runtime. See #21973 for more info.
📌  Using Docker Desktop driver with root privileges
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🚜  Pulling base image v0.0.50 ...
💾  Downloading Kubernetes v1.35.1 preload ...
    > preloaded-images-k8s-v18-v1...:  272.45 MiB / 272.45 MiB  100.00% 5.56 Mi
    > gcr.io/k8s-minikube/kicbase...:  519.58 MiB / 519.58 MiB  100.00% 6.18 Mi
🔥  Creating docker container (CPUs=2, Memory=16200MB) ...
🐳  Preparing Kubernetes v1.35.1 on Docker 29.2.1 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

#### What happened, line by line

1. **Version & OS detected** — `minikube v1.38.1 on Microsoft Windows 11 Pro 25H2`. Minikube reports itself and the host it's running on.
2. **Driver auto-selected** — it picked the **docker** driver automatically (other candidates on my machine were `hyperv`, `virtualbox`, `ssh`). This is a key difference from the book, which used a Hyper-V **VM**: my cluster runs inside a **Docker container** instead. Because Docker Desktop is available, that's the path of least resistance.
3. **Deprecation heads-up** — the `❗` line warns that from **v1.39.0** Minikube will default to the **containerd** runtime instead of Docker. Just informational; my run still used Docker.
4. **Driver privileges** — `Using Docker Desktop driver with root privileges`: the container runs with the access it needs to host a control plane.
5. **Creating the node** — `Starting "minikube" primary control-plane node in "minikube" cluster`. In single-node mode this one node is *both* control plane and worker.
6. **Pulling the base image** — `kicbase` (Kubernetes-in-Container base) is the image that provides the node's OS environment. Here it's `v0.0.50`.
7. **Downloading the Kubernetes preload** — a ~272 MiB bundle of pre-pulled images for **Kubernetes v1.35.1**, plus the ~520 MiB `kicbase` image. Preloading these speeds up startup and avoids pulling each component image separately. (First run only — they're cached afterward.)
8. **Creating the container** — the Docker container is provisioned with **CPUs=2, Memory=16200 MB**. Note there's **no "Creating VM"/"Downloading VM boot image" step** here, unlike the book's Hyper-V run — the container replaces the VM.
9. **Preparing Kubernetes** — `Kubernetes v1.35.1 on Docker 29.2.1`: bootstrapping the control plane (this is where certificates, the API server, etcd, scheduler, controller-manager, and kubelet get set up — kubeadm does the heavy lifting inside the node).
10. **Configuring CNI** — `bridge CNI`: installs the pod networking plugin so pods can get IPs and talk to each other.
11. **Verifying components** — Minikube health-checks the cluster and pulls the `storage-provisioner:v5` image.
12. **Enabling addons** — the same two storage addons as the book come on by default: `storage-provisioner` and `default-storageclass`.
13. **Done** — `kubectl is now configured to use "minikube" cluster and "default" namespace`. Minikube wrote a context into my kubeconfig so `kubectl` points at this cluster out of the box.

In short: even the **default** setup does a lot of work — selecting a driver, pulling images, provisioning the node, bootstrapping every control-plane component, wiring up networking, and configuring `kubectl`. It's all customizable too — `minikube start -h` lists flags for the driver, CPU/memory, Kubernetes version, container runtime, and more.

> **Versions in my run vs. the book:** docker driver (container) instead of Hyper-V (VM); Kubernetes **v1.35.1** instead of v1.23.3; Docker **29.2.1** instead of 20.10.12; **bridge CNI** explicitly configured. The shape of the process is the same — the moving parts are just newer.

### Checking status, stopping, and restarting

Check cluster status:

```console
PS C:\Users\Lenovo> minikube status
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

Everything reports `Running` / `Configured`, so the cluster is healthy.

Stop the cluster:

```console
PS C:\Users\Lenovo> minikube stop
✋  Stopping node "minikube"  ...
🛑  Powering off "minikube" via SSH ...
🛑  1 node stopped.
```

#### Timing a restart — `time` vs. PowerShell

The book measures the restart with the Unix shell built-in `time`. That **doesn't exist in PowerShell**, so it fails:

```console
PS C:\Users\Lenovo> time minikube start
time : The term 'time' is not recognized as the name of a cmdlet, function, script file, or operable program. ...
    + FullyQualifiedErrorId : CommandNotFoundException
```

PowerShell's equivalent is the **`Measure-Command`** cmdlet, which runs a script block and reports how long it took:

```console
PS C:\Users\Lenovo> Measure-Command { minikube start }

Days              : 0
Hours             : 0
Minutes           : 0
Seconds           : 43
Milliseconds      : 377
...
TotalSeconds      : 43.3777969
```

A warm restart took **~43 seconds** for me. It reuses the existing profile and container/VM, so it's noticeably faster than the first cold start (which had to download images and provision the node).

> **Gotcha:** `Measure-Command` swallows the wrapped command's normal output — it returns only the timing object, so you won't see Minikube's usual `😄 … 🏄 Done!` lines. If you want both the output *and* the timing, run `minikube start` on its own, or use `Measure-Command { minikube start | Out-Default }`.

### What Minikube does behind the scenes

The reason `minikube start` is worth appreciating is that it automates everything you'd otherwise have to do by hand when building a cluster from scratch. In my environment (the **docker** driver), behind the curtain it:

1. Pulled the **`kicbase` base image** and created a **Docker container** to act as the node (the book's Hyper-V driver spins up a **VM** here instead).
2. Created **certificates** for the local machine and the node.
3. **Downloaded** the required images (the Kubernetes preload bundle + component images).
4. Set up **networking** between the host and the node, and configured the **bridge CNI** for pod networking.
5. Ran the local **Kubernetes cluster** inside the container.
6. **Configured** the cluster.
7. Started all the **control plane** components (API server, etcd, scheduler, controller-manager).
8. Configured the **kubelet**.
9. Enabled **addons** (for storage).
10. Configured **`kubectl`** to talk to the cluster.

> **Driver note:** step 1 is the main thing that changes with the driver. With **docker** the node is a container; with **hyperv** (the book) or **virtualbox** it's a full VM, which is why the book's output also shows a "Downloading VM boot image" / "Creating VM" step that my run doesn't have. Everything from step 2 onward is the same regardless of driver.

Keeping this list in mind is useful — every one of these steps reappears (manually) when provisioning a cluster the hard way later in the book.

---

## 2. Checking out the cluster

With a cluster running, the next thing I do is poke around inside it.

### SSH into the node

Minikube runs the cluster inside the node — a **Docker container** with my docker driver (the book's Hyper-V driver uses a VM instead) — and I can drop into a shell on it directly:

```console
PS C:\Users\Lenovo> minikube ssh
Linux minikube 6.6.114.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Mon Dec  1 20:46:23 UTC 2025 x86_64
...
docker@minikube:~$ uname -a
Linux minikube 6.6.114.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Mon Dec  1 20:46:23 UTC 2025 x86_64 GNU/Linux
```

A few things to notice in my output versus the book's:

- The shell prompt is `docker@minikube` — I'm logged in as the `docker` user inside the node, and the OS banner identifies it as **Debian GNU/Linux**.
- The kernel is `6.6.114.1-microsoft-standard-WSL2`. That `-WSL2` tag is a giveaway that the container is running on Docker Desktop's WSL2 backend — so the node shares the **WSL2 Linux kernel** of my Windows host rather than booting its own kernel like a VM would. (The book's Hyper-V run shows a plain `4.19.202` kernel from a dedicated VM.)

`uname -a` confirms I'm on the Linux node that actually hosts the cluster. To get back to the host, disconnect with **Ctrl+D** or `logout`.

From here on I lean on **`kubectl`** — the Swiss Army knife of Kubernetes, and the one tool that works against every cluster regardless of how it was provisioned.

### Cluster info and nodes with kubectl

Check that the control plane is healthy:

```console
PS C:\Users\Lenovo> kubectl cluster-info
Kubernetes control plane is running at https://127.0.0.1:51464
CoreDNS is running at https://127.0.0.1:51464/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

The control plane reports healthy. Note the API server endpoint: `https://127.0.0.1:51464`. With the **docker driver** the node is a container, and Docker maps the API server out to a random high port on `127.0.0.1` of my host — that's why it's localhost here, rather than the VM's LAN IP (`172.x.x.x`) the book shows.

`kubectl cluster-info dump` gives a full JSON dump of every object in the cluster. It's exhaustive — my run starts with a `NodeList` describing the `minikube` node (labels, the `podCIDR` of `10.244.0.0/24`, etc.) and walks through every resource type, ending with empty `ReplicaSetList` / `PodList` for the default namespace (nothing of mine deployed yet):

```console
PS C:\Users\Lenovo> kubectl cluster-info dump
{
    "kind": "NodeList",
    ...
    "items": [
        { "metadata": { "name": "minikube", ... },
          "spec": { "podCIDR": "10.244.0.0/24", "podCIDRs": ["10.244.0.0/24"] } }
    ]
}
... (every resource type) ...
{ "kind": "PodList", ..., "items": null }
```

It's useful for deep debugging but overwhelming for browsing, so I prefer narrower commands.

List the nodes:

```console
PS C:\Users\Lenovo> kubectl get nodes
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   29m   v1.35.1
```

One node, `minikube`, `Ready`, running Kubernetes **v1.35.1**. Its only role is `control-plane` (newer Kubernetes dropped the legacy `master` role label that the book's v1.23 output still shows as `control-plane,master`). In single-node mode this node is also schedulable for workloads.

For the full breakdown of a node — capacity, conditions, allocated resources, and events — use `describe`:

```console
PS C:\Users\Lenovo> kubectl describe node minikube
Name:               minikube
Roles:              control-plane
...
Conditions:
  Type             Status   Reason                        Message
  MemoryPressure   False    KubeletHasSufficientMemory    kubelet has sufficient memory available
  DiskPressure     False    KubeletHasNoDiskPressure      kubelet has no disk pressure
  PIDPressure      False    KubeletHasSufficientPID       kubelet has sufficient PID available
  Ready            True     KubeletReady                  kubelet is posting ready status
Addresses:
  InternalIP:  192.168.49.2
  Hostname:    minikube
Capacity:
  cpu:                24
  memory:             32571408Ki
  pods:               110
System Info:
  Kernel Version:             6.6.114.1-microsoft-standard-WSL2
  OS Image:                   Debian GNU/Linux 12 (bookworm)
  Container Runtime Version:  docker://29.2.1
  Kubelet Version:            v1.35.1
PodCIDR:                      10.244.0.0/24
Non-terminated Pods:          (7 in total)
  Namespace     Name                                CPU Requests  Memory Requests  Age
  kube-system   coredns-7d764666f9-jzvpl            100m          70Mi             29m
  kube-system   etcd-minikube                       100m          100Mi            29m
  kube-system   kube-apiserver-minikube             250m          0                29m
  kube-system   kube-controller-manager-minikube    200m          0                29m
  kube-system   kube-proxy-nnrwp                    0             0                29m
  kube-system   kube-scheduler-minikube             100m          0                29m
  kube-system   storage-provisioner                 0             0                29m
```

A few things worth pulling out of this (trimmed) dump:

- **Conditions** — all the pressure conditions are `False` and `Ready` is `True`: the node is healthy with enough memory, disk, and PIDs.
- **`InternalIP: 192.168.49.2`** — this is the node's address on minikube's internal Docker network, distinct from the `127.0.0.1` the host uses to reach the API server.
- **Capacity** — the container can see my whole machine: `cpu: 24`, ~32 GiB memory, and a default cap of `110` pods.
- **System Info** confirms the environment: **Debian 12 (bookworm)**, WSL2 kernel, **Docker 29.2.1** as the container runtime, kubelet **v1.35.1**.
- **Non-terminated Pods (7)** — the cluster isn't really "empty." The control-plane components themselves run as pods in `kube-system`: `etcd`, `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, `kube-proxy`, plus `coredns` (DNS) and `storage-provisioner` (from the default addon).

### Listing the default addons

Before putting the cluster to work, I check which addons Minikube ships with and which are on by default:

```console
PS C:\Users\Lenovo> minikube addons list
┌─────────────────────────────┬──────────┬────────────┬────────────────────────────┐
│         ADDON NAME          │ PROFILE  │   STATUS   │         MAINTAINER         │
├─────────────────────────────┼──────────┼────────────┼────────────────────────────┤
│ dashboard                   │ minikube │ disabled   │ Kubernetes                 │
│ default-storageclass        │ minikube │ enabled ✅ │ Kubernetes                 │
│ ingress                     │ minikube │ disabled   │ Kubernetes                 │
│ metrics-server              │ minikube │ disabled   │ Kubernetes                 │
│ storage-provisioner         │ minikube │ enabled ✅ │ minikube                   │
│ ... (38 addons in total) ...                                                     │
└─────────────────────────────┴──────────┴────────────┴────────────────────────────┘
```

The list is long — **38 addons** in my v1.38.1 run (more than the book's, with newer entries like `headlamp`, `kubetail`, `inspektor-gadget`, `volcano`, `yakd`, and `amd-gpu-device-plugin`). But just like the book, **only two are enabled out of the box** (marked ✅), both for storage:

| Addon | Status | Maintainer |
| --- | --- | --- |
| `default-storageclass` | **enabled ✅** | Kubernetes |
| `storage-provisioner` | **enabled ✅** | minikube |

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
