# Response to Reviewer

**Manuscript:** Post-Quantum Attribute-Based Verifiable Data Storage and Retrieval for Cloud Computing Environments (PQ-ABDSRS)

We thank the reviewer for an unusually detailed and accurate report. The review identified a root cause that we had not seen and that explains a large fraction of the individual comments, and it correctly identified several places where the construction did not support the claims made for it. The manuscript has been reconstructed rather than edited. This document responds point by point.

---

## 0. Root cause of the missing symbols

The reviewer flagged blank domains, blank algorithm names and blank entity abbreviations on pages 5, 6, 7, 8, 9, 10, 11–13 and 14, and treated them as separate critical items.

They have a single cause. The source used 26 custom macros (`\Zq`, `\PP`, `\MK`, `\KGC`, `\TGC`, `\DO`, `\DU`, `\Adv`, `\Chal`, `\LWE`, `\SIS`, `\negl`, `\poly`, `\TrapGen`, `\SamplePre`, `\Commit`, `\Open`, `\Setup`, `\KeyGen`, `\Enc`, `\Sign`, `\Verify`, `\Test`, `\Transform`, `\Z`, `\R`) that were **never defined anywhere in the preamble**. Compiling the original source produces **288 "Undefined control sequence" errors**, and every one of those 288 occurrences typeset as nothing.

A macro definition block has been added at the top of the source, with a comment explaining why it must not be removed. The revised source compiles with **zero** undefined control sequences. Every symbol the reviewer listed as missing is now visible.

---

## A. Critical mathematical and technical corrections

