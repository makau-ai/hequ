# Data Feed Requirements for Non-Sensor Equations

**53 equations that need DATA, not physical sensors.** For each,
the specific data types, formats, and candidate sources are listed.
Any of these could come from makau.ai's existing data infrastructure,
public APIs, archived datasets, or generated synthetically.

---

## Mathematics (9 equations)

These are provable identities and theorems — they don't need
external data to "verify" in the physics sense, but they CAN be
validated computationally against numerical datasets.

### EQ-0073 Euler's Identity: e^(iπ) + 1 = 0
**Data needed:** None — this is an exact identity. Verified by CAS.
**Computational test:** Evaluate `exp(i*pi) + 1` at increasing
precision (50, 100, 500, 1000 digits) and confirm the result
converges to 0. Already doable in hequ.ai's mpmath pipeline.

### EQ-0074 Fundamental Theorem of Calculus: ∫f(x)dx = F(b)−F(a)
**Data needed:** Any time-series signal where both the signal and
its integral are independently measured.
**Data type:** Two synchronized time-series: `signal(t)` and
`cumulative(t)` where cumulative is the running integral.
**Sources:**
- makau.ai sensor streams: any sensor reading + its cumulative sum
- Power grid: instantaneous power P(t) + cumulative energy E(t)
- Financial: price returns (signal) + cumulative return (integral)

### EQ-0075 Bayes' Theorem: P(A|B) = P(B|A)·P(A)/P(B)
**Data needed:** Event counts with labeled categories.
**Data type:** Contingency table: `{event_A: bool, event_B: bool, count: int}`
**Sources:**
- makau.ai learner events: `{passed_quiz: bool, used_hint: bool}`
- Medical datasets: `{test_positive: bool, has_disease: bool}`
- Email: `{is_spam: bool, contains_word_X: bool}` (classic Bayesian filter)
- makau.ai agent assessments: `{learner_stuck: bool, topic: str}`

### EQ-0076 Fourier Transform: F(ω) = ∫f(t)·e^(−iωt)dt
**Data needed:** Any periodic or quasi-periodic time-series signal.
**Data type:** Uniformly-sampled time series `{t: float, value: float}[]`
**Sources:**
- makau.ai sensor streams: temperature oscillations, voltage AC waveforms
- Audio files (WAV/MP3 → sample array)
- Seismic data (USGS, IRIS)
- Financial tick data (high-frequency price series)
- Network packet timing (makau.ai captures → inter-arrival times)

### EQ-0077 Central Limit Theorem: (X̄−μ)/(σ/√n) → N(0,1)
**Data needed:** Repeated samples from ANY distribution.
**Data type:** Array of sample means from N draws of size n:
`{sample_means: float[], n: int, true_mean: float, true_std: float}`
**Sources:**
- makau.ai sensor readings: take n-sample batches from any sensor
- makau.ai learner scores: batch averages of quiz scores
- Any API that returns numeric values: batch, compute mean, repeat

### EQ-0078 Pythagorean Theorem: a² + b² = c²
**Data needed:** Geometric measurements (distances, coordinates).
**Data type:** `{a: float, b: float, c: float}` — three side lengths of a right triangle.
**Sources:**
- GPS coordinates (makau.ai GNSS module): compute distances between 3 points
- Image analysis: detect right angles in photos, measure pixel distances
- M5Stack ToF sensors: measure two perpendicular distances + the hypotenuse

### EQ-0079 Taylor Series: f(x) = Σ f^(n)(a)·(x−a)^n/n!
**Data needed:** A function and its derivatives at a point.
**Data type:** Function evaluation table: `{x: float, f_exact: float, f_taylor_N: float}`
**Sources:** Purely computational — evaluate any function (sin, exp, log) at
increasing Taylor orders and verify convergence. No external data needed.

### EQ-0080 Laplace Transform: F(s) = ∫₀^∞ f(t)·e^(−st)dt
**Data needed:** A time-domain signal and its known Laplace-domain representation.
**Data type:** Time-series `f(t)` + expected `F(s)` at specific s values.
**Sources:**
- Control system step responses (makau.ai PID experiments → step response data)
- Circuit transients (RC charging curve → 1/(s+1/RC) in Laplace domain)

