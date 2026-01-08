
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import google.generativeai as genai


app = FastAPI()

client = genai.Client()

class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str

system_prompt = """
You are provided with notes written by a doctor from a patient's visit.
Your job is to summarize the visit for the doctor and provide an email.
Reply with exactly three sections with the headings:
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
"""

def user_prompt_for(visit: Visit) -> str:
    return f"""Create the summary, next steps and draft email for:
Patient Name: {visit.patient_name}
Date of Visit: {visit.date_of_visit}
Notes: {visit.notes}"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_prompt
)

@app.post("/api")
async def consultation_summary(visit: Visit):
    user_prompt = user_prompt_for(visit)

    # Gemini's streaming method
    response = await model.generate_content_async(user_prompt, stream=True)

    async def event_stream():
        async for chunk in response:
            if chunk.text:
                # Format to match your specific SSE requirements
                lines = chunk.text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
        
       
    #open ai styling
    #prompt = [{"role": "user", "content": "Come up with a new business idea for AI Agents"}]
    #response = client.chat.completions.create(model="gpt-5-nano", messages=prompt)
    #return response.choices[0].message.content