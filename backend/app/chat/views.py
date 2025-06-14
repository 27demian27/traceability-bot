from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values 

import tempfile, os, shutil, re, fitz, uuid, requests, json

from .req_extractor import extract_requirements, extract_requirement_candidates, preprocess_requirements
from .chat_response import build_prompt
from .func_parser import parse_directory_for_functions, preprocess_functions
from . similarity_computer import return_similarity_matches

class ChatBotView(APIView):

    def post(self, request):

        user_prompt = request.data.get('prompt', '')
        if not user_prompt:
            return Response({"error": "Prompt is required."}, status=400)


        if not request.session.session_key:
            request.session.create()
            print("Session ID:", request.session.session_key)
        if "chat_history" not in request.session:
            print("No Session")
            request.session["chat_history"] = []

        chat_history = request.session.get("chat_history", [])
        chat_history.append({"role": "user", "content": user_prompt})
        request.session["chat_history"] = chat_history
        request.session.save()
        print(request.session["chat_history"])
        messages = chat_history

        code_json = request.data.get('code_functions')
        requirements_json = request.data.get('requirements')
        similarities = request.data.get('similarities')

        load_dotenv() 
        local_model = True
        mode = os.getenv("LLM_MODE")
        if mode == "API":
            local_model = False


        def messages_to_user_prompt(messages):
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"[system]: {msg['content']}\n"
                elif msg["role"] == "user":
                    prompt += f"[user]: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"[assistant]: {msg['content']}\n"
            prompt += "[assistant]: "
            return prompt


        def generate():
            if local_model:
                user_prompts = messages_to_user_prompt(messages)
                prompt = build_prompt(user_prompts, requirements_json, code_json, similarities)
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "deepseek-r1:latest",
                        "prompt": prompt,
                        "stream": True
                    },
                    stream=True
                )

                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("response", "")
                        yield f"data: {token}\n\n"
            else:
                prompt = build_prompt(user_prompt, requirements_json, code_json, similarities)

                client = OpenAI(
                    api_key=os.getenv("LLM_API_KEY")
                )

                stream = client.chat.completions.create(
                    model=os.getenv("LLM_API_MODEL"),
                    messages=messages,
                    stream=True,
                )

                for event in stream:
                    delta = event.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield f"data: {delta.content}\n\n"
                
        response =  StreamingHttpResponse(generate(), content_type='text/event-stream')
        return response



class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        request.session["touched"] = True

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
                with open("debug/debug_pdf_output.txt", "w") as debug_file:
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
                relative_path = file.name

                safe_path = os.path.normpath(relative_path)
                full_path = os.path.join(temp_dir, safe_path)


                if not full_path.startswith(temp_dir):
                    return Response({"error": "Invalid file path detected."}, status=status.HTTP_400_BAD_REQUEST)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            parsed_output = parse_directory_for_functions(temp_dir)

            return Response({"code_functions": parsed_output}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            shutil.rmtree(temp_dir)

class EmbeddingView(APIView):
    def post(self, request):
        request.session["touched"] = True
        mode = request.data.get("embedding_mode")
        if not mode:
            return Response({"error": "Embedding_mode is required."}, status=400)
        code_json = request.data.get('code_functions')
        requirements_json = request.data.get('requirements')
        similarity_matches = return_similarity_matches(requirements_json, code_json, 3, mode)
        # graph = build_similarity_graph(requirements_json, code_json, similarity_matches)
        # draw_graph(graph)
        try:
            return Response({"similarities": similarity_matches})     
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClearSessionView(APIView):
    def post(self, request):
        print("CLEARING SESSION")
        request.session.flush()
        return Response({'status': 'session cleared'})