| Review item | Action taken |
|---|---|
| Abstract 14–17: components not completely defined | Abstract rewritten. The construction is now explicitly modular: Section 4 defines the CP-ABE, KP-ABE and ABS interfaces with syntax, correctness and the exact security property consumed, and names the cited instantiation of each. Table 2 lists every guarantee inherited rather than proved here. |
| Abstract 18–20: "formally define and reduce" too strong | Wording changed. The abstract now states what is proved (IND-CPA, EUF-CMA, verifiability, signer privacy, IND-CKA, classical ROM) and Section 1.3 lists what is not claimed. All proofs are now complete game sequences with explicit advantage bounds, not sketches. |
| Abstract 21–26: size claims based on incomplete calculations | All numerical claims recalculated from complete serialized objects and revised sharply upward. The five-to-six-orders and 80–320× figures are removed. |
| p.2 51–52: "every algorithm … is instantiated over pairings" | Replaced with "The security-critical public-key components … are instantiated over groups equipped with a bilinear pairing", followed by a sentence noting that hashing, policy reconstruction and symmetric operations are not pairing operations. |
| p.2 55–58: Shor's algorithm claim | Rewritten: Shor invalidates the underlying discrete-logarithm assumptions; the algorithms remain well defined but no security guarantee survives. Absolute language removed. |
| p.3 92–96: "IND-CPA/CCA2 analogue" ambiguous | Resolved to **IND-CPA**. Remark 3 states plainly that the earlier IND-CCA2 claim did not follow, that no CCA transform was applied and no decryption-oracle simulation was given, and points to the Fujisaki–Okamoto route as future work. |
| p.3 94–96: QROM claimed without QROM reduction | All QROM claims removed. Section 1.3 states that random-oracle programming does not extend to superposition queries and cites Boneh et al. and Zhandry. Everything is now stated in the classical ROM. |
| p.4 130–131: [18,19] misattributed as general MSP | Corrected throughout. [19] (Tsabary) is described as *t*-CNF and [18] (Zhang–Zhang–Ge) as AND-gates with wildcards, both in the text and in explanatory notes appended to the bibliography entries. The scheme's policy class was changed to monotone DNF, which those constructions can actually support, and Section 3.6 states that arbitrary-MSP lattice CP-ABE is open. |
| p.4 142–144: [24,25] are homomorphic authenticators, not the commitment | The homomorphic commitment has been **removed from the construction** (see below). [24] and [25] are now cited only for what they actually are, and a note to that effect appears in the bibliography. Kawachi–Tanaka–Xagawa and Baum et al. are cited where a SIS commitment is discussed in Remark 1. |
| p.4 Table 1: unjustified checkmarks | Every property now has a footnote definition (a–i). The PQ-ABDSRS row carries two explicit qualifiers: policy class restricted to DNF, and keyword privacy at the generic-name level. |
| p.4 149–152: unsupported novelty claim | Changed to "Among the schemes compared here…". |
| p.5 Definitions 1–4: missing domains | Fixed by the macro block. Definitions 1–4 (lattice, discrete Gaussian, LWE, SIS) now display every domain, and the notation subsection defines ℤ, ℝ, ℕ⁺, ℤ_q, negl, poly explicitly. |
| p.5 Def. 3: secret domain missing; `m` overloaded | Domain restored. A sentence now states that the LWE sample count coincides with the trapdoor width and introduces `m_s` for the case where they must differ. |
| p.5 Def. 3: error distribution and parameter regime unspecified | Now stated: χ = D_{ℤ,αq} with αq ≥ 2√n, with the Regev regime and the note that the reduction is quantum, plus Peikert's classical reduction for large moduli. |
| p.5 Def. 4: SIS norm not identified | Now ℓ₂ throughout, with the condition q ≥ β·Õ(√n) and the concrete β values tabulated in Table 5. |
| p.5 Def. 5: TrapGen name missing | Restored as TrapGen(1ⁿ,1^m,q), with the Alwen–Peikert bound m ≥ (1+δ)n log q and δ = 1 fixed. |
| p.5 Def. 6: SamplePre name and domains missing | Restored in full: input matrix width w, target, Gaussian condition σ ≥ ‖T̃‖·ω(√log w), output in ℤ^w, statistical distance negl(n), norm bound σ√w. |
| p.6 204–206: MSP satisfaction condition inverted | Corrected and made explicit: a_i = 0 for rows with ρ(i) ∉ A, with a sentence drawing attention to the direction. |
| p.6 Def. 7: incompatible dimensions | The homomorphic commitment is no longer part of the construction. Where it is discussed (Remark 1), all dimensions are given: B₁ ∈ ℤ_q^{n×k}, B₂ ∈ ℤ_q^{n×m}, B ∈ ℤ_q^{n×(k+m)}, x ∈ ℤ^k, r ∈ {0,1}^m. |
| p.6 Def. 7: Com/Open names and SIS symbols missing | Restored. |
| p.6 Def. 7: hiding never defined but privacy claimed | The privacy claim built on it is withdrawn. Remark 1 explains why binding alone was never enough (see next row). |
| p.6 Def. 7: randomness distribution left open | Fixed to r ∈ {0,1}^m in the remark. |
| **p.9–10: "a homomorphic commitment does not by itself prove correct execution"** | **This is the substantive change in the revision.** Remark 1 now argues the reviewer's point explicitly, and adds a second reason: binding holds only for *short* committed values, whereas the ciphertext components are close to uniform over ℤ_q^{2m}. The mechanism is replaced by (i) a SIS-based binding digest (Ajtai hash, Definition 8, collision-resistant by Lemma 1) computed by the data owner over each ciphertext component and carried **inside the signed header**, and (ii) a random-oracle preimage check on the search tag. Theorem 4 reduces Transform-verifiability to SIS collision resistance plus ABS unforgeability; Theorem 5 reduces Test-verifiability to one-wayness of H₅ plus ABS unforgeability. Both are complete reductions, not sketches. |
| p.6–7 Fig. 1 / Table 2: entity symbols blank | Fixed by the macro block; the figure caption also spells out KGC, TGC, DO, DU and CS in words. |
| p.7: "honest-but-potentially-malicious" contradictory | The cloud is now specified as **malicious**, with five enumerated permitted deviations and one stated availability assumption. Section 5.2. |
| p.7 245–251: entity names missing | Fixed. |
| p.8 Alg. 1: TrapGen, PP, MSK, domains, returns missing | Algorithm 1 rewritten with Require/Ensure blocks and every type given. |
| p.8 Alg. 1 line 8: hash functions described collectively | H₁ … H₅ now each have an individually stated domain and codomain, with the purpose of each in a comment. |
| p.8 Alg. 2: name, input, sampling missing | Algorithm 2 rewritten with both key modes and full types. |
| p.8 Alg. 2 lines 2–3: T_{A₀} used as a trapdoor for the wider A_A | Fixed with an explicit **ExtBasis** call (Definition 7, Cash et al. / Alwen–Peikert), and a paragraph stating that the earlier direct invocation was not valid. |
| p.8 Alg. 2: key width should be 2m, tables counted m | Corrected everywhere. Keys are vectors in ℤ^{2m}, and every size figure now uses 2m. |
| p.8–9 Algs. 3–4: not a complete CP-ABE; attribute matrices do not enter | Restructured. The CP-ABE is now a **named, cited building block** with a stated interface (Definition 9), instantiated with Zhang–Zhang–Ge for AND-clauses, invoked once per DNF clause. The attribute matrices enter through F_{S_j} = [A₀ ‖ Σ_{x∈S_j} A_x], which is the same matrix the decryption key inverts. |
| p.8 Alg. 3: a_i undefined; dropped from the final ciphertext | The per-row LWE sample vectors are gone; the offline phase now precomputes only the shared secret s, the noise vectors and the two random keys, all of which are used in the online phase. Nothing needed for decryption is dropped. |
| p.9 Alg. 4 line 6: XOR only valid for fixed-length strings | Replaced by **KEM–DEM**: the attribute layer encapsulates a uniform 256-bit key K; the payload is AEAD (AES-256-GCM) under H₃(K), with a 96-bit nonce, a 128-bit tag and the header as associated data. Cited to Cramer–Shoup, Rogaway and NIST SP 800-38D. |
| p.9 Alg. 4 line 7: Sign_lattice undefined; GPV is not an ABS | Replaced by a proper **ABS building block** (Definition 11) with unforgeability and signer privacy, instantiated with El Kaafarani–Katsumata. Section 4.3 states explicitly that a GPV signature does not meet the definition. |
| p.9 Alg. 4: P_s never checked against A_s | An explicit check `if P_s(A_s) = false then return ⊥` is now line 1 of the online signcryption algorithm, and the ABS proves satisfaction without revealing A_s. |
| p.9 Alg. 4 line 8: single cm vs per-row cm_i | Resolved by the redesign: there is one digest **d_j per clause**, all of them signed. |
| p.9 Alg. 5: trapdoor delegation missing | The keyword trapdoor is now a KP-ABE key (Definition 10), so no ad hoc delegation is performed. |
| p.9 Alg. 5: u′ from H₂(P_t) undefined | The keyword layer is redesigned around KP-ABE: the DO encrypts a random τ under the keyword-name set, publishes tag = H₅(τ), and Test is decrypt-and-compare. H₂ is retained in the parameter list with a stated codomain but the ad hoc target derivation is gone. |
| p.9 283–287: keyword privacy from "generic names" is not a proof | Section 6.4 now states precisely what the generic-name encoding gives (the cloud learns names and match outcomes, not values) and states that it is not attribute-hiding. Theorem 6 proves IND-CKA for keyword *values* under the KP-ABE's IND-CPA, with the scope of the theorem spelled out afterwards. |
| p.9 Alg. 6: name missing, a° undefined | Algorithm 7 (Test) is named and fully typed. The undefined a° is gone; the DRR now carries the clause index and the KP-ABE key. |
| p.9 Alg. 6 line 2: inconsistent reconstruction notation | One convention throughout: DNF clause selection via Idx(P,A), defined in Section 3.6. |
| p.9 Alg. 6 lines 3–4: cm_i never generated; type mismatch | Resolved by the redesign. |
| p.10 Alg. 7: TK, a°, r″, proof generation undefined | Algorithm 8 (Transform) is now a clause selection with fully typed output. The ill-typed inner product ⟨TK_{A_d}, a°⟩ is removed. |
| p.10 Alg. 7 line 4: type inconsistency with Alg. 2 | Removed. Section 6.4 notes the consequence of the new design: the cloud learns which clause the user satisfies, but never receives the user's decryption key. |
| p.10 Alg. 8: PK undefined; policies absent from CT_out | CT_out now carries the policies, keyword names, digests and tag, precisely because signature verification needs them, and these are included in the size accounting. |
| p.10 303–309: "same telescoping argument" is not a proof | Replaced by **Theorem 1 (Correctness)** with a full derivation and the explicit noise bound B_dec = σ√(2m)·αq√(2m) + αq√κ < q/4, which is what fixes the modulus in Section 9.1. |
| p.11–13: security-game symbols missing | Fixed by the macro block; all games rewritten. |
| p.11 Defs. 8–9: IND-CCA2 claimed without a transform | Reduced to IND-CPA. See Remark 3. |
| p.11 Lemma 2: LWE in the commitment key does not give confidentiality | Removed. Theorem 2 now reduces confidentiality to the CP-ABE's IND-CPA plus AEAD plus a random-oracle term, with an explicit three-game hybrid and a stated advantage bound. |
| p.12 Theorem 2: GPV EUF-CMA ≠ policy-based anonymous unforgeability | Theorem 3 now reduces to the **ABS** unforgeability game, which quantifies over keys for non-satisfying attribute sets. A paragraph after the proof explains why the GPV argument did not cover the game as defined. |
| p.12 399–405: "information-theoretic" DO privacy unsupported | Withdrawn. Lemma 2 gives a **computational** signer-privacy statement reduced to the ABS privacy property, and the text explains the flaw in the earlier argument: SamplePre's output is independent of the internal reconstruction vector but *not* of the matrix F_{A_s}, hence not of A_s. |
| p.13 Lemma 3: no keyword ciphertext components defined | The keyword ciphertext is now KP-ABE.Enc(W°, τ), and Theorem 6 is a two-game hybrid over that concrete object. |
| p.13 line 438: internal drafting note left in text | Deleted. |
| p.14 Tables 4–6: blank domains and operation names | Fixed by the macro block; the cost table (Table 9) is rebuilt from the final algorithms. |
| p.14 Table 5: costs not derived from complete algorithms | Table 6 now lists every operation, including ExtBasis, SamplePre, the digest evaluations, the ABS calls and the AEAD calls. "O(1) SP per key" is replaced by "1 ExtBasis + 1 SamplePre" with the width stated. |
| p.14 Table 6: "O(1) matrices" contradicts one A_x per attribute | Corrected: public parameters contain \|U\| + 2 attribute-layer matrices plus \|U°\| + 1 keyword-layer matrices, counted explicitly in Table 7. |
| p.15 Table 7: 94–165 B estimates omit components | Rebuilt. Table 8 gives a component-by-component breakdown showing that nothing is omitted. The totals are **5.54 MB to 18.07 MB**, i.e. 731–870× ABDSRS rather than smaller. |
| p.15 Table 7: a commitment in ℤ_q^n alone is ~1.7 KB | The reviewer's arithmetic was right and it is what exposed the problem. At the corrected parameters a vector in ℤ_q^n is 5,760 B, and it is counted. |
| p.15 464–466: "NIST Level-1-equivalent" asserted without an estimator | Section 9.1 now derives the parameter set and Table 5 reports primal-uSVP core-SVP costs with the estimator formula given in the text. **The reviewer's suspicion was well founded: the old set (n = 512, q ≈ 2²⁷) gives block size 140, i.e. 2⁴¹ classical and 2³⁷ quantum, not Level 1.** The parameter set has been corrected to n = 1536, q = 2³⁰, giving 2¹⁶⁴ classical and 2¹⁴⁹ quantum. The old m ≈ 6,900 was also wrong by a factor of ten (5n log₂q = 69,120). Both errors and their consequences are stated in the paper. We note in the caption that a full lattice-estimator run should be done before final submission; core-SVP is a lower-bound methodology. |
| p.16 §7.3: "Kyber-scale" misleading | Removed. |
| p.16 §7.3: [30] does not supply an ABE compression technique | Section 9.6 is now explicitly future work. It states that Ring-LWE (Lyubashevsky–Peikert–Regev) supplies no attribute-based construction and that none is attributed to it, adds Langlois–Stehlé for Module-LWE, and lists the three things that would have to be established first. |
| p.16 Table 8: ring replacement not shown to preserve security | PQ-ABDSRS-R has been **removed as an instantiated scheme**. It appears in no table and no figure. |
| p.17 Fig. 4 caption: PQ ciphertexts smaller than ABDSRS | Withdrawn. The figure is regenerated from complete serialized objects and shows PQ-ABDSRS roughly two orders of magnitude larger. Section 9.4 states in plain terms that the earlier claim was an artefact of the omissions. |
| p.17–18 Conclusion: overclaims | Rewritten. The conclusion states what was proved, at what notion, and reports the size gap as the main finding rather than as a favourable trade-off. |
| p.18 Data Availability: unrelated statement | Replaced with: "Data sharing is not applicable to this article as no new data were created or analyzed in this study." |
| p.18 Author contributions: software/validation/data curation | Removed; the CRediT roles now reflect a theoretical paper. |
| p.18 Funding: "Grant No. XXXX" | **Action still required from the authors.** We have not invented a grant number. The placeholder is now `<GRANT NUMBER>` with a LaTeX comment immediately above it giving both options: insert the approved King Faisal University grant number, or replace the statement with "This research received no external funding." |

