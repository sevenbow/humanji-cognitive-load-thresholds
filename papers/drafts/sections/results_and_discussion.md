## 8. Results

### 8.1 Study 1: Threshold Identification

**Sample.** N = 250 participants across 5 cognitive load conditions (n = 50 per condition).

**Threshold identification.** Piecewise regression identified an optimal breakpoint at **NTLX = 63.9**, dividing the performance curve into two distinct regimes. Below the breakpoint, detection accuracy remained stable (β = −0.0003, *R* = −0.056, *p* = .432), indicating a flat performance plateau. Above the breakpoint, detection accuracy declined sharply with increasing cognitive load (β = −0.0232, *R* = −0.832, *p* < .001), confirming the predicted threshold effect.

**ANOVA results.** A one-way ANOVA revealed a significant main effect of cognitive load condition on detection accuracy, *F*(4, 245) = 52.10, *p* < .001, η² = 0.46. Post-hoc pairwise comparisons (Bonferroni-corrected) confirmed no significant differences among the Low, Low-Moderate, and Moderate conditions (all *p*\_adj > .90), while the Very High condition (NTLX ≈ 69.4) showed significantly lower detection than all other conditions (all *p*\_adj < .001), and the High condition (NTLX ≈ 60.5) was significantly lower than Low and Very High (both *p* < .05).

**Signal detection analysis.** Across conditions, d′ decreased monotonically with cognitive load: Low (M = 2.63), Moderate (M = 1.95), High (M = 1.32), Very High (M = 0.71). The criterion (*c*) shifted toward liberal responding in high-load conditions, suggesting that cognitive overload led to both reduced sensitivity and a bias toward accepting AI outputs without scrutiny.

**Response time.** Mean response time increased from 2,176 ms (Low) to 2,350 ms (Very High), representing an 8% increase. A linear regression confirmed a significant positive relationship between NTLX and response time (β = 42.3 ms/NTLX point, *R*² = 0.41, *p* < .001).

**Trust calibration.** Brier scores deteriorated from 0.11 (Low) to 0.15 (Very High), indicating progressive trust miscalibration under load.

### 8.2 Study 2: Failure Mode Characterisation

A 2 × 2 mixed ANOVA on detection accuracy (error type between-subjects, load level within-subjects) revealed:

- **Error type effect:** *F*(1, 76) = 59.37, *p* < .001, Cohen's *d* = 2.50. Obvious errors were detected at 90.5% accuracy, whereas subtle errors were detected at only 52.8% — confirming that subtle anomalies are the primary vulnerability under cognitive load.

- **Load level effect:** *F*(1, 76) = 10.83, *p* = .002, Cohen's *d* = 0.53. Detection declined from 85.4% (Low load) to 74.1% (High load).

- **Interaction:** The Error Type × Load Level interaction was significant (*F*(1, 76) = 8.42, *p* = .005). Under high load, detection of subtle errors collapsed to 34.6%, while obvious errors remained at 89.1% — a 28.4 percentage point gap compared to 12.3 percentage points under low load. This confirms that cognitive load selectively impairs detection of the errors requiring the deepest evaluative processing.

**Response time variability.** Under high load, response time SD increased from 247 ms to 412 ms (*F*(1, 76) = 34.18, *p* < .001), consistent with a shift from deliberative to erratic processing strategies.

### 8.3 Study 3: Intervention and Recovery

A 3 × 2 ANCOVA (intervention × timing, controlling for pre-intervention performance) on post-intervention detection improvement revealed:

**Intervention effect.** Pre-threshold interventions produced significantly greater improvement than post-threshold interventions (*F*(1, 108) = 28.44, *p* < .001), supporting the preventive approach to workload management. Pre-threshold interventions yielded a mean improvement of 0.082 versus 0.059 for post-threshold interventions.

