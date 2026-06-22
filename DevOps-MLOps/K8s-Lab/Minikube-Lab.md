# Minikube Lab — Creating a Single-Node Cluster

This lab covers building a local **single-node** Kubernetes cluster with Minikube and putting it through its paces. A local cluster is the fastest way to get quick edit → test → deploy → debug cycles on my own machine, and a safe sandbox for experimenting without touching a shared environment or running up cloud bills.

Kubernetes usually runs on Linux in production, but plenty of development happens on Windows and macOS — I'm on Windows here, and the differences from a Linux install turn out to be minimal. By the end I've installed Minikube, started a cluster, explored it with `kubectl`, deployed and exposed a service, viewed it in the dashboard, and torn it back down.

← Back to [K8s-Lab overview](README.md)

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

#### Aside: do I need to turn on VirtualBox before selecting it as the driver?

**No — I don't need to open or "turn on" VirtualBox first.** It just needs to be **installed correctly**; Minikube creates and starts the VM itself:

```powershell
minikube start --driver=virtualbox
```

The official Minikube docs list the VirtualBox requirement and use exactly this command.

One catch: I already have a `minikube` cluster on the **docker** driver. To switch cleanly to VirtualBox, delete the current one first:

```powershell
minikube delete
minikube start --driver=virtualbox
```

Or keep both by creating a separate profile:

```powershell
minikube start -p minikube-vbox --driver=virtualbox
```

**My recommendation:** stay on the **docker** driver unless I specifically want to compare VM behavior — it's faster and simpler on this setup. VirtualBox is mainly useful when I want to see Minikube as a real **VM node** rather than a Docker-container node.

