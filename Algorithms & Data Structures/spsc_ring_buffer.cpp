// =============================================================================
//  spsc_ring_buffer.cpp
//
//  Lock-free Single-Producer / Single-Consumer (SPSC) ring buffer for PCM audio.
//
//  Designed for a real-time AI voice call-center pipeline:
//
//      RTP / jitter buffer  ->  [ SpscRingBuffer ]  ->  VAD -> smart-turn
//                                                            -> utterance assembly
//                                                            -> AI model commit
//
//  Audio is 8 kHz mono PCM, samples stored as int16_t. One thread (the RTP /
//  network side) writes decoded frames; one thread (the inference / DSP side)
//  reads them. There is exactly one producer and one consumer.
//
//  Real-time safety guarantees of this class:
//    * No locks, no mutexes, no condition variables, no syscalls on the hot path.
//    * No heap allocation after construction (all memory reserved in the ctor).
//    * Wait-free for the producer and wait-free for the consumer: write() and
//      read() run in bounded time independent of the other thread.
//
//  Build:
//      g++   -std=c++17 -O2 -Wall -Wextra spsc_ring_buffer.cpp -o spsc_ring_buffer && ./spsc_ring_buffer
//      clang++ -std=c++17 -O2 -Wall -Wextra spsc_ring_buffer.cpp -o spsc_ring_buffer && ./spsc_ring_buffer
//      MSVC:  cl /std:c++17 /O2 /EHsc spsc_ring_buffer.cpp
//
//  Dependency-free, portable C++17.
// =============================================================================

#include <atomic>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <new>
#include <vector>

// -----------------------------------------------------------------------------
//  Cache-line size used to pad the two atomic indices apart so that the
//  producer writing head_ and the consumer writing tail_ do not invalidate the
//  same cache line on each other's CPU (false sharing). 64 bytes is correct for
//  x86-64 and AArch64; harmless if the real line is smaller.
// -----------------------------------------------------------------------------
#if defined(__cpp_lib_hardware_interference_size)
    // std::hardware_destructive_interference_size may be unavailable even when
    // the feature macro is defined on some libstdc++ versions; fall back safely.
    static constexpr std::size_t kCacheLineSize = 64;
#else
    static constexpr std::size_t kCacheLineSize = 64;
#endif

// =============================================================================
//  SpscRingBuffer
// =============================================================================
class SpscRingBuffer
{
public:
    // -------------------------------------------------------------------------
    //  Construct a buffer able to hold at least `capacitySamples` int16_t PCM
    //  samples simultaneously.
    //
    //  Internally the backing storage is rounded UP to the next power of two so
    //  that index wrap-around can be done with a single bitwise-AND mask instead
    //  of a modulo / branch. One extra slot is *not* needed here because we use
    //  free-running 64-bit indices (head/tail keep counting up and are masked
    //  only when indexing); the full/empty ambiguity is resolved by comparing
    //  the raw counters, so the entire allocated array is usable.
    //
    //  The usable capacity reported by capacity() is the rounded-up storage size.
    // -------------------------------------------------------------------------
    explicit SpscRingBuffer(std::size_t capacitySamples)
        : capacity_(roundUpPow2(capacitySamples == 0 ? 1 : capacitySamples)),
          mask_(capacity_ - 1),
          buffer_(static_cast<int16_t*>(::operator new[](capacity_ * sizeof(int16_t))))
    {
        // All allocation happens here, in the constructor, never on the hot path.
        head_.store(0, std::memory_order_relaxed);
        tail_.store(0, std::memory_order_relaxed);
    }

    ~SpscRingBuffer()
    {
        ::operator delete[](buffer_);
    }

    // Non-copyable, non-movable: the buffer is shared by reference between the
    // two threads; copying atomic indices would break the SPSC contract.
    SpscRingBuffer(const SpscRingBuffer&)            = delete;
    SpscRingBuffer& operator=(const SpscRingBuffer&) = delete;
    SpscRingBuffer(SpscRingBuffer&&)                 = delete;
    SpscRingBuffer& operator=(SpscRingBuffer&&)      = delete;

