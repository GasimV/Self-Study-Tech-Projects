# Bare-Metal Lab — Creating a Cluster from Scratch

The cloud is the dominant way to run Kubernetes, but there are real reasons to run it on **bare metal** — from big, powerful data-center servers to Kubernetes at the edge. This lab is about building a cluster from scratch on physical infrastructure, a separate question from hosted vs. on-premise. If you already operate a fleet of servers, you're in the best position to decide whether this makes sense.

## Use cases for bare metal

Bare-metal clusters are genuinely hard to manage yourself. Some companies (like Platform9) offer commercial support, but the offerings are still maturing; a solid open-source option is **Kubespray**, which can deploy production-grade clusters on bare metal as well as AWS, GCE, Azure, and OpenStack. It's worth the effort when:

- **Price** — if you already run large-scale bare-metal infrastructure, hosting your own clusters can be far cheaper.
- **Low network latency** — when nodes need minimal latency between them, VM overhead may be too costly.
- **Regulatory requirements** — compliance rules may forbid using cloud providers.
- **Total hardware control** — you may have special needs that cloud options can't meet.

## Notes — bare metal vs. VMs vs. container nodes

A clarification I want to nail down: **bare metal isn't just for embedded/edge devices.** In production data centers it's often used for big, powerful servers. Embedded/edge is only *one* bare-metal case, not the main one.

The reason to pick bare metal is performance and control:

```text
Bare-metal node = maximum performance, direct hardware access, less virtualization overhead
```

Common bare-metal Kubernetes use cases:

```text
large data centers
high-performance workloads
GPU/AI workloads
telecom/edge systems
storage-heavy systems
on-prem private clouds
```

A big physical server can be **one Kubernetes node** — and that's not "wasting" it. Scheduling many pods onto a single node and dividing its CPU/RAM among workloads is exactly what Kubernetes is for:

```text
big physical server = 1 Kubernetes node
  ├── pod A
  ├── pod B
  ├── pod C
  └── pod D
```

You reach for **VMs** when you want stronger isolation, easier management, or to split one huge server into several smaller node-like units:

```text
big physical server
  ├── VM 1 = Kubernetes node
  ├── VM 2 = Kubernetes node
  └── VM 3 = Kubernetes node
```

The trade-off between the two models:

```text
Bare metal       = performance / control
VMs              = isolation / flexibility
Container nodes  = mostly local testing/CI, not typical production
```

Two things I keep straight here:

- **Blast radius.** One giant bare-metal node means that if the node fails, *everything* on it goes down, and scheduling/HA is coarser. Splitting it into several VM-nodes shrinks the blast radius — that's a big part of *why* people accept the VM overhead for isolation.
- **"Container nodes" ≠ how containers normally work in production.** With KinD/k3d the *node itself* is a container, which is why they suit local dev and CI. In normal production the **nodes** are bare metal or VMs, and the **containers are the pods** running on them — don't conflate the two.

## When should you consider it?

Building a cluster from scratch is complex — a Kubernetes cluster is not a simple beast, and much of the how-to material online goes stale quickly as the ecosystem moves. Go down this road only if you have the operational ability to **troubleshoot every layer of the stack**. Most problems will be networking-related, but filesystems, storage drivers, and version mismatches between Kubernetes, the container runtime, images, the OS, the kernel, and your addons can all bite you. Layering VMs on top of bare metal adds yet another level of complexity.

## Understanding the process

There's a lot to address when assembling a cluster by hand. The major concerns include:

- Implementing your own cloud-provider interface, or sidestepping it
- Choosing a networking model and how to implement it (CNI plugin, direct compile)
- Whether or not to use network policies
- Selecting images for the system components
- The security model and SSL certificates
- Admin credentials
- Templates for components like the API server, replication controller, and scheduler
- Cluster services: DNS, logging, monitoring, and a GUI

For a deeper understanding of what building a highly available cluster from scratch with **kubeadm** involves, the Kubernetes site's guide is the reference I'm following:
<https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/>

← Back to [K8s-Lab overview](README.md)
