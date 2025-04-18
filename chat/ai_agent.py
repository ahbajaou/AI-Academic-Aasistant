import re  # Fixed missing import
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from .models import ChatMessage

# Initialize Gemini AI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key='AIzaSyD9-e_nHzUSgbUW41rPLB9KTyoomRuK2HA' # Uses GOOGLE_API_KEY from environment
    # google_api_key=None  # Uses GOOGLE_API_KEY from environment
)

# Institution data
INSTITUTION_DATA = {
    "EMINE": {
        "admission": [
            "Complete high school with strong grades in math, physics, and chemistry.",
            "Prepare for entrance exams (e.g., JEE or specific engineering tests).",
            "Submit application with transcripts and recommendation letters.",
            "Attend an interview or assessment if required."
        ],
        "scholarship": [
            "Check university-specific scholarships (e.g., merit-based or need-based).",
            "Apply for external funding (e.g., Erasmus+ for European schools).",
            "Submit financial documents and a scholarship essay.",
            "Meet deadlines (typically early 2025 for Fall 2025 intake)."
        ]
    },
    "1337": {
        "admission": [
            "Be aged 18-30 with basic coding interest (no degree required).",
            "Pass the online logic and memory tests on 1337.ma.",
            "Complete the Piscine (28-day coding bootcamp) in Morocco.",
            "No tuition fees, but prepare for living expenses."
        ],
        "scholarship": [
            "No formal scholarships (free education model).",
            "Seek external funding (e.g., Moroccan government grants).",
            "Prove financial need for accommodation support.",
            "Contact 1337 administration for partner programs."
        ]
    }
}

# Prompt templates
institution_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a student-oriented assistant named Uorianted, created by Chebchoub. Provide clear, concise answers about EMINE or 1337 admission and scholarships based on the provided data."),
    ("human", "User asked: {input}\n\nInstitution data:\n{inst_data}")
])

fallback_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a student-oriented assistant named Uorianted, created by Chebchoub. Politely redirect users to ask about EMINE or 1337 admission or scholarships."),
    ("human", "User asked: {input}")
])

# Chains
institution_chain = institution_prompt | llm
fallback_chain = fallback_prompt | llm

def get_response(user_input):
    """
    Process student queries about EMINE or 1337 admission/scholarships.
    Redirects non-relevant queries politely.
    """
    # Check for institution queries
    institution_keywords = [
        r"emine",
        r"1337",
        r"admission",
        r"scholarship",
        r"apply to",
        r"get into",
        r"funding",
        r"enroll",
        r"join",
        r"financial aid"
    ]
    is_institution_query = any(re.search(keyword, user_input.lower()) for keyword in institution_keywords)
    
    if is_institution_query:
        # Handle institution query
        inst_data = ""
        user_input_lower = user_input.lower()
        
        if "emine" in user_input_lower:
            inst = "EMINE"
            if any(k in user_input_lower for k in ["admission", "apply", "get into", "enroll", "join"]):
                inst_data = "\n".join(f"- {item}" for item in INSTITUTION_DATA["EMINE"]["admission"])
            elif any(k in user_input_lower for k in ["scholarship", "funding", "financial aid"]):
                inst_data = "\n".join(f"- {item}" for item in INSTITUTION_DATA["EMINE"]["scholarship"])
            else:
                inst_data = (
                    "Admission:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["EMINE"]["admission"]) +
                    "\n\nScholarships:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["EMINE"]["scholarship"])
                )
        elif "1337" in user_input_lower:
            inst = "1337"
            if any(k in user_input_lower for k in ["admission", "apply", "get into", "enroll", "join"]):
                inst_data = "\n".join(f"- {item}" for item in INSTITUTION_DATA["1337"]["admission"])
            elif any(k in user_input_lower for k in ["scholarship", "funding", "financial aid"]):
                inst_data = "\n".join(f"- {item}" for item in INSTITUTION_DATA["1337"]["scholarship"])
            else:
                inst_data = (
                    "Admission:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["1337"]["admission"]) +
                    "\n\nScholarships:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["1337"]["scholarship"])
                )
        else:
            # General query about institutions
            inst_data = "Available institutions: EMINE, 1337\n"
            if any(k in user_input_lower for k in ["admission", "apply", "get into", "enroll", "join"]):
                inst_data += (
                    "EMINE Admission:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["EMINE"]["admission"]) +
                    "\n\n1337 Admission:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["1337"]["admission"])
                )
            elif any(k in user_input_lower for k in ["scholarship", "funding", "financial aid"]):
                inst_data += (
                    "EMINE Scholarships:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["EMINE"]["scholarship"]) +
                    "\n\n1337 Scholarships:\n" + "\n".join(f"- {item}" for item in INSTITUTION_DATA["1337"]["scholarship"])
                )
        
        if not inst_data:
            inst_data = "Please specify EMINE or 1337 for admission or scholarship details."
        
        response = institution_chain.invoke({"input": user_input, "inst_data": inst_data})
    else:
        # Redirect non-relevant queries
        response = fallback_chain.invoke({"input": user_input})
    
    # Save to database (optional, confirm if you want to keep)
    ChatMessage.objects.create(
        user_input=user_input,
        ai_response=response.content
    )
    
    return response.content