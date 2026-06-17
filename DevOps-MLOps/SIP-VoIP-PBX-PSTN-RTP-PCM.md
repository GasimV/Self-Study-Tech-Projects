# SIP, VoIP, PBX, PSTN, ATS, RTP, and PCM

These technologies sit at different layers of voice communication. Some describe
the network, some describe call control, and some describe how voice is encoded
and transported.

## Contents

- [Quick Summary](#quick-summary)
- [PSTN](#pstn)
- [ATS](#ats)
- [PBX](#pbx)
- [VoIP](#voip)
- [SIP Trunk Provider](#sip-trunk-provider)
- [SIP](#sip)
- [RTP](#rtp)
- [PCM](#pcm)
- [How They Work Together](#how-they-work-together)
- [Example Business Call Flow](#example-business-call-flow)
- [Layer Relationship](#layer-relationship)

## Quick Summary

| Term | Full name | Layer | Main role |
| --- | --- | --- | --- |
| PSTN | Public Switched Telephone Network | Legacy carrier network | Traditional phone network for landline and carrier voice calls |
| ATS | Automatic Telephone Exchange | Telephone switching system | Connects dialed numbers to receiving lines inside the PSTN or a private phone system |
| PBX | Private Branch Exchange | Business phone system | Routes calls inside an organization and connects them to external networks |
| VoIP | Voice over IP | Voice architecture | Sends voice calls over IP networks instead of dedicated telephone circuits |
| SIP trunk provider | SIP trunking carrier | Carrier bridge | Connects an IP PBX to external landline and mobile networks |
| SIP | Session Initiation Protocol | Signaling | Starts, manages, and ends VoIP sessions |
| RTP | Real-time Transport Protocol | Media transport | Carries live audio or video packets after a call is established |
| PCM | Pulse Code Modulation | Audio encoding | Converts analog voice into digital audio samples |

[Back to contents](#contents)

## PSTN

PSTN is the traditional public telephone network.

### What It Is

The PSTN is a carrier-operated, circuit-switched telephone network. Historically,
it used copper lines and physical switching equipment to create a dedicated path
between callers.

### Role

- Connects traditional landline numbers.
- Provides access to national and international telephone numbering plans.
- Still acts as the external phone network for many business systems.

### Key Characteristics

- Uses carrier-controlled infrastructure.
- Originally designed for analog voice.
- Provides high reliability, emergency calling support, and telephone number
  routing.
- Requires gateways or carrier interconnects when connecting to IP-based VoIP
  systems.

[Back to contents](#contents)

## ATS

ATS stands for Automatic Telephone Exchange. It is the switching system that
automatically connects one telephone line, number, or extension to another.

### What It Is

An ATS is the call-switching equipment or service that receives dialed digits,
finds the destination, and establishes the connection. In traditional public
telephony, an ATS is part of the PSTN. In an organization, the same idea is
usually called a PBX or PABX.

The simple distinction is:

- PSTN is the wider public telephone network.
- ATS is the switching system inside that network, or inside a private
  organization, that directs calls.

### Main Responsibilities

- Receives dialed digits or signaling information.
- Identifies the destination line, number, route, or extension.
- Reserves or selects the path needed for the call.
- Connects the caller to the recipient.
- Releases the connection when the call ends.

### ATS Types

| Type | Description | Typical use |
| --- | --- | --- |
| Public local ATS | Carrier-operated exchange serving a town, district, or neighborhood | Connects local landline subscribers and routes calls to other exchanges |
| Private/local ATS | Organization-owned exchange, commonly called PBX or PABX | Office, factory, hotel, school, or campus extensions |
| Virtual ATS | Cloud-hosted exchange, usually based on VoIP and SIP | Hosted business phone systems without on-premises switching hardware |

### ATS vs PSTN

PSTN is the network. ATS is one of the switching systems that makes the network
usable.

```text
PSTN = the road network
ATS  = the exchange/router that decides where a call goes
```

When a landline user dials a number, the local ATS receives the digits, selects
the route, and connects the caller through the PSTN to the destination exchange
or line.

[Back to contents](#contents)

## PBX

PBX stands for Private Branch Exchange. It is the phone system used by an
organization to manage internal and external calls.

### What It Is

A PBX is a private call-routing system. It connects company extensions to each
other and connects those extensions to external phone networks such as the PSTN
or SIP trunks.

### Main Responsibilities

- Routes calls between internal extensions.
- Sends outbound calls to carriers.
- Receives inbound calls and forwards them to the correct user, queue, IVR, or
  department.
- Provides business calling features such as hold, transfer, voicemail, call
  recording, call queues, ring groups, and auto attendants.

### PBX Types

| Type | Description | Typical connectivity |
| --- | --- | --- |
| Traditional PBX | Hardware-based office phone system | Analog lines, PRI, or PSTN circuits |
| IP PBX | PBX that uses IP networking and VoIP phones | SIP phones, SIP trunks, LAN/WAN |
| Hosted PBX | Cloud-hosted PBX managed by a provider | Internet connection and SIP/WebRTC clients |
| Hybrid PBX | Mix of legacy telephony and IP voice | PSTN, PRI, SIP trunks, analog adapters |

### PBX in a VoIP Environment

In a VoIP setup, the PBX usually acts as the central call-control system. It may
register SIP phones, route calls, enforce dial plans, connect to SIP trunks, and
send calls to media services such as recording, IVR, or conferencing.

Example:

```text
User SIP phone -> IP PBX -> SIP trunk provider -> PSTN/mobile network
```

### PBX Examples: 3CX and Asterisk

3CX and Asterisk are PBX systems. They can manage internal phones, extensions,
voicemail, call queues, IVRs, and extension-to-extension calls. By themselves,
however, they are private phone systems. They do not automatically have access to
the global telephone network.

For external calls to landline or mobile numbers, the PBX needs a carrier
connection. In modern VoIP deployments, that carrier connection is usually a SIP
trunk provider.

[Back to contents](#contents)

## VoIP

VoIP stands for Voice over IP. It is the overall method of carrying voice calls
over packet-based IP networks.

### What It Is

VoIP converts voice into digital data, splits it into packets, and sends those
packets across an IP network such as a LAN, WAN, private network, or the
internet.

### Core Components

- Endpoint: A SIP desk phone, softphone, browser client, mobile app, or voice
  gateway.
- Signaling protocol: Usually SIP, used to establish and control the call.
- Media protocol: Usually RTP or SRTP, used to carry the live audio stream.
- Codec: Encodes and compresses the audio, such as G.711, G.729, Opus, or
  G.722.
- Network path: The IP route between callers, PBX systems, media servers, or
  carriers.

### Key Characteristics

- Uses IP networks instead of dedicated telephone circuits.
- Scales more easily than traditional fixed-line systems.
- Can support voice, video, messaging, call recording, analytics, IVR, and
  contact center workflows.
- Depends heavily on network quality, latency, jitter, packet loss, and firewall
  or NAT traversal.

### VoIP Call Flow at a High Level

```text
1. SIP sets up the call.
2. A codec encodes the voice audio.
3. RTP carries the encoded audio packets.
4. SIP ends the call when either side hangs up.
```

[Back to contents](#contents)

## SIP Trunk Provider

A SIP trunk provider is the digital bridge between an internal IP PBX and the
Public Switched Telephone Network.

### What It Is

A SIP trunk provider is a carrier or VoIP provider that lets a PBX place and
receive external calls over an internet connection. It accepts SIP signaling from
the PBX, handles call routing, and connects the call to landline, mobile, or
other business phone networks.

Without a SIP trunk or another carrier connection, a PBX such as 3CX or Asterisk
can still run internal calls, voicemail, IVRs, queues, and extensions, but it
cannot normally call or receive calls from outside phone numbers.

### Role

- Connects an internal PBX to the PSTN.
- Provides inbound and outbound telephone number routing.
- Handles caller ID, number presentation, and carrier-level call delivery.
- May provide emergency calling, SMS, fraud controls, call recording options, or
  regional compliance features depending on the provider and country.

### How the Connection Works

```text
Internal phones / softphones
  -> 3CX or Asterisk PBX
  -> SIP trunk over the internet
  -> SIP trunk provider
  -> PSTN / mobile / landline network
```

The PBX controls internal routing. The SIP trunk provider handles the external
network side.

### When You Need a SIP Trunk Provider

You need a SIP trunk provider, or an equivalent carrier connection, when you want
3CX, Asterisk, or another IP PBX to make or receive calls with external phone
numbers.

Common cases:

- Calling customer mobile or landline numbers.
- Receiving calls on public business phone numbers.
- Routing contact center traffic to agents from the PSTN.
- Connecting an office PBX to national or international telephone networks.

### When You May Not Need One

There are two common exceptions:

- Internal-only communications: The PBX is used only for employees, branches, or
  internal extensions.
- Legacy carrier hardware: The PBX connects directly to analog lines, T1/E1, or
  PRI circuits through telephony interface cards or external voice gateways.

Legacy hardware gateways still provide a carrier connection, but they bypass SIP
trunking by connecting the PBX to older physical telephone circuits.

### 3CX and Asterisk Provider Selection

For 3CX, prefer a 3CX-supported or preferred SIP trunk provider when possible.
Supported providers are tested with 3CX, include preconfigured templates, and
reduce setup risk for caller ID, inbound routing, outbound rules, and emergency
calling.

For Asterisk, provider selection is more flexible because Asterisk is open and
highly configurable. Asterisk can work with many SIP trunk providers, including
API-oriented platforms such as Telnyx SIP Trunking or Twilio Elastic SIP
Trunking, but the administrator is responsible for trunk configuration, codecs,
security, dial plans, and interoperability testing.

[Back to contents](#contents)

## SIP

SIP stands for Session Initiation Protocol.

### What It Is

SIP is an IP-based application-layer signaling protocol. It acts as the call
manager for many VoIP systems.

### Role

- Locates the called party.
- Negotiates call parameters such as supported codecs and media addresses.
- Starts, modifies, transfers, and ends calls.
- Sends signaling messages such as `INVITE`, `100 Trying`, `180 Ringing`,
  `200 OK`, `ACK`, and `BYE`.

### Key Characteristic

SIP does not carry the actual voice audio. It controls the session. The media is
usually carried separately by RTP or SRTP.

[Back to contents](#contents)

## RTP

RTP stands for Real-time Transport Protocol.

### What It Is

RTP is the protocol responsible for transporting real-time media such as voice or
video after the call has been established.

### Role

- Packages audio or video into real-time packets.
- Adds sequence numbers so receivers can detect missing or out-of-order packets.
- Adds timestamps so receivers can play media smoothly.
- Carries the media stream between endpoints, PBX systems, media servers, or
  gateways.

### Key Characteristic

RTP commonly runs over UDP because live conversation prioritizes low delay over
perfect retransmission. A small amount of packet loss is usually better than
waiting too long for missing packets to be resent.

[Back to contents](#contents)

## PCM

PCM stands for Pulse Code Modulation.

### What It Is

PCM is a mathematical method for converting continuous analog audio, such as human speech,
into digital samples.

### Role

- Samples the audio waveform at regular intervals.
- Converts each sample into a numeric value.
- Produces digital audio that can be processed by codecs and transported over
  RTP.

### Key Characteristic

Standard telephony audio commonly samples voice 8,000 times per second. G.711,
one of the most common VoIP codecs, is based on PCM and produces a 64 kbps audio
stream before packet overhead.

[Back to contents](#contents)

## How They Work Together

For a typical VoIP call:

```text
Caller endpoint
  -> SIP signaling starts the session
  -> Codec converts voice into digital audio
  -> RTP transports the audio packets
  -> SIP signaling ends the session
  -> Called endpoint receives and plays the audio
```

If the call reaches a traditional landline or mobile number, a gateway or SIP
trunk provider bridges the IP voice network to the PSTN.

```text
SIP phone
  -> IP PBX
  -> SIP trunk provider
  -> PSTN gateway / ATS
  -> Landline or mobile phone
```

For a traditional landline call, the ATS is the system that performs the actual
switching inside the PSTN.

```text
Landline phone
  -> Local ATS
  -> PSTN
  -> Destination ATS
  -> Receiving phone
```

[Back to contents](#contents)

## Example Business Call Flow

```text
1. A customer calls the company phone number from the PSTN.
2. The carrier sends the call to the company's SIP trunk provider.
3. The SIP trunk provider sends a SIP INVITE to the company PBX.
4. The PBX applies routing rules, such as IVR, queue, extension, or business hours.
5. SIP negotiates the media details.
6. RTP carries the live audio between the customer side and the selected agent.
7. PCM-based audio may be encoded using a codec such as G.711.
8. When the call ends, SIP sends a BYE message and the RTP stream stops.
```

[Back to contents](#contents)

## Layer Relationship

```text
Business call control:  PBX
Voice architecture:    VoIP
Carrier bridge:        SIP trunk provider
Call signaling:        SIP
Media transport:       RTP
Audio encoding:        PCM / codecs
Legacy carrier side:   PSTN
Telephone switching:   ATS
```

In short, PBX decides how business calls are routed, VoIP carries voice over IP
networks, a SIP trunk provider connects the IP PBX to external phone networks,
SIP controls the call session, RTP transports the live media, PCM represents the
digital audio foundation, PSTN connects to the traditional telephone world, and
ATS performs the switching that connects dialed numbers to receiving lines.

[Back to contents](#contents)