    // -------------------------------------------------------------------------
    //  write() — PRODUCER thread only.
    //
    //  Copies up to `sampleCount` samples from `input` into the buffer and
    //  returns the number actually written (which is min(sampleCount, freeSpace)).
    //  A short return means the buffer was (nearly) full; the caller decides
    //  whether to drop the remainder. In real-time audio we never block.
    // -------------------------------------------------------------------------
    std::size_t write(const int16_t* input, std::size_t sampleCount) noexcept
    {
        // Our own index. We are the only writer of head_, so relaxed load is
        // fine — no other thread changes it.
        const std::size_t head = head_.load(std::memory_order_relaxed);

        // Consumer's index. ACQUIRE so that we observe the slots the consumer
        // has already freed (its release store in read()). This synchronizes
        // the "space is available" information.
        const std::size_t tail = tail_.load(std::memory_order_acquire);

        const std::size_t freeSlots = capacity_ - (head - tail);
        const std::size_t toWrite   = (sampleCount < freeSlots) ? sampleCount : freeSlots;
        if (toWrite == 0)
            return 0;

        // Copy, splitting into at most two contiguous runs around the wrap point.
        const std::size_t offset = head & mask_;                 // start index
        const std::size_t first  = std::min(toWrite, capacity_ - offset);
        std::memcpy(buffer_ + offset, input, first * sizeof(int16_t));
        if (toWrite > first)
            std::memcpy(buffer_, input + first, (toWrite - first) * sizeof(int16_t));

        // Publish the new head with RELEASE: every sample store above must be
        // visible to the consumer *before* it sees the advanced head. This is
        // the half of the handshake that hands data to the reader.
        head_.store(head + toWrite, std::memory_order_release);
        return toWrite;
    }

    // -------------------------------------------------------------------------
    //  read() — CONSUMER thread only.
    //
    //  Copies up to `sampleCount` samples out of the buffer into `output` and
    //  returns the number actually read (min(sampleCount, available)). A short
    //  return means the buffer was (nearly) empty.
    // -------------------------------------------------------------------------
    std::size_t read(int16_t* output, std::size_t sampleCount) noexcept
    {
        // Our own index; we are the only writer of tail_, relaxed is fine.
        const std::size_t tail = tail_.load(std::memory_order_relaxed);

        // Producer's index. ACQUIRE so that the sample stores published by the
        // producer's release store in write() are visible to us before we read
        // them. This is the other half of the handshake.
        const std::size_t head = head_.load(std::memory_order_acquire);

        const std::size_t avail   = head - tail;
        const std::size_t toRead  = (sampleCount < avail) ? sampleCount : avail;
        if (toRead == 0)
            return 0;

        const std::size_t offset = tail & mask_;
        const std::size_t first  = std::min(toRead, capacity_ - offset);
        std::memcpy(output, buffer_ + offset, first * sizeof(int16_t));
        if (toRead > first)
            std::memcpy(output + first, buffer_, (toRead - first) * sizeof(int16_t));

        // Publish the new tail with RELEASE: the producer reads tail_ with
        // acquire to learn that these slots are now free for reuse. Releasing
        // here guarantees the producer won't overwrite slots we are still
        // copying out of.
        tail_.store(tail + toRead, std::memory_order_release);
        return toRead;
    }

    // -------------------------------------------------------------------------
    //  Observers. Safe to call from either thread, but the value is only an
    //  instantaneous snapshot — by the time it returns the other thread may
    //  have moved on. For SPSC use:
    //    * available() / empty()  are exact for the CONSUMER (only producer can
    //      add, so the real count is >= the returned value).
    //    * freeSpace() / full()   are exact for the PRODUCER (only consumer can
    //      free, so the real free space is >= the returned value).
    //  i.e. each observer is conservative for the thread that needs it.
    // -------------------------------------------------------------------------
    std::size_t available() const noexcept
    {
        const std::size_t head = head_.load(std::memory_order_acquire);
        const std::size_t tail = tail_.load(std::memory_order_acquire);
        return head - tail;
    }

    std::size_t freeSpace() const noexcept
    {
        return capacity_ - available();
    }

    std::size_t capacity() const noexcept { return capacity_; }

    bool empty() const noexcept { return available() == 0; }

    bool full()  const noexcept { return available() == capacity_; }

