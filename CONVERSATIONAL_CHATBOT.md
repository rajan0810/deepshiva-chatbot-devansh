# Conversational & Document-Aware Chatbot

## Changes Implemented

### 1. **Conversation History Integration** ✅
- Chat now maintains context across messages
- Fetches last 5 messages from session history
- Passes conversation context to LLM for natural flow
- No more "one-shot" responses - context carries forward

**Example:**
```
User: "I have burns"
Bot: "I'm sorry to hear that. Can you tell me where the burn is located and how it happened?"

User: "On my hand from a hot pan"
Bot: "I understand. How severe is the burn? Is it just red, or are there blisters?"

User: "It's red with blisters"
Bot: [Provides specific treatment for second-degree burns]
```

### 2. **Conversational Symptom Checker** ✅
- New `ConversationalSymptomChecker` class
- Asks follow-up questions before making recommendations
- Gathers details: severity, duration, location, context
- Only proceeds to RAG retrieval when assessment is complete

**Flow:**
1. User mentions vague symptom
2. Bot asks clarifying questions (one at a time)
3. User provides details
4. Bot confirms understanding
5. Marks `ASSESSMENT_COMPLETE`
6. Then queries RAG for recommendations

### 3. **Document Q&A Intent** ✅
- New intent: `document_query` 
- Detects questions about uploaded medical documents
- Triggers `DocumentQAChain` instead of general agents
- Uses full document text (decrypted) for accurate answers

**Triggers:**
- "What was my hemoglobin?"
- "What did my X-ray show?"
- "What medications am I on?"
- "Explain my blood test results"

**Example:**
```
User uploads blood test showing Hemoglobin: 10.2 g/dL

User: "What was my hemoglobin level?"
Bot: "According to your blood test from [date], your hemoglobin was 10.2 g/dL. 
     This is below the normal range (12-16 g/dL for women, 13-17 g/dL for men), 
     which may explain fatigue. I recommend consulting your doctor about this."
```

### 4. **Enhanced Document Context** ✅
- Summaries for general context (medications, diagnoses)
- Full text decryption for detailed queries
- Limited to 2000 chars per document to avoid token overflow
- Automatically included when `document_query` intent detected

## Components Added

### `document_qa_chain.py`
**DocumentQAChain:**
- Analyzes user's medical documents
- Provides explanations in simple language
- Cites specific documents
- Never makes treatment recommendations (only explains)
- Asks for clarification if question is vague

**ConversationalSymptomChecker:**
- Multi-turn symptom assessment
- Asks focused follow-up questions
- Gathers severity, duration, location, context
- Marks completion when enough info collected

### Updated Files

**workflow.py:**
- Added `conversation_history` parameter to `run()`
- Integrated `DocumentQAChain` and `ConversationalSymptomChecker`
- Added `document_query` intent handler
- Modified symptom checker to be conversational

**api_mongodb.py:**
- Fetches conversation history (last 5 messages)
- Decrypts full document text for queries
- Passes `conversation_history` to workflow
- Stores both summaries and full text in user profile

**base_chains.py:**
- Added `document_query` to intent classification
- Updated semantic guidelines to detect document questions

## How It Works

### Conversation Flow
```
Message 1:
User: "I have a headache"
Bot: "I'm sorry to hear that. Can you tell me how long you've had this headache 
     and how severe it is on a scale of 1-10?"
[Stores in session history]

Message 2:
User: "For 2 days, around 7/10"
[System fetches Message 1 history]
Bot: "Thank you. Is the pain constant or does it come and go? 
     And have you noticed anything that makes it worse?"
[Stores in session history]

Message 3:
User: "Constant, worse with bright lights"
[System fetches Message 1 & 2 history]
Bot: "Based on what you've shared - a constant 7/10 headache for 2 days 
     that worsens with light - let me find recommendations..."
[Proceeds to RAG retrieval with full context]
```

### Document Query Flow
```
1. User uploads blood_test_2024.pdf
2. System extracts & encrypts full text
3. Stores summary: "Complete Blood Count | Hemoglobin: 10.2 g/dL (Low)"

Later:
User: "What was my hemoglobin?"
Intent: document_query detected
System: Decrypts full document text
DocumentQAChain: Analyzes text, finds "Hemoglobin: 10.2 g/dL"
Bot: "Your hemoglobin was 10.2 g/dL, which is below normal range..."
```

## Benefits

1. **Natural Conversations** - Context flows between messages
2. **Better Symptom Assessment** - Gathers complete picture before recommendations
3. **Accurate Document Answers** - Uses actual document content, not summaries
4. **No Unnecessary Agent Triggers** - Document questions don't trigger Ayush/Yoga unnecessarily
5. **User-Friendly** - Feels like talking to a real medical assistant

## Testing

**Test Conversational Symptoms:**
```
1. "I have burns"
   → Expect follow-up question about location/severity
2. Respond with details
   → Expect more specific question
3. Provide final detail
   → Expect recommendations
```

**Test Document Q&A:**
```
1. Upload a lab report PDF
2. Ask: "What was my blood sugar?"
   → Expect specific value from document
3. Ask: "Is that normal?"
   → Expect explanation based on document
```

**Test Conversation Context:**
```
1. "I have diabetes"
2. "What should I eat?"
   → Expect response referencing diabetes from message 1
```
