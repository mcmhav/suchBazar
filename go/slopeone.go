package main

import (
  "fmt"
)

type SlopeOne struct {
  diffs map[Key]float64
  freqs map[Key]float64
}

type Key struct {
  item1, item2 string
}

type Prediction struct {
  Title string
  Score string
}

func (s *SlopeOne) Init() {
  s.diffs = make(map[Key]float64)
  s.freqs = make(map[Key]float64)
}

func (s *SlopeOne) Update(userdata map[string]float64) {
  for i1, r1 := range userdata {
    for i2, r2 := range userdata {
      s.diffs[Key{i1, i2}] += r1 - r2
      s.freqs[Key{i1, i2}] += 1
    }
  }
  for key, _ := range s.diffs {
    s.diffs[key] = s.diffs[key] / s.freqs[key]
  }
}

func (s *SlopeOne) Predict(userdata map[string]float64) []Prediction {
  preds := make(map[string]float64)
  freqs := make(map[string]float64)

  for key, value := range s.diffs {
    if _, ok := userdata[key.item1]; !ok {
      if _, ok := userdata[key.item2]; ok {
        if key.item1 != key.item2 {
          // Do weighted average on the differences
          preds[key.item1] += s.freqs[key] * (userdata[key.item2] + value)
          freqs[key.item1] += s.freqs[key]
        }
      }
    }
  }

  // Divide all predicitons on frequency
  predictions := make([]Prediction, 0)
  for title, pred := range preds {
    predictions = append(predictions, Prediction{Title: title, Score: fmt.Sprintf("%.2f", pred/freqs[title])})
  }

  return predictions
}

/* Sorting on predictions */
type ByScore []Prediction
func (bs ByScore) Len() int { return len(bs) }
func (bs ByScore) Swap(i, j int) { bs[i], bs[j] = bs[j], bs[i] }
func (bs ByScore) Less(i, j int) bool {
  return bs[i].Score >= bs[j].Score
}
