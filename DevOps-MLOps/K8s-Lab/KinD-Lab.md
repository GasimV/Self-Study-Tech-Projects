# KinD Lab — Creating a Multi-Node Cluster

This lab moves from a single node to a **multi-node** cluster using **KinD**, and re-runs the same echo-server deployment I did on Minikube so I can compare the two. The short version up front: with KinD everything is faster and easier.

## Quick introduction to KinD

**KinD** stands for **Kubernetes in Docker**. It's a tool for spinning up *ephemeral* clusters — there's no persistent storage, so a cluster is meant to be created, used, and thrown away. It was originally built to run Kubernetes' own conformance tests, which is also why it's a CNCF-conformant installer: a tool used to certify Kubernetes had better behave like real Kubernetes. It supports Kubernetes 1.11 and later.

Under the hood, KinD uses **kubeadm** to bootstrap Docker containers as the cluster's nodes, so each "node" is a container rather than a VM. It ships as both a **library** (usable from your own code for testing) and a **CLI**, and it can stand up **highly available** clusters with multiple control-plane nodes.

KinD starts very fast, but it has trade-offs to keep in mind:

- **No persistent storage** — clusters are ephemeral by design.
- **Docker only** — no support for alternative container runtimes yet.

Next I install KinD and build the cluster.

← Back to [K8s-Lab overview](README.md)