### EQ-0081 Stokes' Theorem: ∮F·dr = ∬(∇×F)·dS
**Data needed:** A vector field sampled on a surface and its boundary.
**Data type:** `{field_values: [{x,y,z, Fx,Fy,Fz}], boundary_points: [{x,y,z}]}`
**Sources:** Computational verification — define a vector field analytically,
compute both sides numerically, verify equality. Alternatively: use
makau.ai's network topology data (graph Laplacian as a discrete Stokes analog).

---

## Computer Science (9 equations)

### EQ-0090 Shannon Entropy: H = −Σ pᵢ·log₂(pᵢ)
**Data needed:** Probability distributions (empirical frequency counts).
**Data type:** `{symbol: str, count: int}[]` → compute pᵢ = count/total
**Sources:**
- makau.ai event types: frequency distribution of 80+ event types
- Text corpora: character or word frequency distributions
- Network traffic: protocol distribution from packet captures
- Sensor readings: histogram bin counts from any sensor stream

### EQ-0091 Gradient Descent: θ := θ − α·∇J(θ)
**Data needed:** A loss function J(θ) and its gradient, evaluated over training steps.
**Data type:** `{step: int, theta: float[], loss: float, gradient: float[]}[]`
**Sources:**
- makau.ai orchestrator task log: agent optimization traces (convergence curves)
- Any ML training run: log loss + parameter snapshots per epoch
- Synthetic: generate a quadratic J(θ) and trace GD convergence

### EQ-0092 Backpropagation: δˡ = ((Wˡ⁺¹)ᵀδˡ⁺¹) ⊙ σ'(zˡ)
**Data needed:** Neural network forward+backward pass snapshots.
**Data type:** `{layer: int, z: float[], a: float[], delta: float[], W: float[][]}` per layer
**Sources:**
- PyTorch/TensorFlow training hook that dumps intermediate activations
- makau.ai agent neural network internals (if exposed)
- Synthetic: small 2-layer network on XOR, log every intermediate

### EQ-0093 Attention Mechanism: Attention(Q,K,V) = softmax(QKᵀ/√dₖ)V
**Data needed:** Query, Key, Value matrices and the attention output.
**Data type:** `{Q: float[][], K: float[][], V: float[][], d_k: int, output: float[][]}`
**Sources:**
- Transformer model inference hook (extract Q,K,V from a specific layer)
- makau.ai's AI agents use LLMs — attention weights could be extracted
- Synthetic: small sequence, manual Q/K/V, compute attention, verify

### EQ-0094 Softmax: P(yᵢ) = e^(zᵢ)/Σe^(zⱼ)
**Data needed:** Logit vector and resulting probability distribution.
**Data type:** `{logits: float[], probabilities: float[]}`
**Sources:**
- Any classifier's final layer output (before and after softmax)
- makau.ai agent decision scores (if exposed as logits)
- Synthetic: random logit vector, compute softmax, verify Σpᵢ = 1

### EQ-0095 Cross-Entropy Loss: L = −Σ yᵢ·log(ŷᵢ)
**Data needed:** True labels and predicted probabilities.
**Data type:** `{y_true: int[], y_pred_prob: float[][]}` (one-hot true + softmax predicted)
**Sources:**
- Any classification model's predictions vs ground truth
- makau.ai agent assessment predictions vs actual learner outcomes
- makau.ai knowledge-base query relevance scores vs human judgments

### EQ-0096 PageRank: PR(p) = (1−d)/N + d·Σ PR(q)/L(q)
**Data needed:** A directed graph (adjacency list) and convergent PageRank scores.
**Data type:** `{nodes: str[], edges: [{from, to}], damping: float, pagerank: {node: score}}`
**Sources:**
- makau.ai CORE network topology: nodes = routers/hosts, edges = links
- Web crawl data (Common Crawl, if accessible)
- Citation networks (OpenAlex, Semantic Scholar API)
- Social network graphs (if available through makau.ai)