---

## B. Language, notation and formatting

All items adopted:

- "data-owner anonymity" used consistently when adjectival.
- "Learning with Errors (LWE)-based" and "Short Integer Solution (SIS)-based".
- "potentially malicious cloud server".
- "ciphertext-policy attribute-based encryption (CP-ABE)" capitalised only at definition.
- "Theoretical and experimental comparison" removed; the contribution bullet now says concrete parameters and complete size accounting, and Section 1.3 states that no implementation is reported.
- "Gorbunov, Vaikuntanathan, and Wee" with serial comma.
- "independently of the attribute-based …".
- "PQ-ABDSRS is intended to provide …" (in fact the sentence was rewritten entirely).
- "Learning with Errors" standardised.
- lowercase "monotone span program" after definition.
- "if and only if" in formal prose; "iff" no longer used.
- Entity abbreviations restored before any grammatical editing (root cause above).
- Section heading now "Key generation".
- "online/offline" used consistently.
- "without the cloud's secret key" deleted; the cloud holds no secret key in PQ-ABDSRS, which is now stated.
- "data-retrieval and unsigncryption-verification oracle".
- Serial commas in enumerations.
- "big-O notation".
- "ip-1–ip-4".
- "Ring-LWE/Module-LWE" without spaces.
- "direct comparison" rather than "like-for-like".
- "Comparative size estimates".
- Future work clearly separated from established results, in Section 1.3 and again in Section 9.6.
- Reference titles standardised to sentence case, MDPI style, with LNCS volumes and publisher details added.
- Hyphenation of compound modifiers made consistent (attribute-based, cloud-side, search-result verification).
- Spacing inside |U| and A_d normalised; the macro block is what makes this stable.
- Algorithm names now use exactly the declared forms: Setup, KeyGen, Off-Signcrypt, On-Signcrypt, KwTrapGen, DRRGen, Test, Transform, Unsigncrypt-Verify.

