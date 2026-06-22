# Bare-Metal Lab — Creating a Cluster from Scratch

The cloud is the dominant way to run Kubernetes, but there are real reasons to run it on **bare metal** — Kubernetes at the edge being a prime example. This lab is about building a cluster from scratch on physical infrastructure, a separate question from hosted vs. on-premise. If you already operate a fleet of servers, you're in the best position to decide whether this makes sense.

## Use cases for bare metal

Bare-metal clusters are genuinely hard to manage yourself. Some companies (like Platform9) offer commercial support, but the offerings are still maturing; a solid open-source option is **Kubespray**, which can deploy production-grade clusters on bare metal as well as AWS, GCE, Azure, and OpenStack. It's worth the effort when:

- **Price** — if you already run large-scale bare-metal infrastructure, hosting your own clusters can be far cheaper.
- **Low network latency** — when nodes need minimal latency between them, VM overhead may be too costly.
- **Regulatory requirements** — compliance rules may forbid using cloud providers.
- **Total hardware control** — you may have special needs that cloud options can't meet.

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
