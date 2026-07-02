# Pre-Computing Likely-Needed Results

**Example (from Zeeguu):** 

When a learner reads a text and asks for a translation, the most important thing is to return a good-enough translation **fast**. 

However, the words in the vocabulary exercises are drawn from the learner's past translations, so the system needs to verify that word/translation pairs obtained from Google Translate or Azure Translate APIs are correct before including them in exercises. 

The system can afford to insert an imprecise translation while the reader is quickly trying to make sense of a text, but it cannot afford to have users repeatedly practice imprecise translations! A regular cron job identifies words users should study next and pre-computes LLM-based verification of the quality of their translations. 

**Forces:** LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real-time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

**Solution:** Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs.
