# **Eldorian Abridged Dictionary: Lexicographical Style Guide**

Version: 2.7

Status: Active Standards

Scope: English-to-Eldorian / Eldorian-to-English Bilingual Entries

## **1. General Formatting Constraints**

* **Single-Paragraph Entry:** Every entry must be a single, continuous block of text without line breaks.  
* **No Headers or Meta-Labels:** Do not include markdown headers (e.g., ### Word), classification titles, or "Type" labels above or within the entry. The entry must consist *solely* of the formatted paragraph.  
* **Character Limits:** Maintain a soft limit of **500 characters** per entry. Prioritize brevity, but include necessary context for translation.  
* **Typography & Highlights:**  
  * **Bold:** Used exclusively for the **Headword** at the start of the entry. Do *not* use a colon separator.  
  * *Italics:* Used for *IPA transcriptions*, *grammatical abbreviations* (PoS), *metadata tags*, and *Eldorian terms* appearing within English sentences.  
  * **Small Caps + Serif Font + Bold:** Used exclusively for the **Primary English Translation**. This differentiates the "printed" meaning from the "handwritten" (Corsiva) text and adds weight to the small caps.  
    * *Implementation:* Use inline HTML: <span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">word</span>.  
  * **Plain Font:** Used for English descriptive notes, definitions, usage examples, and etymology brackets.

## **2. The Metadata Stack**

Immediately following the phonetic transcription, provide the grammatical "tags" in italics, separated by commas and ending with a period.

1. **Part of Speech:** *n., v., adj., adv., num., pron., prep.*  
2. **Grammatical Gender:**  
   * *c.* (Celestial)  
   * *w.* (Worldly)  
3. **Elemental Affiliation:**  
   * *ea.* (Earth)  
   * *ai.* (Air)  
   * *fi.* (Fire)  
   * *wa.* (Water)

**Note on Schema Codes:** While the drafting process uses Schema types (T1, T2, T3, TS) to categorize word complexity, these codes **must not appear** in the final public-facing entry.

## **3. Lexicographical Content Rules**

* **The Translation Anchor:** The primary meaning must be the first non-italicized text after the metadata stack, formatted in **Small Caps** (lowercase letters) using a distinct **Bold Serif** font.  
* **Meaning Neutrality:** The gender and element are grammatical traits, not definitions. Do not explain them in the text unless they create a specific idiomatic exception (e.g., "In the Fire element, this implies anger").  
* **No Meta-Description:** Do not describe the classification logic or content rules within the entry (e.g., do not state "This is a workhorse word"). Let the content speak for itself.  
* **Contextual Completeness:**  
  * **Collocations:** For high-frequency words, focus on common pairings rather than explaining simple concepts. (e.g., For "To Give," list "give honor," "give thanks").  
  * **Sequence Definitions:** For system words (Numbers/Days), briefly define their place (e.g., "The number following six").  
  * **Implicit Variations:** Include natural extensions of the word where necessary (e.g., providing the **ordinal form** for a number), even if not strictly required by a specific rule.  
* **Eliminate Redundancy:** Avoid phrases like "This word means..." or "As a verb...". Let the formatting and tags do the work.  
* **Sense Discrimination:** Use brackets to distinguish homonyms or specific domains.  
  * *Example:* **Bank** ... <span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">bank</span> [Finance] vs. [Geography].

## **4. Orthography and Conjugation**

* **The Hyphen Rule:** Hyphens are morphological indicators for suffixes (e.g., *-esse*) or prefixes only. They **must never appear** in the final, defined Eldorian headword.  
* **Verb Conjugation:** List only relevant forms that deviate from the standard or are frequently used.  
  * *Standard Codes:* *inf.* (informal), *form.* (formal), *hon.* (honorific), *subj.* (subjunctive), *abst.* (abstract).

## **5. Entry Sequence**

Entries must strictly follow this linear sequence:

1. **Headword** (Bold)  
2. *Phonetics* (Italicized IPA enclosed in slashes /.../)  
3. *Metadata Stack* (Italics: PoS, Gender, Element)  
4. Primary Translation (Small Caps <span>)  
5. Descriptive Gloss / Context (Plain text)  
6. *Derivatives / Plurals / Forms* (Italicized labels; e.g., *pl.* Word)  
7. Usage Example (One English sentence with the *italicized* Eldorian word)  
8. [Etymology] (Square brackets; use < for "derived from").

## **6. Style Examples**

**Markdown Code:**

```

**Kishad** */kɪˈʃæd/ n., w., ea.* <span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">head</span>. Refers specifically to a humanoid head; *pl.* Kishadai; *adj.* Kishadan. "The guard wore a heavy iron helmet to protect his *kishad*." [< OE. Oellihidkhu + OD. Zraudaklur]

```

Rendered:

**Kishad** */kɪˈʃæd/ n., w., ea.* **head**. Refers specifically to a humanoid head; *pl.* Kishadai; *adj.* Kishadan. "The guard wore a heavy iron helmet to protect his *kishad*." [< OE. Oellihidkhu + OD. Zraudaklur]

**Markdown Code:**

```

**Helgothlad** */ˈhɛl.ɡɒθ.læd/ n., c., ai.* <span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">culture</span>. The shared beliefs and traditions defining a society; *pl.* Helgothladai; *v.* Helgothlas. "The *helgothlad* of the elves is famously rich in music." [< OE. Halen'gothlad]

```

Rendered:

**Helgothlad** */ˈhɛl.ɡɒθ.læd/ n., c., ai.* **culture**. The shared beliefs and traditions defining a society; *pl.* Helgothladai; *v.* Helgothlas. "The *helgothlad* of the elves is famously rich in music." [< OE. Halen'gothlad]

**Markdown Code:**

```

**Affe** */ˈæfeɪ/ v., w., fi.* <span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">to give</span>. *n.* Affa (gift); *pl.* Affai; *form.* affen; *hon.* affetal; *affe affa* (give a gift); *affe vardis* (give honor). "The generous patron decided to *affe* a fortune to the library." [< OD. bakka → baffae]

```

Rendered:

**Affe** */ˈæfeɪ/ v., w., fi.* **to give**. *n.* Affa (gift); *pl.* Affai; *form.* affen; *hon.* affetal; *affe affa* (give a gift); *affe vardis* (give honor). "The generous patron decided to *affe* a fortune to the library." [< OD. bakka → baffae]

**Markdown Code:**

```

**Hethan** */ˈhɛθ.ən/ num., c., wa.* <span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">seven</span>. The cardinal number following six; *ord.* hethana (seventh); *hethan aman* (seven loves). "A true leader is recognized for possessing *hethan* noble virtues." [< CE. hethan]

```

Rendered:

**Hethan** */ˈhɛθ.ən/ num., c., wa.* **seven**. The cardinal number following six; *ord.* hethana (seventh); *hethan aman* (seven loves). "A true leader is recognized for possessing *hethan* noble virtues." [< CE. hethan]

## **7. Automated Validation Protocols (Appendix)**

To ensure data integrity, entries should be validated against the following logic.

### **7.1 Logical Schema (JSON)**

Conceptually, every entry must parsable into this JSON structure:

```
{
  "headword": "String (Bold)",
  "phonetics": "String (IPA format)",
  "metadata": {
    "pos": "Enum (n., v., adj., adv., num., etc.)",
    "gender": "Enum (c., w.)",
    "element": "Enum (ea., ai., fi., wa.)"
  },
  "translation": "String (Small Caps + Serif + Bold)",
  "definition": "String",
  "forms": "Array<String> (Optional)",
  "example": "String (Must contain headword in italics)",
  "etymology": "String (Bracketed)"
}
```

### **7.2 Regex Validator**

Use this Regular Expression to validate the **start** of any entry (Headword through Translation). This checks for Bold, IPA, correct Metadata order, and the specific HTML Span with font styling.

```

^\*\*([A-Z][a-zA-Z]+)\*\* \*/.*?/ ([a-z]{1,4}\.,) ([cw]\.,) ([a-z]{2}\.)\* <span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">[^<]+</span>\.

```

**Breakdown of Validator:**
^\*\*([A-Z][a-zA-Z]+)\*\*: Starts with BoldedHeadword.
\*/.*?/: Followed by space and /ItalicIPA/.
([a-z]{1,4}\.,): Followed by space and Part of Speech (e.g., n.,).
([cw]\.,): Followed by space and Gender (c., or w.,).
([a-z]{2}\.): Followed by space and Element (ea., wa., etc.). Updated for 2-letter code.
\*: Followed by the closing asterisk for the italics block.
<span style="font-variant: small-caps; font-family: Georgia, serif; font-weight: bold;">[^<]+</span>\.: Followed by the HTML span for the translation (including font family and bold weight), ending in a period.