    // -------------------------------------------------------------------------
    //  reset() — NOT thread-safe. Only call when both producer and consumer are
    //  quiesced (e.g. between calls, on stream teardown / new call setup).
    // -------------------------------------------------------------------------
    void reset() noexcept
    {
        head_.store(0, std::memory_order_relaxed);
        tail_.store(0, std::memory_order_relaxed);
    }

private:
    static std::size_t roundUpPow2(std::size_t v) noexcept
    {
        // Smallest power of two >= v.
        if (v <= 1) return 1;
        --v;
        v |= v >> 1;
        v |= v >> 2;
        v |= v >> 4;
        v |= v >> 8;
        v |= v >> 16;
#if SIZE_MAX > 0xFFFFFFFFu
        v |= v >> 32;
#endif
        return v + 1;
    }

    const std::size_t capacity_;   // power-of-two number of int16_t slots
    const std::size_t mask_;       // capacity_ - 1, for AND-wrapping
    int16_t* const    buffer_;     // backing store, allocated once in ctor

    // Free-running counters. They only ever increase; we mask them when
    // indexing. Using the unwrapped difference (head - tail) avoids the classic
    // "one empty slot" trick and removes full/empty ambiguity. With 64-bit
    // counters at 8 kHz, overflow would take ~73 million years.
    //
    // Each atomic sits on its own cache line (alignas) so the producer's writes
    // to head_ and the consumer's writes to tail_ never ping-pong the same line
    // between cores — this is the false-sharing mitigation.
    alignas(kCacheLineSize) std::atomic<std::size_t> head_;  // written by producer
    alignas(kCacheLineSize) std::atomic<std::size_t> tail_;  // written by consumer

    // Pad the tail end too, so a neighbouring object in memory can't share
    // tail_'s line either.
    char padding_[kCacheLineSize - sizeof(std::atomic<std::size_t>)];
};

// =============================================================================
//  Unit tests / assertions
// =============================================================================
namespace tests {

static void test_basic_write_read()
{
    SpscRingBuffer rb(8);  // rounds to 8
    assert(rb.capacity() == 8);
    assert(rb.empty());
    assert(!rb.full());
    assert(rb.available() == 0);
    assert(rb.freeSpace() == 8);

    int16_t in[4] = {10, 20, 30, 40};
    assert(rb.write(in, 4) == 4);
    assert(rb.available() == 4);
    assert(rb.freeSpace() == 4);
    assert(!rb.empty());

    int16_t out[4] = {0, 0, 0, 0};
    assert(rb.read(out, 4) == 4);
    assert(out[0] == 10 && out[1] == 20 && out[2] == 30 && out[3] == 40);
    assert(rb.empty());
    assert(rb.available() == 0);
    std::cout << "[ok] basic write/read\n";
}

static void test_wrap_around()
{
    SpscRingBuffer rb(8);  // capacity 8

    // Advance head and tail near the end so the next write straddles the wrap.
    int16_t seed[6] = {1, 2, 3, 4, 5, 6};
    assert(rb.write(seed, 6) == 6);
    int16_t drain[6] = {};
    assert(rb.read(drain, 6) == 6);          // head=tail=6, both near wrap

    // Now write 6 more: 2 fit before index 8 wraps, 4 wrap to the front.
    int16_t in[6] = {100, 101, 102, 103, 104, 105};
    assert(rb.write(in, 6) == 6);
    assert(rb.available() == 6);

    int16_t out[6] = {};
    assert(rb.read(out, 6) == 6);
    for (int i = 0; i < 6; ++i)
        assert(out[i] == in[i]);             // order preserved across wrap
    std::cout << "[ok] wrap-around read/write\n";
}

static void test_partial_write_when_full()
{
    SpscRingBuffer rb(4);  // capacity 4
    int16_t in[6] = {1, 2, 3, 4, 5, 6};

    // Only 4 fit; write must report the truncated count.
    assert(rb.write(in, 6) == 4);
    assert(rb.full());
    assert(rb.freeSpace() == 0);

    // A further write when full returns 0 (no blocking, no overwrite).
    assert(rb.write(in, 3) == 0);
    std::cout << "[ok] partial write when full\n";
}

static void test_partial_read_when_empty()
{
    SpscRingBuffer rb(4);
    int16_t in[2] = {7, 8};
    assert(rb.write(in, 2) == 2);

    int16_t out[6] = {};
    // Asked for 6, only 2 available -> returns 2.
    assert(rb.read(out, 6) == 2);
    assert(out[0] == 7 && out[1] == 8);
    assert(rb.empty());

    // Reading an empty buffer returns 0.
    assert(rb.read(out, 6) == 0);
    std::cout << "[ok] partial read when empty\n";
}

static void test_available_freespace_accounting()
{
    SpscRingBuffer rb(16);
    assert(rb.available() + rb.freeSpace() == rb.capacity());

    int16_t in[10] = {};
    rb.write(in, 10);
    assert(rb.available() == 10);
    assert(rb.freeSpace() == 6);
    assert(rb.available() + rb.freeSpace() == rb.capacity());

    int16_t out[7] = {};
    rb.read(out, 7);
    assert(rb.available() == 3);
    assert(rb.freeSpace() == 13);
    assert(rb.available() + rb.freeSpace() == rb.capacity());

    rb.reset();
    assert(rb.empty());
    assert(rb.freeSpace() == rb.capacity());
    std::cout << "[ok] available/freeSpace accounting\n";
}

static void run_all()
{
    test_basic_write_read();
    test_wrap_around();
    test_partial_write_when_full();
    test_partial_read_when_empty();
    test_available_freespace_accounting();
    std::cout << "All tests passed.\n";
}

} // namespace tests

