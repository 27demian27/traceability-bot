from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
import re
import fitz
import uuid

from .req_extractor import extract_requirements, extract_requirement_candidates
from .chat_response import chat_response

class ChatBotView(APIView):
    def post(self, request):
        user_prompt = request.data.get('prompt', '')
        if not user_prompt:
            return Response({"error": "Prompt is required."}, status=status.HTTP_400_BAD_REQUEST)

        code_json = []
        requirements_json =  request.data.get('requirements')

        response = chat_response(user_prompt, requirements_json, code_json)

        return Response({"reply": response})



class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        print("TEST")
        print("Request data:", request.data)

        upload_type = request.data.get("type")

        if upload_type == "req":
            print("REQ")
        if upload_type == "code":
            print("CODE")

        if 'files' not in request.FILES:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        raw_requirements = []

        for f in request.FILES.getlist('files'):
            filename = f.name.lower()

            try:
                if filename.endswith('.pdf'):
                    pdf_doc = fitz.open(stream=f.read(), filetype="pdf")
                    content = ""
                    for page in pdf_doc:
                        content += page.get_text()
                else:
                    content = f.read().decode('utf-8')
            except Exception:
                return Response({"error": f"Failed to read file: {f.name}"}, status=status.HTTP_400_BAD_REQUEST)

            if 'requirement' in filename:
                with open("debug_pdf_output.txt", "w") as debug_file:
                        debug_file.write(content)
                # Filter out lines that are not requirements related
                filtered_lines = extract_requirement_candidates(content, k=0)
                filtered_lines = "\n\n".join(filtered_lines)
                raw_requirements.append(filtered_lines)

        if not raw_requirements:
            return Response({"error": "No requirement files found. (Please make sure your filename contains 'requirement')"}, status=status.HTTP_400_BAD_REQUEST)

        joined_text = "\n\n".join(raw_requirements)

        # Feed filtered requirements to language model
        extracted_requirements = extract_requirements(joined_text)

        return Response({"requirements": extracted_requirements}, status=status.HTTP_200_OK)
