# Medical Document Upload Feature

## Overview
Added complete document upload system for medical reports, prescriptions, and lab results with AI-powered extraction and chat integration.

## Components Added

### 1. Backend API (`api_mongodb.py`)
**Endpoints:**
- `POST /documents/upload` - Upload PDF documents
- `GET /documents` - List user's documents
- `DELETE /documents/{document_id}` - Delete a document

**Features:**
- PDF validation
- Automatic text extraction using PyPDFLoader
- LLM-based medical data extraction (test results, medications, diagnoses, vital signs)
- Encrypted storage in MongoDB
- Document context automatically included in chat queries

### 2. Frontend Component (`DocumentUploader.tsx`)
**Features:**
- Drag-and-drop file upload interface
- Real-time upload progress
- Document list with summaries
- Auto-loads documents on mount
- Delete functionality
- Error/success notifications

**UI Integration:**
- Added FileText button in chat input area
- Modal dialog for document management
- Matches app's stone/beige theme

### 3. Workflow Integration (`workflow.py`)
**Context Enhancement:**
- Fetches recent 5 documents automatically during chat
- Adds document summaries to user profile context
- Includes document context in:
  - Symptom checking
  - Health advisory
  - Ayurvedic recommendations
  - Yoga suggestions

**Example Context Format:**
```
Recent Medical Documents:
📄 blood_test_2024.pdf: Complete Blood Count report | Medications: Metformin, Aspirin | Diagnoses: Type 2 Diabetes
📄 chest_xray.pdf: X-ray shows clear lungs, no abnormalities detected
```

## How It Works

### Upload Flow
1. User clicks FileText button in chat
2. Modal opens with DocumentUploader
3. User selects PDF file
4. File sent to `/documents/upload`
5. Backend:
   - Saves to temp file
   - Extracts text with PyPDFLoader
   - Analyzes with LLM (structured extraction)
   - Stores in MongoDB (encrypted)
   - Returns analysis summary
6. Frontend displays document in list

### Chat Integration Flow
1. User sends chat message
2. Backend chat endpoint:
   - Fetches user's recent documents
   - Extracts summaries from document analysis
   - Adds to user_profile.document_context
3. Workflow receives enhanced context
4. LLM generates personalized response using document data

## Database Schema

### `user_documents` Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  file_name: String,
  file_size: Number,
  upload_date: DateTime,
  extraction: {
    num_pages: Number,
    extracted_at: String
  },
  analysis: {
    analyzed: Boolean,
    document_type: String,
    findings: [String],
    medications: [String],
    diagnoses: [String],
    recommendations: [String],
    key_values: Object,
    summary: String
  },
  full_text_encrypted: String,  // Encrypted with user salt
  status: String,  // "processed" | "failed"
  error: String
}
```

## Security Features
- Only PDF files accepted
- User authentication required
- Documents encrypted with user-specific salt
- Access control (users can only see their own documents)
- Full text encrypted in database
- Only metadata and analysis visible in API responses

## Benefits
1. **Personalized Advice**: LLM considers actual test results and diagnoses
2. **Drug Interactions**: Knows current medications from prescriptions
3. **Context Awareness**: References specific lab values in recommendations
4. **Medical History**: Long-term tracking of health records
5. **DISHA Compliant**: Encrypted storage of sensitive medical data

## Example Use Cases

### Lab Report Upload
User uploads blood test → System extracts:
- Hemoglobin: 10.2 g/dL (Low)
- Blood Sugar: 145 mg/dL (High)

Chat interaction:
```
User: "I'm feeling tired lately"
AI: "I see from your recent blood test that your hemoglobin is low (10.2 g/dL). 
     This can cause fatigue. Here are iron-rich foods to help..."
```

### Prescription Tracking
User uploads prescription → System extracts:
- Medications: Metformin 500mg BD, Aspirin 75mg OD

Chat interaction:
```
User: "Can I take turmeric supplements?"
AI: "⚠️ Important: You are currently taking Metformin and Aspirin. 
     Turmeric can interact with blood thinners like Aspirin. Please consult..."
```

## Testing
1. Start backend: `python api_mongodb.py`
2. Start frontend: `cd frontend && npm run dev`
3. Login to app
4. Click FileText button in chat
5. Upload a medical PDF
6. Ask related questions in chat
7. Verify LLM uses document context

## Future Enhancements
- Support for DOCX, images (OCR)
- Document search within files
- Timeline view of medical history
- Export reports as PDF
- Share documents with healthcare providers
- AI-powered trend analysis (e.g., blood sugar over time)
