from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
import tempfile
import os
import shutil
import re
import fitz
import uuid

from .req_extractor import extract_requirements, extract_requirement_candidates, preprocess_requirements
from .chat_response import chat_response
from .func_parser import parse_directory_for_functions, preprocess_functions

class ChatBotView(APIView):
    def post(self, request):
        user_prompt = request.data.get('prompt', '')
        if not user_prompt:
            return Response({"error": "Prompt is required."}, status=status.HTTP_400_BAD_REQUEST)

        code_json = request.data.get('code_functions')
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
            return self.handle_requirement_upload(request)
        elif upload_type == "code":
            return self.handle_code_upload(request)
        else:
            return Response({"error": "Invalid upload type."}, status=status.HTTP_400_BAD_REQUEST)

    def handle_requirement_upload(self, request):
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

                #filtered_lines = extract_requirement_candidates(content, k=1, requirement_id_only=True)
                filtered_lines = preprocess_requirements(content)
                filtered_lines = "\n\n".join(filtered_lines)
                
                raw_requirements.append(filtered_lines)

        if not raw_requirements:
            return Response({"error": "No requirement files found. (Please make sure your filename contains 'requirement')"},
                            status=status.HTTP_400_BAD_REQUEST)

        joined_text = "\n\n".join(raw_requirements)
        extracted_requirements = extract_requirements(joined_text)

        return Response({"requirements": extracted_requirements}, status=status.HTTP_200_OK)

    def handle_code_upload(self, request):
        if 'files' not in request.FILES:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        temp_dir = tempfile.mkdtemp()

        try:
            for file in request.FILES.getlist('files'):
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            parsed_output = parse_directory_for_functions(temp_dir)
            print(parsed_output)
            return Response({"code_functions": parsed_output}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            shutil.rmtree(temp_dir)