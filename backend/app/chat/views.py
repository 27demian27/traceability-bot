from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values 

import tempfile, os, shutil, re, fitz, uuid, requests, json

from .models import UploadedDocument
from .req_extractor import extract_requirements, extract_requirement_candidates, preprocess_requirements
from .prompt_builder import build_prompt
from .func_parser import parse_directory_for_functions, preprocess_functions
from .similarity_computer import return_similarity_matches
from .graph_builder import build_similarity_graph, draw_graph

K=5

class ChatBotView(APIView):

    def post(self, request):
        if (os.path.exists("debug/debug_response.txt")):
            os.remove("debug/debug_response.txt") 

        user_prompt = request.data.get('prompt', '')
        if not user_prompt:
            return Response({"error": "Prompt is required."}, status=400)


        if not request.session.session_key:
            request.session.create()
            print("Session ID:", request.session.session_key)
        if "chat_history" not in request.session:
            request.session["chat_history"] = []
        if "code" not in request.session:
            request.session["code"] = []
        if "requirements" not in request.session:
            request.session["requirements"] = []
        if "testing_docs" not in request.session:
            request.session["testing_docs"] = []
        if "similarities" not in request.session:
            request.session["similarities"] = []
            

        chat_history = request.session.get("chat_history", [])
        print(chat_history)
        chat_history.append({"role": "user", "content": user_prompt})
        request.session["chat_history"] = chat_history
        request.session.save()
        messages = chat_history

        code_json = request.session["code"]
        requirements_json = request.session["requirements"]
        similarities = request.session["similarities"]
        testing_docs = request.session["testing_docs"]

        load_dotenv() 
        local_model = True
        mode = os.getenv("LLM_MODE_CHAT")
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
            reply = ""

            if local_model:
                user_prompts = messages_to_user_prompt(messages)
                prompt = build_prompt(user_prompts, requirements_json, code_json, testing_docs, similarities)
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": os.getenv("LLM_API_MODEL"),
                        "prompt": prompt,
                        "stream": True
                    },
                    stream=True
                )

                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("response", "")
                        reply += token
                        yield f"data: {token}\n\n"
            else:
                prompt = build_prompt(user_prompt, requirements_json, code_json, testing_docs, similarities)
                
                api_messages = messages + [{"role": "user", "content": prompt}]
                client = OpenAI(
                    api_key=os.getenv("LLM_API_KEY")
                )

                stream = client.chat.completions.create(
                    model=os.getenv("LLM_API_MODEL"),
                    messages=api_messages,
                    stream=True,
                )

                with open("debug/debug_response.txt", "a") as debug_file:
                    for event in stream:
                        delta = event.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            reply += delta.content
                            debug_file.write(delta.content)
                            yield f"data: {delta.content}\n\n"

        
            request.session["chat_history"].append({"role": "assistant", "content": reply})
            request.session.save()

        response = StreamingHttpResponse(generate(), content_type='text/event-stream')
        return response



class DocumentUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        if not request.FILES:
            return Response({"error": "No files provided.", "files_uploaded": []}, status=status.HTTP_400_BAD_REQUEST)

        if not request.session.session_key:
            request.session.create()
            print("Session ID:", request.session.session_key)
        if "requirements" not in request.session:
            request.session["requirements"] = []
        if "testing_docs" not in request.session:
            request.session["testing_docs"] = []
        request.session["touched"] = True

        files_uploaded = []
        i = 0
        for key in request.FILES:
            if key.startswith('files[') and key.endswith(']'):
                upload_type = request.POST[f'types[{i}]']
                file = request.data[f'files[{i}]']
                if(upload_type == "unknown"):
                    continue
                try:
                    filename = file.name
                    if UploadedDocument.objects.filter(filename=filename).exists():
                        print(f"Skipping duplicate file: {filename}")
                        continue

                    if upload_type == "req":
                        reqs = self.handle_requirement_upload(file)
                        request.session["requirements"].append(reqs)
                    elif upload_type == "test":
                        testdoc = self.handle_testing_doc_upload(file)
                        request.session["testing_docs"].append(testdoc)
                    else:
                        return Response({"error": "Invalid upload type."}, status=status.HTTP_400_BAD_REQUEST)

                    UploadedDocument.objects.create(filename=filename)
                    files_uploaded.append(filename)
                except Exception as e:
                    print(f"Exception occurred: {e}")
                    return Response({"error": f"Failed to read file: {file.name}", "details": str(e)}, status=400)
                i += 1

        request.session.save()
        return Response({"status": "success", "files_uploaded": files_uploaded}, status=status.HTTP_200_OK)

    def handle_requirement_upload(self, file):
        print("REQ UPLOAD")
        raw_requirements = []
        filename = file.name.lower()

        if filename.endswith('.pdf'):
            pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
            content = ""
            for page in pdf_doc:
                content += page.get_text()
        else:
            content = file.read().decode('utf-8')

        with open("debug/debug_req_pdf_output.txt", "w") as debug_file:
            debug_file.write(content)

        filtered_lines = preprocess_requirements(content)
        filtered_lines = "\n\n".join(filtered_lines)

        raw_requirements.append(filtered_lines)

        joined_text = "\n\n".join(raw_requirements)
        extracted_requirements = extract_requirements(joined_text)

        return extracted_requirements



    def handle_testing_doc_upload(self, file):
        filename = file.name.lower()
        content = ""
        if filename.endswith('.pdf'):
            pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
            for page in pdf_doc:
                content += page.get_text()
        else:
            content = file.read().decode('utf-8')

        with open("debug/debug_testing_pdf_output.txt", "w") as debug_file:
            debug_file.write(content)

        return content


class CodeUploadView(APIView):

    def post(self, request):
        if 'files' not in request.FILES:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.session.session_key:
            request.session.create()
            print("Session ID:", request.session.session_key)
        if "code" not in request.session:
                request.session["code"] = []
        request.session["touched"] = True

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
            
            seen = set()
            for item in parsed_output:
                key = (item['file'], item['name'])
                if key not in seen:
                    seen.add(key)
                    request.session["code"].append(item)

            request.session.save()
            return Response({"status": "success", "code" : parsed_output}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            shutil.rmtree(temp_dir)

class EmbeddingView(APIView):
    def convert_similarity_matches(self, matches):
        return [
            (req_id, [(test, float(score)) for test, score in test_scores])
            for req_id, test_scores in matches
        ]

    def post(self, request):
        if "similarities" not in request.session:
            request.session["similarities"] = []
        if "code" not in request.session:
            request.session["code"] = []
        if "requirements" not in request.session:
            request.session["requirements"] = []
        request.session["touched"] = True
        
        mode = request.data.get("embedding_mode")
        if not mode:
            return Response({"error": "Embedding_mode is required."}, status=400)

        code_json = request.session["code"]
        
        requirements_list = request.session["requirements"]
        requirements_json = [item for sublist in requirements_list for item in sublist]
        
        similarity_matches = return_similarity_matches(requirements_json, code_json, top_n=K, mode=mode)
        graph = build_similarity_graph(requirements_json, code_json, similarity_matches)
        
        print("DRAWING NEW SIMILARITY GRAPH")
        draw_graph(graph, "debug/similarity_graph.png")
        request.session["similarities"] = self.convert_similarity_matches(similarity_matches)
        request.session.save()
        try:
            return Response({"status": "success", "similarities": similarity_matches})     
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClearSessionView(APIView):
    def post(self, request):
        if request.data.get("clear_chat_only"):
            print("CLEARING CHAT")
            request.session["chat_history"] = []
            request.session.save()
            return Response({'status': 'chat cleared'})
        else:
            print("CLEARING ENTIRE SESSION")
            request.session.flush()
            UploadedDocument.objects.all().delete()
            return Response({'status': 'session cleared'})