Per author preference, the em-dash is not used in the running text.

---

## C. Reference and citation audit

| Ref | Action |
|---|---|
| [1] Bera et al. | DOI 10.1016/j.jisa.2023.103482 added. Metadata confirmed (J. Inf. Secur. Appl. 75:103482, 2023). |
| [2–3] | Retained; LNCS volume and publisher details added. |
| [4–14] | Retained. Every Table 1 checkmark now has a footnote definition, and the table is explicitly scoped to the schemes compared. |
| [15] Boyen | Cited for lattice attribute-based functional encryption only, not as the instantiated primitive. |
| [16] GVW13 | Now used for its actual content, the KP-ABE for Boolean formulas, which is the keyword layer's building block. It no longer stands behind the CP-ABE algorithms. |
| [17] ABB | Retained for lattice IBE. The delegation result needed for [A₀ ‖ ΣA_x] is now cited separately and precisely: Cash–Hofheinz–Kiltz–Peikert (Bonsai trees) and Alwen–Peikert, invoked as ExtBasis in Definition 7. |
| [18] Zhang–Zhang–Ge | Access structure now stated correctly (AND-gates with wildcards) in the text and in a note on the bibliography entry. No arbitrary-MSP construction is attributed to it. |
| [19] Tsabary CRYPTO 2019 | Corrected to *t*-CNF in the text and in a bibliography note. |
| [20] GPV | No longer cited as evidence of attribute-based authentication or anonymity. Section 4.3 states explicitly that GPV does not meet the ABS definition. |
| [21] Alwen–Peikert | The exact use is now named: the m ≥ (1+δ)n log q bound in Definition 5 and the ExtBasis result in Definition 7. |
| [22] Boyen 2010 | Retained as background. A direct lattice ABS reference is added: El Kaafarani–Katsumata (PKC 2018), with Tsabary (TCC 2017) as an alternative. |
| [23] Regev | The parameter regime is now stated (αq ≥ 2√n) and the reduction is identified as quantum, with Peikert (STOC 2009) added for the classical case. |
| [24] Gennaro–Wichs | **Corrected.** The entry is now "Fully homomorphic message authenticators", ASIACRYPT 2013, LNCS 8270, pp. 301–320, with a note that it constructs a symmetric-key homomorphic authenticator, not a commitment. (We verified the venue: it is ASIACRYPT 2013, not CRYPTO 2013; the page range 301–320 the reviewer quoted is correct.) It is no longer used as the source of any commitment. |
| [25] Gorbunov–Vaikuntanathan–Wichs | Retained as a homomorphic-signature reference only. Kawachi–Tanaka–Xagawa and Baum et al. are added and cited where a SIS commitment is discussed. |
| [26] Boneh et al., random oracles in a quantum world | Now cited for the *negative* point, that ordinary ROM programming does not lift to the QROM. Zhandry (CRYPTO 2012) added. |
| [27–29] | Table 1 entries re-checked and footnoted. |
| [30] Lyubashevsky–Peikert–Regev | Cited only as the Ring-LWE foundation. Langlois–Stehlé added for Module-LWE. Section 9.6 states that neither supplies the attribute-based construction the earlier version implied. |
| [31] Shor | No change. |
| New | Ajtai (STOC 1996), Micciancio–Peikert (EUROCRYPT 2012), Boneh et al. (EUROCRYPT 2014), Hofheinz–Hövelmanns–Kiltz (TCC 2017), Cramer–Shoup, Rogaway (CCS 2002), NIST SP 800-38D, Albrecht–Player–Scott, Alkim et al. (USENIX 2016). |

