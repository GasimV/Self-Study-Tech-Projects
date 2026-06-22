# K8s-Lab — Hands-On Kubernetes Journey

This folder is my hands-on lab log while working through **_Mastering Kubernetes_ by Gigi Sayfan**. The goal is to actually build, run, break, and inspect Kubernetes clusters on my own machine — not just read about them — and to keep a running record of the commands I ran, the output I got, and what each step actually did under the hood.

I'm following the book's progression, starting from a local single-node cluster and moving toward more advanced multi-node and production-style setups.

---

## Labs in this folder

| Lab | Tool | What it covers |
| --- | --- | --- |
| [Minikube Lab](Minikube-Lab.md) | Minikube | A local **single-node** cluster — install, start, explore, deploy & expose a service, dashboard, teardown. |
| [KinD Lab](KinD-Lab.md) | KinD | A **multi-node** cluster running Kubernetes-in-Docker; re-runs the echo-server deployment. |
| [k3d Lab](k3d-Lab.md) | k3d (k3s) | A **multi-node** cluster with Rancher's lightweight k3s, packaged by k3d. |
| [Bare-Metal Lab](Bare-Metal-Lab.md) | kubeadm | Building a cluster **from scratch** on physical infrastructure. |

---

## Comparing Minikube, KinD, and k3d

A quick reference for choosing between the three local options, based on the book's take plus my own runs:

| | Minikube | KinD | k3d |
| --- | --- | --- | --- |
| **Maturity / features** | Official, very mature, full-featured | Conformance-tested, conformant | Lightweight, very capable |
| **Nodes** | Single node only | Multi-node, **HA control plane** | Multi-node, multiple clusters |
| **Speed** | Slow to install & start (needs a VM*) | Much faster than Minikube | Fastest, most user-friendly |
| **State** | Persistent | **Ephemeral** (no persistent storage) | Easy stop/start without losing state |
| **Best for** | When you need a feature only it has | Contributing to / testing against Kubernetes itself | General local development (my default) |

\* On my machine Minikube auto-selected the **docker** driver, so it ran in a container rather than a VM — see the [Minikube Lab](Minikube-Lab.md) for how that changed the output.

**My takeaway:** **k3d** is the winner for everyday local work — lightning fast, multi-node, multi-cluster, and painless to stop and resume. Reach for **KinD** when you specifically need an HA multi-control-plane cluster or are testing against Kubernetes itself, and for **Minikube** only when it offers a feature the others don't.

- Minikube: <https://minikube.sigs.k8s.io/>
- KinD: <https://kind.sigs.k8s.io/>
- k3d: <https://k3d.io/>

---