> Reference: [virtualbox | minikube](https://minikube.sigs.k8s.io/docs/drivers/virtualbox/)

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

[↑ Back to Contents](#table-of-contents)

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

[↑ Back to Contents](#table-of-contents)

---

## 3. Doing work — deploy, expose, and call a service

> **Note:** if a VPN is running, it may interfere with image pulls — shutting it down temporarily helps.

The cluster isn't completely empty (DNS and other system services already run as pods in the `kube-system` namespace), but it's time to deploy something of my own.

Create a deployment from the `echoserver` image:

```console
PS C:\Users\Lenovo> kubectl create deployment echo --image=k8s.gcr.io/e2e-test-images/echoserver:2.5
deployment.apps/echo created
```

> If I run it twice I get `error: failed to create deployment: deployments.apps "echo" already exists` — harmless, it just means the deployment is already there.

Watch the pod come up — the `-w` flag streams a new line on every status change (Ctrl+C to stop watching):

```console
PS C:\Users\Lenovo> kubectl get po -w
NAME                    READY   STATUS              RESTARTS   AGE
echo-679d8d5747-cv924   0/1     ContainerCreating   0          5s
echo-679d8d5747-cv924   1/1     Running             0          6s
```

Expose the deployment as a `NodePort` service:

```console
PS C:\Users\Lenovo> kubectl expose deployment echo --type=NodePort --port=8080
service/echo exposed
```

`NodePort` publishes the service on a port on the node — but **not** the `8080` the pod listens on. Kubernetes maps it to a high-numbered port. So I grab the node IP and the mapped port:

```console
PS C:\Users\Lenovo> minikube ip
192.168.49.2

PS C:\Users\Lenovo> kubectl get service echo -o jsonpath='{.spec.ports[0].nodePort}'
31325
```

### The NodePort isn't reachable directly (docker driver gotcha)

The book curls `http://<node-ip>:<nodePort>` and it just works — because its node is a Hyper-V **VM** with a routable LAN IP. On my **docker driver** it fails:

```console
PS C:\Users\Lenovo> curl http://192.168.49.2:31325/hi
curl : Unable to connect to the remote server
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-WebRequest], WebException
```

**Why:** `192.168.49.2` is the node's address on Minikube's *internal Docker network*. With the docker driver on Windows that network lives inside the WSL2 VM, so the IP isn't routable from my Windows host — the connection never lands. (It's the same reason `kubectl cluster-info` earlier showed the API server on `127.0.0.1:<mapped-port>` instead of the node IP.) On Linux, where Docker runs natively, the direct curl *would* work.

**The fix:** let Minikube open a tunnel from the host to the service with `minikube service`. The `--url` form prints a reachable `127.0.0.1` URL instead of launching a browser:

```console
PS C:\Users\Lenovo> minikube service echo --url
http://127.0.0.1:57067
❗  Because you are using a Docker driver on windows, the terminal needs to be open to run it.
```

That `❗` note is important: with the docker driver the URL is a live tunnel that **only exists while this command keeps running**. So I leave this terminal open and curl the printed URL from a **second** terminal.

#### Second gotcha: PowerShell's `curl` triggers a security prompt

In PowerShell, `curl` is an **alias for `Invoke-WebRequest`** (not the real curl). When I call it, instead of fetching the body it stops with a *"Script Execution Risk"* prompt:

```console
PS C:\Users\Lenovo> curl http://127.0.0.1:57067/hi

Security Warning: Script Execution Risk
Invoke-WebRequest parses the content of the web page. Script code in the web page might be run when the page is parsed.
    RECOMMENDED ACTION:
    Use the -UseBasicParsing switch to avoid script code execution.
    Do you want to continue?
[Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "N"):
```

`Invoke-WebRequest` tries to parse the response as HTML through the legacy Internet Explorer engine; when that can't initialize it prompts. It's not a real risk here — but it blocks the request. Answering `N` (the default) cancels it outright:

```console
[Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "N"): N
curl : Operation cancelled due to security concerns. Use -UseBasicParsing parameter for safe HTML parsing without
script execution.
```

Three ways around it (all run in the second terminal while the tunnel stays open):

```powershell
curl.exe http://127.0.0.1:57067/hi                       # real curl — the .exe bypasses the alias (cleanest)
Invoke-RestMethod http://127.0.0.1:57067/hi              # returns the body directly
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:57067/hi   # skips HTML parsing, no prompt
```

Using real curl, the echo server finally answers:

```console
PS C:\Users\Lenovo> curl.exe http://127.0.0.1:57067/hi

Hostname: echo-679d8d5747-cv924

Pod Information:
        -no pod information available-

Server values:
        server_version=nginx: 1.14.2 - lua: 10015

Request Information:
        client_address=10.244.0.1
        method=GET
        real path=/hi
        query=
        request_version=1.1
        request_scheme=http
        request_uri=http://127.0.0.1:8080/hi

Request Headers:
        accept=*/*
        host=127.0.0.1:57067
        user-agent=curl/8.19.0

Request Body:
        -no body in request-
```

🎉 **Success — the full round trip works.** A couple of things to note:

- `minikube service echo` (without `--url`) does the same tunnelling but opens the service in my default browser.
- `request_uri` still shows port `8080` (the pod's port) while I connected on the tunnel port — a nice illustration of how the request is mapped through. That's a full round trip: **a local cluster, a deployed service, and external access to it.**

[↑ Back to Contents](#table-of-contents)

---

## 4. Examining the cluster with the dashboard

Kubernetes ships a well-designed web UI — itself deployed as a service in a pod. It gives a high-level overview of the cluster and lets me drill into individual resources, view logs, and edit resource files. It's the go-to option when I want to inspect things visually and don't have desktop tools like **KUI** or **Lens** handy. Minikube provides it as an addon.

Enable it:

```console
PS C:\Users\Lenovo> minikube addons enable dashboard
💡  dashboard is an addon maintained by Kubernetes. For any concerns contact minikube on GitHub.
    ▪ Using image docker.io/kubernetesui/dashboard:v2.7.0
    ▪ Using image docker.io/kubernetesui/metrics-scraper:v1.0.8
💡  Some dashboard features require the metrics-server addon. To enable all features please run:

        minikube addons enable metrics-server

🌟  The 'dashboard' addon is enabled
```

The `metrics-server` hint is optional — without it the dashboard still works, it just won't show CPU/memory graphs. Launch the dashboard (Minikube starts a local proxy and opens the UI in the default browser):

```console
PS C:\Users\Lenovo> minikube dashboard
🤔  Verifying dashboard health ...
🚀  Launching proxy ...
🤔  Verifying proxy health ...
🎉  Opening http://127.0.0.1:61581/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/ in your default browser...
```

Like the `minikube service` tunnel from section 3, this proxy lives only while the `minikube dashboard` command keeps running — closing that terminal closes the dashboard. The URL goes through `127.0.0.1`, the same host-to-cluster proxying pattern the docker driver relies on.

The **Workloads** view shows Deployments, Replica Sets, and Pods (and can also display DaemonSets, StatefulSets, and Jobs — none of which exist in this cluster yet). Here it is showing the `echo` deployment I created in section 3:

![Workloads view of the Kubernetes dashboard showing the echo deployment](../assets/Workloads%20dashboard.png)

[↑ Back to Contents](#table-of-contents)

---

## 5. Tearing the cluster down

When I'm done experimenting, `minikube delete` removes the cluster — with the docker driver that means deleting the node **container** and the cluster's machine state:

```console
PS C:\Users\Lenovo> minikube delete
🔥  Deleting "minikube" in docker ...
🔥  Deleting container "minikube" ...
🔥  Removing C:\Users\Lenovo\.minikube\machines\minikube ...
💀  Removed all traces of the "minikube" cluster.
```

### What got removed vs. what stayed

Checking Docker Desktop afterward, I noticed the cleanup wasn't total:

- **Containers** — the `minikube` node container is **gone**. The Containers tab is empty again.
- **Images** — the two `gcr.io/k8s-minikube/kicbase` images (the `v0.0.50` tag and a `<none>` one, ~1.93 GB each) are **still there**.

This is **intentional**, not a bug. `minikube delete` removes the *cluster* (the container and its machine directory), but it deliberately leaves the cached base images behind so that the **next** `minikube start` is fast — it can reuse `kicbase` instead of re-downloading ~500 MB. The message says "Removed all traces of the cluster," and that's accurate: the images aren't part of the cluster, they're a shared cache.

If I want to reclaim that disk space too, I can remove the images explicitly:

```powershell
# Purge minikube's own cached files (~/.minikube) along with the cluster
minikube delete --all --purge

# …and/or drop the leftover Docker images directly
docker rmi gcr.io/k8s-minikube/kicbase:v0.0.50
docker image prune        # clears dangling <none> images
```

> Trade-off: deleting the images frees ~2 GB now, but the next `minikube start` pays the full download cost again. If I plan to spin the cluster back up, leaving them cached is the right call.

### Verifying the cleanup from the terminal

I deleted the two `kicbase` images from the Docker Desktop GUI (the "delete forever" button), then confirmed from the terminal that nothing is left:

```console
PS C:\Users\Lenovo> docker images gcr.io/k8s-minikube/kicbase
IMAGE   ID   DISK USAGE   CONTENT SIZE   EXTRA
                                                    # (header only — no images)

PS C:\Users\Lenovo> docker images -a                # nothing, including dangling layers
PS C:\Users\Lenovo> docker images -f "dangling=true"  # no orphaned <none> images

PS C:\Users\Lenovo> docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          0         0         0B        0B
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     0         0         0B        0B
```

`docker system df` is the definitive check — **Images** at `0B` / `0B` reclaimable means Docker is holding no image data. Running `docker system prune -a --volumes` afterward confirmed it: `Total reclaimed space: 0B` (nothing left to free).

### Gotcha: my C: drive free space didn't go up

After all that, I noticed **C: free space hadn't increased at all.** This is expected on Windows/WSL2 and **won't fix itself** — not after waiting, and not after a normal reboot.

**Why:** Docker Desktop stores everything inside a WSL2 **virtual disk** file:

```text
C:\Users\Lenovo\AppData\Local\Docker\wsl\disk\docker_data.vhdx
```

That `.vhdx` file only ever **grows**. Deleting images frees space *inside* the virtual disk (which is exactly what `docker system df = 0B` reflects), but the file on the Windows host keeps its already-allocated size. Windows can't reclaim those gigabytes until the virtual disk is **compacted**. So `docker system df` showing `0B` is the correct signal that Docker is clean — the host-side reclaim is a separate, manual step.

**Reclaiming the space on C:** quit Docker Desktop, shut down the WSL backend, then either make the disk auto-shrinking or compact it directly.

```powershell
# Always start by stopping WSL (quit Docker Desktop first)
wsl --shutdown
```

Option A — mark the disk **sparse** so it can release freed space (simplest; Windows 11 / recent WSL):

```powershell
wsl --manage docker-desktop --set-sparse true
```

> **Correction — only one distro on modern Docker Desktop.** Older guides tell you to also run this against a second distro, `docker-desktop-data`, and sometimes to add an `--allow-unsafe` flag. Neither applies to my setup:
>
> - I have a **single** distro. Verified with `wsl --list --verbose`:
>   ```text
>   NAME              STATE      VERSION
>   * docker-desktop    Stopped    2
>   ```
>   The two-distro layout (`docker-desktop` + `docker-desktop-data`) was the *old* Docker Desktop design; recent versions (~4.30+, 2024) consolidated to just `docker-desktop`, with data in `...\Docker\wsl\disk\docker_data.vhdx`. Running the command against `docker-desktop-data` here just errors with "distribution not found" — so I skip it.
> - **`--allow-unsafe` is not a documented `--set-sparse` flag.** The official syntax is `wsl --manage <Distro> --set-sparse <true|false>`. If WSL refuses the operation, the real fix is making sure the distro is fully stopped (`wsl --shutdown`), not adding an undocumented flag.
> - Sparse mode lets the disk *release* freed blocks, but it's not a guaranteed background shrink. For an immediate, deterministic reclaim, use Option B below.

Option B — **compact** the .vhdx directly with `diskpart` (works on any version):

```text
diskpart
  select vdisk file="C:\Users\Lenovo\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
  attach vdisk readonly
  compact vdisk
  detach vdisk
  exit
```

#### Option B, command by command

A dynamically expanding VHDX grows as images/containers/volumes are created, but doesn't always shrink when you delete them. `compact vdisk` rewrites the file to drop the freed empty space — here's what each line does:

| Command | What it does |
| --- | --- |
| `wsl --shutdown` | Stops WSL completely so Docker's virtual disk isn't in use (Microsoft's WSL disk steps also begin here). |
| `diskpart` | Opens Windows' disk-management command tool. |
| `select vdisk file="...docker_data.vhdx"` | Tells DiskPart *this* is the virtual disk file to work on. |
| `attach vdisk readonly` | Mounts the VHDX **read-only** — compaction is safest when nothing can write to the disk. |
| `compact vdisk` | Actually shrinks the file by removing unused empty space inside the virtual disk. |
| `detach vdisk` | Unmounts the VHDX cleanly. |
| `exit` | Leaves DiskPart. |

The flow in one picture:

```text
Docker deletes data inside the VHDX
→ the VHDX file may still stay large on C:
→ DiskPart `compact vdisk` rewrites/shrinks it
→ Windows gets the free space back
```

Use Option B when you want an **immediate, manual reclaim** — just make sure Docker Desktop is fully quit and `wsl --shutdown` has run first.

When it works, the DiskPart session confirms each step — this is my actual run:

```console
DISKPART> select vdisk file="C:\Users\Lenovo\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
DiskPart successfully selected the virtual disk file.
DISKPART> attach vdisk readonly
DiskPart successfully attached the virtual disk file.
DISKPART> compact vdisk
  100 percent completed
DiskPart successfully compacted the virtual disk file.
DISKPART> detach vdisk
DiskPart successfully detached the virtual disk file.
DISKPART> exit
```

> **Pitfall — run these *inside* the `DISKPART>` prompt, not in PowerShell.** `select`, `attach`, `compact`, and `detach` are DiskPart sub-commands; they only exist after you've launched `diskpart`. If they're entered at a normal `PS>` prompt (e.g. by pasting the block a second time after `exit`), PowerShell misinterprets them — harmlessly but confusingly:
> - `select` → resolves to the `Select-Object` alias → parameter error
> - `attach` / `detach` → "not recognized as the name of a cmdlet"
> - `compact` → runs **`compact.exe`**, the unrelated NTFS file-compression tool, which just lists the current folder and does nothing to the VHDX
>
> None of that harms anything — but the only run that matters is the one under `DISKPART>`. The `DiskPart successfully compacted...` line is the proof it worked.

After either option, the `.vhdx` shrinks and the freed gigabytes show up as C: free space again. In my case, C: free space went from **772 GB to 775 GB** right after the compaction — about **3 GB reclaimed**, which matches the ~2 GB of `kicbase` images plus assorted container/layer overhead that the cluster had allocated inside the virtual disk.

> **Takeaway:** `docker system df = 0B` proves *Docker* is clean; recovering disk on the *Windows host* needs the extra `wsl --shutdown` + sparse/compact step. It never happens automatically.

**Recap of this section:** I created a local single-node cluster on Windows, explored it with `kubectl`, deployed and exposed a service, called it over HTTP, browsed it in the web dashboard, and finally tore it down — noting that the cached `kicbase` images survive deletion by design. Next up: building a **multi-node** cluster with [KinD](KinD-Lab.md).

[↑ Back to Contents](#table-of-contents)

---

## Reference

- **Book:** _Mastering Kubernetes_ — Gigi Sayfan
- **Minikube docs:** <https://minikube.sigs.k8s.io/docs/start/>
- **Chocolatey:** <https://chocolatey.org/>