---

## Summary against the reviewer's ten next steps

1. **Restore every missing symbol and algorithm name.** Done; root cause fixed, 288 → 0 undefined macros.
2. **Choose and reproduce one complete lattice CP-ABE.** Done as a named cited building block with a stated interface, instantiated with Zhang–Zhang–Ge, and the policy class narrowed to what that construction supports.
3. **Add a genuine policy-based anonymous signature.** Done via an ABS building block (El Kaafarani–Katsumata) with an explicit policy check.
4. **Formally define the keyword encryption/token/test relation.** Done via KP-ABE plus a random-oracle tag check.
5. **Replace the commitment sketch.** Done; replaced by a SIS binding digest inside the signed header, with the reviewer's objection to the commitment argued explicitly in Remark 1.
6. **Prove correctness before security.** Done; Theorem 1 with the noise bound, which now drives the choice of q.
7. **Reduce claims to IND-CPA and classical ROM.** Done.
8. **Recalculate all tables and figures.** Done from complete serialized objects; figures regenerated.
9. **Remove or clearly label the Ring/Module-LWE instantiation.** Removed as an instantiated scheme; retained only as labelled future work with no numbers presented as results.
10. **Correct [24], the data availability statement and the funding placeholder.** [24] and the data availability statement are corrected. The funding placeholder is flagged for the authors and has not been invented.

