import json
from time import time
from fastapi import FastAPI, Request
from app.services.open_ai_model import PromptSender
from supabase import create_client, Client
from app.services.vv import prompt

app = FastAPI()

# Supabase Connection
supabase: Client = None
def connect_supabase():
    global supabase
    if not supabase:
        url = "https://oatmdaldxsmmbgifacie.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9hdG1kYWxkeHNtbWJnaWZhY2llIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk0MTA2NDEsImV4cCI6MjA2NDk4NjY0MX0._jNuGdec6wJ96Jzs0dHxb6TLrYWiQx6DTieF9ktbAtU"
        supabase = create_client(url, key)
    return supabase

class VVSupabase:
    def __init__(self, user_id):
        self.user_id = user_id
        self.supabase_app = None
        self.supabase_chat_table = "vv_chats"
        self.supabase_chat_summary_table = "vv_chats_summary"
        self.supabase_chat_meta_data_table = "vv_chats_meta_data"

    def _connect_supabase(self):
        if not self.supabase_app:
            self.supabase_app = connect_supabase()
        return self.supabase_app

    def get_supabase_connection(self):
        return self._connect_supabase()

    def check_for_chat_in_supabase(self) -> list:
        supabase = self.get_supabase_connection()
        return (supabase.table(self.supabase_chat_table)
                .select("*")
                .eq("user_id", self.user_id)
                .execute()).data

    def check_for_chat_summary_in_supabase(self) -> list:
        supabase = self.get_supabase_connection()
        return (supabase.table(self.supabase_chat_summary_table)
                .select("*")
                .eq("user_id", self.user_id)
                .limit(1)
                .execute()).data

    def check_for_chat_meta_data_in_supabase(self, key) -> list:
        supabase = self.get_supabase_connection()
        return (supabase.table(self.supabase_chat_meta_data_table)
                .select("*")
                .eq("user_id", self.user_id)
                .eq("key", key)
                .limit(1)
                .execute()).data