// =============================================================================
//  Example: 8 kHz mono PCM, 20 ms frames (160 samples per frame).
//
//  At 8000 Hz, a 20 ms frame = 0.020 * 8000 = 160 samples. This is the typical
//  RTP packetization interval (ptime=20) for narrowband telephony codecs
//  (G.711 / G.722 decoded to linear PCM, etc.).
//
//  We size the buffer to hold ~200 ms of audio (10 frames) so the consumer side
//  (VAD / smart-turn / model commit) can fall a few frames behind without the
//  producer dropping audio.
// =============================================================================
namespace example {

constexpr std::size_t kSampleRate   = 8000;                 // 8 kHz
constexpr std::size_t kFrameMs      = 20;                   // 20 ms frames
constexpr std::size_t kFrameSamples = kSampleRate * kFrameMs / 1000;  // = 160
constexpr std::size_t kBufferMs     = 200;                  // ~200 ms cushion
constexpr std::size_t kBufferSamples= kSampleRate * kBufferMs / 1000; // = 1600

static void run()
{
    SpscRingBuffer rb(kBufferSamples);  // rounded up to 2048 internally
    std::cout << "\nExample: 8 kHz / 20 ms frames (" << kFrameSamples
              << " samples/frame), capacity = " << rb.capacity()
              << " samples (~" << (rb.capacity() * 1000 / kSampleRate)
              << " ms)\n";

    // --- Producer side (RTP/jitter thread) -----------------------------------
    // Synthesize one frame of fake PCM and push it. In production this is the
    // decoded RTP payload handed off after jitter-buffer reordering.
    int16_t frame[kFrameSamples];
    for (std::size_t i = 0; i < kFrameSamples; ++i)
        frame[i] = static_cast<int16_t>(i);  // ramp, just for demonstration

    std::size_t pushed = rb.write(frame, kFrameSamples);
    std::cout << "Producer wrote " << pushed << " samples; buffer now holds "
              << rb.available() << " (" << (rb.available() * 1000 / kSampleRate)
              << " ms).\n";

    // --- Consumer side (VAD / inference thread) ------------------------------
    // Pull whole frames for downstream processing. read() may return a short
    // count if a full frame isn't ready yet; the consumer simply waits for the
    // next scheduler tick rather than blocking.
    int16_t outFrame[kFrameSamples];
    std::size_t got = rb.read(outFrame, kFrameSamples);
    std::cout << "Consumer read " << got << " samples for VAD/smart-turn; "
              << "buffer now holds " << rb.available() << ".\n";

    // Verify the round trip preserved the data.
    bool intact = (got == kFrameSamples);
    for (std::size_t i = 0; intact && i < kFrameSamples; ++i)
        intact = (outFrame[i] == frame[i]);
    std::cout << "Frame integrity: " << (intact ? "OK" : "CORRUPT") << "\n";
}

} // namespace example

// =============================================================================
int main()
{
    tests::run_all();
    example::run();
    return 0;
}