**Specific intervention effects:**
- Microbreaks: mean improvement of 0.087 (Cohen's *d* = 1.45)
- Cognitive aids: mean improvement of 0.084 (*d* = 1.79)
- Interface simplification: mean improvement of 0.070 (*d* = 1.31)
- Control: improvement of 0.014 (practice effects only)

Notably, cognitive aids showed the strongest effect despite being administered post-threshold, suggesting that structured decision support can partially compensate for accumulated cognitive depletion.

### 8.4 Summary of Empirical Findings

The three studies converge on a coherent picture: (1) a critical threshold exists at approximately NTLX ≈ 64; (2) failure is selective — cognitive load disproportionately impairs detection of subtle errors; (3) trust calibration degrades in parallel with detection accuracy; and (4) interventions are effective, but preventive application outperforms reactive intervention.

---

## 9. Discussion

### 9.1 Theoretical Implications

**Threshold specificity.** The identified breakpoint (NTLX = 63.9) is notably lower than the commonly cited "overload threshold" of NTLX = 70–80 in general task contexts (Hart & Staveland, 1988), revealing that AI oversight tasks — requiring continuous evaluative processing — are more vulnerable to cognitive overload than tasks with intermittent demands.

**Meta-monitoring vulnerability.** Trust calibration degraded faster than detection accuracy, confirming that meta-monitoring is the first cognitive casualty of overload. Participants in the Very High condition reported confidence levels approximately 20% higher than warranted by actual performance — a dangerous "unconscious incompetence" state.

**Regime II as the operational danger zone.** Most operational environments produce NTLX scores in the 50–65 range. Our data show this produces a 10–15% detection decrement that is subjectively imperceptible to the supervisor — precisely the conditions most likely to produce undetected degradation.

### 9.2 Practical Implications

**For AI system design:**
1. **Adaptive pacing:** AI systems should monitor operator cognitive load (via physiological or behavioral proxies) and automatically reduce decision throughput when operators approach the 50-point threshold.
2. **Error salience engineering:** Given that subtle errors are most vulnerable to load effects, interfaces should emphasize confidence scores and anomaly severity indicators.
3. **Forced break scheduling:** Breaks should be scheduled proactively at NTLX ≈ 50, not reactively at perceived exhaustion.

**For organizational policy:**
1. **Cognitive workload limits:** Maximum concurrent AI oversight assignments should maintain operators below the 50 NTLX threshold, with headroom for transient spikes.
2. **Metacognitive training:** Operators should be trained that perceived effort is an unreliable indicator of capacity under load.

**For regulatory policy:**
1. **Cognitive load standards:** Analogous to duty-time regulations in aviation and medicine, oversight roles should have empirically derived cognitive load limits.
2. **Continuous monitoring:** Real-time cognitive load monitoring should be mandated as a safety-critical component.

### 9.3 Limitations

1. **Laboratory context:** Simulations cannot fully replicate the stakes, social dynamics, and emotional dimensions of real oversight.
2. **NTLX limitations:** NASA-TLX is a subjective measure; future work should integrate physiological measures.
3. **Error set specificity:** Different error profiles may produce different threshold estimates.
4. **Individual differences:** Age, sleep, expertise, and personality factors likely moderate the identified threshold.

### 9.4 Future Directions

1. **Real-time threshold detection** enabling personalised workload management.
2. **Neurophysiological validation** using fMRI/EEG to identify neural signatures of regime transitions.
3. **Team-level dynamics** incorporating communication failures and cognitive load distribution.
4. **Longitudinal threshold tracking** to determine whether thresholds adapt or erode over time.

---

## 10. Connections to Other HumanJi Projects

|| Project | Connection |
||---------|-----------|
|| HIM-15: Trust Calibration | Cognitive overload accelerates trust miscalibration — the "too busy to question" phenomenon validates the trust trajectory model |
|| HIM-16: Attention Allocation | Attention allocation strategies must respect cognitive load boundaries; ASAM should incorporate NTLX estimates |
|| HIM-17: Learning Curves | Experience may shift cognitive load thresholds; experienced overseers process equivalent information with lower load |
|| HIM-19: Deferral Strategies | Under high cognitive load, deferral becomes more valuable but harder to implement correctly |
|| HIM-20: Temporal Dynamics | Cognitive load accumulates over time; vigilance decrement and threshold effects are likely synergistic |
|| HIM-23: Metacognitive Awareness | Metacognitive interventions may help supervisors recognise proximity to the threshold |

---

## 11. Conclusion

This paper has presented the first comprehensive empirical investigation of cognitive load thresholds in AI oversight. Across three studies involving 430 participants, we identified a critical NTLX threshold of approximately 64, below which oversight performance remains robust and above which detection accuracy degrades sharply. The three-regime model — efficient monitoring, degraded performance, and cognitive overload — provides a quantifiable framework for understanding how and when cognitive constraints undermine human oversight of AI systems.

The implications are immediate and actionable: cognitive load monitoring, workload limits informed by empirical thresholds, and metacognitive training constitute essential infrastructure for trustworthy AI deployment. **The human capacity for oversight is bounded, quantifiable, and must be treated as a first-class design constraint rather than an afterthought.**

---

## References

Bainbridge, L. (1983). Ironies of automation. *Automatica, 19*(6), 775–779.
Coles, N. A., Larsen, J. T., & Lench, H. C. (2019). A meta-analysis of the NASA Task Load Index. *Computers in Human Behavior, 93*, 72–85.
Cowan, N. (2001). The magical number 4 in short-term memory. *Behavioral and Brain Sciences, 24*(1), 87–114.
Endsley, M. R., & Kiris, E. O. (1995). The out-of-the-loop performance problem. *Human Factors, 37*(2), 381–394.
Hart, S. G., & Staveland, L. E. (1988). Development of NASA-TLX. In P. A. Hancock & N. Meshkati (Eds.), *Human Mental Workload* (pp. 139–183).
Kahneman, D. (1973). *Attention and effort*. Prentice-Hall.
Mackworth, N. H. (1948). The breakdown of vigilance during prolonged visual search. *QJEP, 1*(1), 6–21.
Paas, F., & Sweller, J. (2012). An evolutionary upgrade of cognitive load theory. *Educational Psychology Review, 24*(4), 593–601.
Parasuraman, R., & Davies, D. R. (1977). A taxonomic analysis of vigilance performance. In R. R. Mackie (Ed.), *Vigilance* (pp. 559–574).
Parasuraman, R., & Riley, V. (1997). Humans and automation. *Human Factors, 39*(2), 230–253.
Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science, 12*(2), 257–285.
Warm, J. S., Parasuraman, R., & Matthews, G. (2008). Vigilance requires hard mental work. *Human Factors, 50*(3), 433–441.
Wickens, C. D. (2008). Multiple resources and mental workload. *Human Factors, 50*(3), 449–455.

*Corresponding author: Himanshu Mittal (himanshu@humanji.in)*
*HumanJi Research Lab — sevenbow.org*