# k3d Lab — Creating a Multi-Node Cluster

This lab builds a **multi-node** cluster with **k3d** from Rancher. I don't repeat the echo-server deployment here because it's identical to the KinD walkthrough (including reaching it through a proxy). The spoiler: creating clusters with k3d is even faster and friendlier than KinD.

## Quick introduction to k3s and k3d

Rancher built **k3s** as a lightweight Kubernetes distribution — the name is a play on "k8s" with five characters stripped away, reflecting how much it trims out. The idea is to drop the things most people don't need:

- Non-default features
- Legacy features
- Alpha features
- In-tree storage drivers
- In-tree cloud providers

It makes some bigger swaps too: it drops Docker in favor of **containerd** (though you can bring Docker back if you depend on it), and it stores cluster state in an **SQLite** database instead of etcd. Networking and DNS are handled by **Flannel** and **CoreDNS**, and a simplified installer takes care of SSL and certificate provisioning.

The result is remarkable: a **single binary under 40 MB** that runs in as little as **512 MB of memory**. Unlike Minikube and KinD, k3s is actually designed for **production** — its sweet spots are edge computing, IoT, and CI systems, and it's optimized for ARM devices.

So where does **k3d** fit in? It takes everything k3s offers, packages it inside Docker (much like KinD), and wraps it in a friendly CLI for managing clusters. Next I install k3d and try it out.

← Back to [K8s-Lab overview](README.md)
