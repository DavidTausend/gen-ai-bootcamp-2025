# German Vocabulary Extraction Guidelines

## Overview
Extract **all German vocabulary** from the provided text. Each word should be structured with **its base form, phonetic representation, and meaning**.

---

## **Extraction Rules**

### **1. Extract Every Word from the Text**
Include the following word types:
- **Nouns** (*Substantive*)  
- **Verbs** (*Verben*)  
- **Adjectives** (*Adjektive*)  
- **Adverbs** (*Adverbien*)  

### **2. Ignore Grammatical Elements**
Do **not** include:
- **Conjunctions** (e.g., *und, oder, aber*)  
- **Prepositions** (e.g., *auf, in, mit, über*)  
- **Auxiliary verbs** (e.g., *haben, sein, werden*)  

### **3. Convert Words to Their Base Form**
- Convert **plural nouns** to singular (e.g., *Häuser* → *Haus*).
- Convert **conjugated verbs** to their **infinitive form** (e.g., *läuft* → *laufen*).

---

## **Word Breakdown Format**
Each extracted word should follow this exact structure:

```json
{
    "word": "Hochschule",
    "ipa": "ˈhoːxˌʃuːlə",
    "english": "university",
    "parts": [
        { "root": "hoch", "ipa": "hoːx", "english": "high" },
        { "root": "Schule", "ipa": "ʃuːlə", "english": "school" }
    ]
}