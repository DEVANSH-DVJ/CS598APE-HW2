// philox_engine.h
#ifndef PHILOX_ENGINE_H
#define PHILOX_ENGINE_H

#include <cstdint>
#include <limits>
#include <philox_rng.h>

struct PhiloxEngine {
  using result_type = uint32_t;
  // streams of different (seed, stream, substream) never overlap
  explicit PhiloxEngine(uint32_t seed, uint32_t stream = 0, uint32_t substream = 0)
      : key_{seed, stream}, counter_{0, substream} {
  }
  uint32_t operator()() {
    // the first counter word numbers the draws
    uint32_t c[4] = {counter_[0]++, counter_[1], 0, 0};
    uint32_t k[2] = {key_[0], key_[1]};
    // ten rounds of Philox4x32
    for (int i = 0; i < 10; i++) {
      uint64_t p0 = (uint64_t)PHILOX_M4x32A * c[0];
      uint64_t p1 = (uint64_t)PHILOX_M4x32B * c[2];
      c[0] = (uint32_t)(p1 >> 32) ^ c[1] ^ k[0];
      c[2] = (uint32_t)(p0 >> 32) ^ c[3] ^ k[1];
      c[1] = (uint32_t)p1;
      c[3] = (uint32_t)p0;
      k[0] += PHILOX_W32A;
      k[1] += PHILOX_W32B;
    }
    return c[0];
  }
  static constexpr uint32_t min() {
    return 0;
  }
  static constexpr uint32_t max() {
    return UINT32_MAX;
  }

private:
  uint32_t key_[2];
  uint32_t counter_[2];
};

#endif // PHILOX_ENGINE_H