class VIV:

    def __init__(self, user_id):
        self.user_id = user_id

    def _upload_message(self, message, timestamp=None, sender="bot"):
        if not timestamp:
            timestamp = str(int(time()))

        chat = {
            "timestamp": timestamp,
            "sender": sender,
            "message": message,
            "user_id": self.user_id
        }

        vv_supabase = VVSupabase(user_id=self.user_id)
        supabase_conn = vv_supabase.get_supabase_connection()
        response = supabase_conn.table(vv_supabase.supabase_chat_table).insert(chat).execute()
        print(response)

    def _upload_chat_summary(self, chat_summary, timestamp):
        if not timestamp:
            timestamp = str(int(time()))
        
        summary = {
            "timestamp": timestamp,
            "summary": chat_summary,
            "user_id": self.user_id
        }

        vv_supabase = VVSupabase(user_id=self.user_id)
        supabase_conn = vv_supabase.get_supabase_connection()
        response = supabase_conn.table(vv_supabase.supabase_chat_summary_table).insert(summary).execute()
        print(response)

    def initialise_new_chat(self):
        base_prompt = prompt.BASE_PROMPT
        greeting_prompt = prompt.GREETING_PROMPT.replace("<duration>", "New conversation")
        response_prompt = prompt.RESPONSE_FORMAT
        chat_context = prompt.CHAT_CONTEXT_PROMPT.replace("<chat_summary>", "This is a new conversation, no message till now").replace("<questions_left>", "All questions are unanswered").replace("<user_message>", "No message, user just opened the conversation")

        messages = [
            {"role": "system", "content": f"{base_prompt}\n{response_prompt}"},
            {"role": "assistant", "content": greeting_prompt},
            {"role": "user", "content": chat_context}
        ]

        gpt_response_object = PromptSender.send_prompt_by4_1_mini(messages, response_format='json_object')
        gpt_response = json.loads(gpt_response_object)

        timestamp = str(int(time()))
        self._upload_message(gpt_response.get("reply"), timestamp)

        summary_prompt = prompt.SUMMARY_PROMPT.replace("<chat_summary>", "This is a new conversation, no message till now").replace("<user_message>", "No message, user just opened the conversation").replace("<bot_reply>", gpt_response.get('reply'))

        messages = [{"role": "system", "content": f"{summary_prompt}"}]
        gpt_response_summary = str(PromptSender.send_prompt_by4_1_nano(messages))

        self._upload_chat_summary(gpt_response_summary, timestamp)

        self._create_new_intake_question_object()

        return {'gpt_response': gpt_response, 'gpt_response_summary': gpt_response_summary}

    def _create_new_intake_question_object(self):
        intake_profile_questions_answer = {
            "user_id": self.user_id,
            "key": "intake_profile_questions_answer",
            "value": { 
                "demographics": {
                  "age": {"status": False, "answer":""},
                  "sex_biological": {"status": False, "answer":""},
                  "ethnicity": {"status": False, "answer":""},
                  "height": {"status": False, "answer":""},
                  "weight": {"status": False, "answer":""},
                  "pregnancy_or_lactation_status": {"status": False, "answer":""}
                },
                "medical_health_history": {
                  "known_medical_conditions": {"status": False, "answer":""},
                  "recent_illnesses_or_hospitalisations": {"status": False, "answer":""},
                  "current_medications": {"status": False, "answer":""},
                  "ongoing_treatments": {"status": False, "answer":""},
                  "family_history_of_chronic_conditions": {"status": False, "answer":""},
                  "previous_abnormal_lab_results": {"status": False, "answer":""}
                },
                "lifestyle_habits": {
                  "sleep_duration_and_quality": {"status": False, "answer":""},
                  "stress_levels": {"status": False, "answer":""},
                  "smoking_status": {"status": False, "answer":""},
                  "alcohol_consumption": {"status": False, "answer":""},
                  "physical_activity_level": {"status": False, "answer":""},
                  "dietary_pattern_or_restrictions": {"status": False, "answer":""},
                  "hydration_habits": {"status": False, "answer":""}
                },
                "symptoms_current_concerns": {
                  "fatigue_or_low_energy": {"status": False, "answer":""},
                  "weight_gain_loss": {"status": False, "answer":""},
                  "digestive_issues": {"status": False, "answer":""},
                  "cognitive_issues": {"status": False, "answer":""},
                  "mood_issues": {"status": False, "answer":""},
                  "skin_hair_changes": {"status": False, "answer":""},
                  "hormonal_symptoms": {"status": False, "answer":""}
                },
                "health_goal": {
                  "specific_health_concerns_or_focus_areas": {"status": False, "answer":""}
                },
                "supplements_medications": {
                  "list_of_supplements": {"status": False, "answer":""},
                  "dosage_and_frequency": {"status": False, "answer":""},
                  "hormonal_or_steroid_medications": {"status": False, "answer":""},
                  "any_recent_medication_changes": {"status": False, "answer":""}
                },
                "reproductive_health": {
                  "menstrual_regularity": {"status": False, "answer":""},
                  "use_of_hormonal_contraceptives": {"status": False, "answer":""},
                  "trying_to_conceive": {"status": False, "answer":""},
                  "menopause_status": {"status": False, "answer":""}
                }
            }
        }
        vv_supabase = VVSupabase(user_id=self.user_id)
        supabase_conn = vv_supabase.get_supabase_connection()
        response = supabase_conn.table(vv_supabase.supabase_chat_meta_data_table).insert(intake_profile_questions_answer).execute()
        print(response)

    def _upload_intake_ques_ans(self, original_qa, qa_obj):
        for category, obj in qa_obj.items():
            for ques, ans in obj.items():
                ans_obj = {
                    "status": True,
                    "answer": ans
                }
                original_qa[category][ques] = ans_obj

        vv_supabase = VVSupabase(user_id=self.user_id)
        supabase_conn = vv_supabase.get_supabase_connection()
        response = (supabase_conn.table(vv_supabase.supabase_chat_meta_data_table)
                    .update({"value": original_qa})
                    .eq("user_id", self.user_id)
                    .eq("key", "intake_profile_questions_answer")
                    .execute())
        print(response)

    def get_qa(self, chat_meta_data):
        if not chat_meta_data:
            return "All questions are unanswered", "All questions are unanswered"
        
        ans_qa = ""
        left_qa = ""

        for category, obj in chat_meta_data.items():
            ans_local_str = ""
            left_local_str = ""
            for ques, ans in obj.items():
                if ans['status']:
                    ans_local_str += f"QUES - {ques}, ANSWER - {ans['answer']}\n"
                else:
                    left_local_str += f"{ques}\n"
            if ans_local_str:
                ans_qa += f"\nCategory - {category} \n{ans_local_str}"
            if left_local_str:
                left_qa += f"\nCategory - {category} \n{left_local_str}"

        if not ans_qa:
            ans_qa = "All questions are unanswered"
        if not left_qa:
            left_qa = "All questions are answered"
        return ans_qa, left_qa

    def bot_reply(self, user_message="No new message, User just opened the conversation again.", greet_user=False):
        vv_supabase = VVSupabase(user_id=self.user_id)
        chat_summary_data = vv_supabase.check_for_chat_summary_in_supabase()
        chat_meta_data = vv_supabase.check_for_chat_meta_data_in_supabase(key="intake_profile_questions_answer")

        if not chat_summary_data or not chat_meta_data:
            return {"error": "No chat summary or meta data found."}

        chat_meta_data_qa = chat_meta_data[0]["value"]
        chat_summary = chat_summary_data[0]
        answered_intake_questions, left_intake_questions = self.get_qa(chat_meta_data_qa)

        base_prompt = prompt.BASE_PROMPT
        response_prompt = prompt.RESPONSE_FORMAT
        chat_context = prompt.CHAT_CONTEXT_PROMPT \
            .replace("<user_message>", str(user_message or "")) \
            .replace("<chat_summary>", str(chat_summary.get('summary') or "")) \
            .replace("<questions_left>", str(left_intake_questions or "")) \
            .replace("<questions_answered>", str(answered_intake_questions or ""))

        print(chat_context)
        messages = [
            {"role": "system", "content": f"{base_prompt}\n{response_prompt}"},
            {"role": "user", "content": chat_context}
        ]

        if greet_user:
            greeting_prompt = prompt.GREETING_PROMPT.replace(
                "<duration>",
                f"Duration after which user appeared - {str(int(time()) - int(chat_summary['timestamp']))} seconds"
            )
            messages.append({"role": "assistant", "content": greeting_prompt})
        else:
            other_ques_prompt = prompt.OTHER_QUESTION_PROMPT
            messages.append({"role": "assistant", "content": other_ques_prompt})

        messages.append({"role": "assistant", "content": prompt.CHAT_GAURDRAILS})

        if left_intake_questions == "All questions are answered":
            messages.append({"role": "assistant", "content": prompt.FUNCTIONAL_ANALYSIS_PROMPT})

        gpt_response_object = PromptSender.send_prompt_by4_1(messages, response_format='json_object')
        gpt_response = json.loads(gpt_response_object)

        timestamp = str(int(time()))
        self._upload_message(gpt_response.get("reply"), timestamp)

        if gpt_response.get("intake_profile_questions"):
            self._upload_intake_ques_ans(chat_meta_data_qa, gpt_response.get("intake_profile_questions_answer"))

        summary_prompt = prompt.SUMMARY_PROMPT.replace(
            "<chat_summary>", chat_summary['summary']
        ).replace(
            "<user_message>", user_message
        ).replace(
            "<bot_reply>", gpt_response.get('reply')
        )
        messages = [{"role": "system", "content": f"{summary_prompt}"}]
        gpt_response_summary = str(PromptSender.send_prompt_by4_1_nano(messages))

        self._upload_chat_summary(gpt_response_summary, timestamp)

        return {'gpt_response': gpt_response, 'gpt_response_summary': gpt_response_summary}