## A further error found after the revision

While building the reproduction code that accompanies this revision, its test suite caught a mistake introduced during the rewrite. The decryption-error bound had been evaluated with Cauchy–Schwarz, |⟨e_A, e_j⟩| ≤ ‖e_A‖·‖e_j‖, rather than with the correct Gaussian tail bound |⟨e_A, e_j⟩| ≤ ‖e_A‖·αq·ω(√log n). The looser form overestimates the error by about 34×, roughly five bits of modulus, and evaluating it correctly showed that q = 2²⁷ does not satisfy q/4 > B_dec at these dimensions.

The parameter set is now **n = 1536, q = 2³⁰, m = 92,160, σ = 1024**, giving 2¹⁶⁴ classical and 2¹⁴⁹ quantum core-SVP with a correctness margin of 2³·⁹. Theorem 1, Equation (2), Table 5, Table 7, Table 8 and both figures were regenerated from the corrected set. A regression test now pins this so the two bounds cannot be confused again.

## Two items the authors must still close

1. **Grant number.** Not invented. See the comment above `\funding{}` in the source.
2. **Lattice estimator.** Table 5 reports primal-uSVP core-SVP estimates computed from the standard 2016 methodology. A run of the current lattice estimator (including dual and hybrid attacks) should be substituted before final submission. The parameter set has margin, so we do not expect the conclusion to change, but the numbers should be the estimator's rather than ours.