### EQ-0097 RSA Encryption: c = mᵉ mod n; m = cᵈ mod n
**Data needed:** RSA key pair (p, q, n, e, d) and plaintext/ciphertext pairs.
**Data type:** `{p: int, q: int, n: int, e: int, d: int, m: int, c: int}`
**Sources:**
- Generate keypairs programmatically (openssl, python-rsa)
- makau.ai compliance dossiers may include certificate/key metadata
- Synthetic: small primes for educational RSA, verify encrypt/decrypt cycle

### EQ-0098 Big-O Notation: f(n) = O(g(n))
**Data needed:** Runtime measurements at increasing input sizes.
**Data type:** `{n: int, runtime_seconds: float}[]` for a known algorithm
**Sources:**
- Benchmark any algorithm: sort, search, matrix multiply at n = 10, 100, 1k, 10k, 100k
- makau.ai orchestrator task log: task completion time vs problem size
- makau.ai CORE network simulation: packet processing time vs topology size

---

## Economics & Finance (9 equations)

### EQ-0099 Black-Scholes: ∂V/∂t + ½S²σ²∂²V/∂S² + rS·∂V/∂S − rV = 0
**Data needed:** Option prices, underlying stock price, volatility, risk-free rate.
**Data type:** `{S: float, K: float, T: float, r: float, sigma: float, V_market: float, V_BS: float}`
**Sources:**
- Yahoo Finance API (free): historical stock + option chain data
- CBOE delayed quotes
- FRED (Federal Reserve Economic Data): risk-free rate (T-bill yields)
- Synthetic: generate BS prices, add noise, verify PDE residual

### EQ-0100 CAPM: E(Rᵢ) = Rᶠ + βᵢ·(E(Rₘ) − Rᶠ)
**Data needed:** Stock returns, market returns, risk-free rate.
**Data type:** `{stock_returns: float[], market_returns: float[], rf: float}`
**Sources:**
- Yahoo Finance API: daily returns for any stock + S&P 500 index
- FRED: T-bill rate for Rᶠ
- Kenneth French data library (free): Fama-French factor returns

### EQ-0101 Cobb-Douglas: Y = A·Lᵅ·Kᵝ
**Data needed:** GDP, labor input, capital stock, technology parameter.
**Data type:** `{year: int, GDP: float, labor: float, capital: float}[]`
**Sources:**
- World Bank Open Data API: GDP, labor force, gross capital formation by country/year
- Penn World Table (free): cross-country production function data
- FRED: US GDP + employment + capital stock time series

### EQ-0102 Nash Equilibrium
**Data needed:** Payoff matrices for two-player games.
**Data type:** `{player1_payoffs: float[][], player2_payoffs: float[][], strategies: int[]}`
**Sources:**
- Game theory textbook datasets (Prisoner's Dilemma, Chicken, Stag Hunt)
- makau.ai agent interaction logs: multi-agent decision outcomes
- Auction data (eBay completed listings — game-theoretic equilibrium analysis)

### EQ-0103 GDP Expenditure: GDP = C + I + G + (X − M)
**Data needed:** National accounts: consumption, investment, government spending, exports, imports.
**Data type:** `{year: int, C: float, I: float, G: float, X: float, M: float, GDP: float}`
**Sources:**
- World Bank API: GDP components by country/year
- FRED: US NIPA (National Income and Product Accounts) quarterly
- IMF World Economic Outlook database

### EQ-0104 Fisher Equation: (1+i) = (1+r)·(1+π)
**Data needed:** Nominal interest rate, real interest rate, inflation rate.
**Data type:** `{date: str, nominal_rate: float, inflation: float, real_rate: float}`
**Sources:**
- FRED: Federal Funds Rate (i), CPI inflation (π), TIPS yield (r)
- Bank of England, ECB, or any central bank API

### EQ-0105 Solow Growth: Δk = s·f(k) − (δ+n)·k
**Data needed:** Savings rate, depreciation, population growth, capital per worker over time.
**Data type:** `{year: int, k: float, s: float, delta: float, n: float, GDP_per_worker: float}[]`
**Sources:**
- Penn World Table: capital stock, labor, GDP per worker by country
- World Bank: savings rate, population growth, investment/GDP ratio

### EQ-0106 Phillips Curve: π = πₑ − β·(u − uₙ) + ε
**Data needed:** Inflation rate, unemployment rate, expected inflation.
**Data type:** `{date: str, inflation: float, unemployment: float, expected_inflation: float}`
**Sources:**
- FRED: CPI inflation + unemployment rate (monthly, decades of history)
- Survey of Professional Forecasters (expected inflation)
- OECD stats: cross-country inflation + unemployment

### EQ-0107 Supply-Demand Equilibrium: Qd(P*) = Qs(P*)
**Data needed:** Price + quantity data showing equilibrium convergence.
**Data type:** `{price: float, quantity_demanded: float, quantity_supplied: float}[]`
**Sources:**
- Commodity markets: historical price + production + consumption (USDA, EIA)
- makau.ai auction/marketplace data (if any)
- Synthetic: generate supply/demand curves with known elasticities

---

## Social Sciences & Psychology (7 equations)

### EQ-0108 Pearson Correlation: r = Σ(xᵢ−x̄)(yᵢ−ȳ)/√[Σ(xᵢ−x̄)²·Σ(yᵢ−ȳ)²]
**Data needed:** Any paired dataset (x, y).
**Data type:** `{x: float[], y: float[]}`
**Sources:**
- makau.ai learner data: time-on-task vs score (are they correlated?)
- Any two sensor streams from the M5Stack lab (T vs P, V vs I)
- Public datasets: UCI Machine Learning Repository (hundreds of paired datasets)

### EQ-0109 Chi-Square Test: χ² = Σ(Oᵢ − Eᵢ)²/Eᵢ
**Data needed:** Observed vs expected frequency counts.
**Data type:** `{categories: str[], observed: int[], expected: float[]}`
**Sources:**
- makau.ai event type distribution: are events uniformly distributed?
- Survey data: response distributions vs null hypothesis
- Dice/coin experiment data (M5Stack RNG → simulated rolls → chi-square)

### EQ-0110 ANOVA F-statistic: F = MS_between/MS_within
**Data needed:** Grouped numeric observations.
**Data type:** `{groups: {group_name: str, values: float[]}[]}`
**Sources:**
- makau.ai learner scores grouped by classroom/teacher/method
- Lab sensor readings grouped by experimental condition
- Agricultural yield data (classic ANOVA application)

### EQ-0111 Weber-Fechner Law: S = k·ln(I/I₀)
**Data needed:** Stimulus intensity + perceived sensation magnitude.
**Data type:** `{stimulus_intensity: float, perceived_magnitude: float}[]`
**Sources:**
- M5Stack light sensor (vary LED intensity via DAC) + human response (button press on perceived "brightness level") — this IS testable with the lab hardware!
- Sound volume experiments: vary speaker power, record perceived loudness
- makau.ai learner difficulty perception vs actual difficulty level

### EQ-0112 Student's t-test: t = (x̄ − μ)/(s/√n)
**Data needed:** A sample from a population with known or hypothesized mean.
**Data type:** `{sample: float[], hypothesized_mean: float}`
**Sources:**
- Any sensor stream: "is the mean reading significantly different from the expected value?"
- makau.ai learner scores: "is this cohort different from the historical average?"

### EQ-0113 Logistic Regression: P(Y=1) = 1/(1+e^(−(β₀+β₁X)))
**Data needed:** Binary outcome data with one or more predictors.
**Data type:** `{X: float[], y: int[]}` where y ∈ {0, 1}
**Sources:**
- makau.ai learner data: {features} → pass/fail
- Medical datasets: {features} → diagnosis
- makau.ai intervention data: {features} → learner_unstuck (yes/no)

### EQ-0114 Signal Detection Theory: d' = z(Hit Rate) − z(False Alarm Rate)
**Data needed:** Hit rate and false alarm rate from a detection task.
**Data type:** `{hits: int, misses: int, false_alarms: int, correct_rejections: int}`
**Sources:**
- makau.ai security alerts: true positive vs false positive rates
- makau.ai compliance gates: detection performance of automated checks
- Any classification system's confusion matrix

---

## Linguistics (2 equations)

### EQ-0134 Zipf's Law: f(r) ∝ r^(−s), s ≈ 1
**Data needed:** Word frequency distribution from a text corpus.
**Data type:** `{word: str, rank: int, frequency: int}[]`
**Sources:**
- makau.ai knowledge base: word frequencies in ingested documents
- Project Gutenberg (free full-text books)
- Wikipedia dumps (freely available)
- makau.ai chat/event logs: word frequency in learner messages

### EQ-0135 Heaps' Law: V(n) = K·n^β, β ≈ 0.4–0.6
**Data needed:** Vocabulary size as a function of text length.
**Data type:** `{n_tokens: int, unique_words: int}[]` at increasing n
**Sources:**
- Same text corpora as Zipf: process incrementally, count unique words at each step
- makau.ai knowledge base: vocabulary growth curve as documents are ingested

---

## Political Science (2 equations)

### EQ-0136 Median Voter Theorem: x* = median{xᵢ}
**Data needed:** Voter preference distributions on a single policy dimension.
**Data type:** `{voter_id: str, preferred_position: float}[]`
**Sources:**
- Survey data: voter ideology scores (ANES, PEW, Gallup)
- makau.ai learner preferences: preferred difficulty level (a policy-space analog)
- Simulated elections with known preference distributions

### EQ-0137 Arrow's Impossibility Theorem
**Data needed:** Ranked preference ballots from 3+ voters over 3+ alternatives.
**Data type:** `{voter_id: str, ranking: str[]}[]` (ordered list of alternatives)
**Sources:**
- Ranked-choice voting datasets (FairVote, municipal election records)
- makau.ai: ranked preferences for lab activities or learning paths
- Synthetic: generate preference profiles, test every SWF for U/P/I/D violations

---

## Summary: Data Types Needed

| Data type | Equations it unlocks | Best source |
|-----------|---------------------|-------------|
| **Time series (numeric)** | Fourier Transform, CLT, Laplace, FTC, gradient descent, Big-O | makau.ai sensor streams, financial APIs |
| **Frequency distributions** | Shannon entropy, Zipf, Heaps, chi-square | makau.ai event logs, text corpora |
| **Paired observations (x,y)** | Pearson correlation, logistic regression, ANOVA, t-test | makau.ai learner data, UCI datasets |
| **Financial market data** | Black-Scholes, CAPM, Fisher equation, supply-demand | Yahoo Finance, FRED, World Bank APIs |
| **National economic data** | GDP, Cobb-Douglas, Solow, Phillips Curve | World Bank, FRED, Penn World Table |
| **Graph/network data** | PageRank, Nash equilibrium | makau.ai CORE topology, citation networks |
| **Text corpora** | Zipf, Heaps, Shannon entropy (on text) | Project Gutenberg, Wikipedia, makau.ai KB |
| **Classification results** | Cross-entropy, softmax, signal detection (d'), Bayes | makau.ai agent predictions, ML model outputs |
| **Neural network internals** | Backpropagation, attention mechanism | PyTorch hooks, makau.ai agent internals |
| **Cryptographic keypairs** | RSA encryption | Generated programmatically |
| **Voting/preference data** | Median voter, Arrow's theorem | Survey data, ranked-choice elections |
| **Stimulus-response data** | Weber-Fechner | M5Stack DAC + light sensor + human subject |

---

## What makau.ai Already Has

Based on the makau.ai capability report, these data sources
are ALREADY AVAILABLE without new integration:

| makau.ai source | Equations it feeds |
|-----------------|-------------------|
| Sensor readings (GET /api/events/?event_type=sensor:reading) | FTC, Fourier Transform, CLT (batched sensor data) |
| Event archive (80+ types, timestamped) | Shannon entropy, Zipf (event type distribution), chi-square |
| Learner profiles + assessments | Bayes, Pearson, ANOVA, t-test, logistic regression, signal detection |
| Agent orchestrator logs | Gradient descent (convergence curves), Big-O (task time vs size) |
| CORE network topology | PageRank (router graph), network dynamics |
| Packet captures | Fourier Transform (inter-arrival times), Shannon entropy (protocol distribution) |
| Knowledge base (RAG) | Zipf, Heaps (word frequencies in ingested docs) |
| Dashboard stats + timelines | Time series for any statistical equation |
| Compliance dossiers | Signal detection (gate pass/fail rates) |
| Intervention history | Bayes (hint given → outcome), logistic regression |
