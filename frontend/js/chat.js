import { marked } from "https://esm.sh/marked";
import { setupDropZone } from './directoryDropHelper.js';

let droppedCodeFiles = [];

setupDropZone("codeDropZone", (files) => {
  droppedCodeFiles = files;
  document.getElementById("codeUploadErrors").textContent =
    `Ready to upload ${files.length} file(s) from ${new Set(
      files.map(f => f.fullPath?.split("/")[0])
    ).size} folder(s). Click “Upload Files”.`;
});


const state = {
    requirements: [],
    code_functions: [],
    similarities: [],
    embedding_mode: "default",
    embedding_mode_changed: false,
};

async function sendPrompt() {
    const input = document.getElementById('promptInput');
    const message = input.value.trim();
    if (message === "") return;

    if (state.similarities.length == 0 || state.embedding_mode_changed) {
        await getSimilarities();
    }

    console.log("Similarities: "+state.similarities);

    const messages = document.getElementById('messages');
    messages.innerHTML += `
    <div style="display: flex; justify-content: flex-end;">
        <div class="message user">${message}</div>
    </div>`;

    const botMessageContainer = document.createElement('div');
    botMessageContainer.style.display = 'flex';
    botMessageContainer.style.justifyContent = 'flex-start';

    const botMessageDiv = document.createElement('div');
    botMessageDiv.className = 'message bot normal';
    botMessageDiv.textContent = '';

    botMessageContainer.appendChild(botMessageDiv);
    messages.appendChild(botMessageContainer);

    try {
        const response = await fetch('http://localhost:8000/chat/ask/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'
                     },
            credentials: "include",
            body: JSON.stringify({
                prompt: message,
                requirements: state.requirements,
                code_functions: state.code_functions,
                similarities: state.similarities
            })
        });

        if (!response.ok || !response.body) {
            throw new Error("Stream connection failed");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let raw_read = "";
        let test_string = "";

        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            raw_read += decoder.decode(value, { stream: true });
            const parts = buffer.split("\n\n");

            for (let i = 0; i < parts.length - 1; i++) {
                const part = parts[i];
                //console.log("part: "+ part);
                if (part.includes("data:")) {
                    const chunk = part.slice(6);
                    test_string += chunk;
                    botMessageDiv.innerHTML += chunk;
                    if(chunk.includes("<think>")) {
                        botMessageDiv.className = 'message bot thinking';
                    }
                    if(chunk.includes("</think>")) {
                        botMessageDiv.className = 'message bot normal';
                        botMessageDiv.innerHTML = ''
                    }
                } else {
                    test_string += '\n';
                    botMessageDiv.innerHTML += '\n';
                }
                messages.scrollTop = messages.scrollHeight;
            }
            buffer = parts[parts.length - 1];
        }
        botMessageDiv.innerHTML = marked.parse(botMessageDiv.innerHTML);
        console.log(botMessageDiv.innerHTML);
    } catch (error) {
        messages.innerHTML += `<strong>Error:</strong> <i>Could not reach server.</i>`;
        console.error(error);
    } finally {
        input.value = '';
    }
}

async function getSimilarities() {
    try {
        const response = await fetch('http://localhost:8000/chat/embedding/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                requirements: state.requirements,
                code_functions: state.code_functions,
                embedding_mode: state.embedding_mode,
            })
        });
        const data = await response.json();
        console.log(data);
        state.similarities = data.similarities;
    } catch(error) {
        messages.innerHTML =
            "<strong>Error:</strong> <i>Error getting similarities.</i>";
        console.error(error);
    } finally {
        state.embedding_mode_changed = false;
    }
}

async function uploadFilesReq() {
    console.log(document.getElementById('uploadInputReq'));
    console.log("uploadFilesReq")
    const input = document.getElementById('uploadInputReq');
    const files = input.files;
    if (files.length === 0) return;

    const formData = new FormData();
    formData.append('type', 'req');
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    const errorMessages = document.getElementById('reqUploadErrors');
    errorMessages.innerHTML = ""
    errorMessages.innerHTML += `<div>Uploaded ${files.length} file(s)</div>`;

    loadingIndicator.style.display = 'flex';
    const messages = document.getElementById('messages');
    try {
        const response = await fetch('http://localhost:8000/chat/upload/', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        const data = await response.json();

        messages.innerHTML += `
        <div style="display: flex; justify-content: flex-start;">
            <div class="message bot">Thanks for providing your requirements documents.</div>
        </div>`;  
        console.log(data);
        state.requirements = data.requirements;
    } catch (error) {
        errorMessagesessages.innerHTML += `<div><strong>Error:</strong> <i>Document upload failed.</i></div>`;
        console.error(error);
    } finally {
        loadingIndicator.style.display = 'none';
    }

    input.value = '';
}

async function uploadFilesCode() {
    const input = document.getElementById('uploadInputCode');
    const pickerFiles = Array.from(input.files || []);
    const files = [...pickerFiles, ...droppedCodeFiles];
    droppedCodeFiles = [];

    if (files.length === 0) return;

    const formData = new FormData();
    formData.append('type', 'code');

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const relPath = file.fullPath || file.webkitRelativePath || file.name;
        formData.append('files', file, relPath);
    }

    const errorMessages = document.getElementById('codeUploadErrors');
    errorMessages.textContent = `Uploading ${files.length} code file(s)…`;

    try {
        const response = await fetch("http://localhost:8000/chat/upload/", {
            method: "POST",
            credentials: 'include',
            body: formData
        });

        const data = await response.json();

        document.getElementById("messages").innerHTML += `
            <div style="display:flex;justify-content:flex-start">
                <div class="message bot">Code files received and analyzed.</div>
            </div>`;
        console.log(data);
        state.code_functions = data.code_functions;

    } catch (error) {
        errorMessages.innerHTML =
            "<strong>Error:</strong> <i>Code upload failed.</i>";
        console.error(error);
    } finally {
        errorMessages.textContent = `Succesfully uploaded ${files.length} code file(s).`;
        input.value = '';
    }
}

async function clearSession() {
    try {
        await fetch("http://localhost:8000/chat/clear_session/", {
            method: "POST",
            credentials: "include"
        });
    } catch(error) {
        console.error(error);
    }
}

window.addEventListener("unload", clearSession);

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("sendPromptButton").addEventListener("click", sendPrompt);
    document.getElementById("uploadDocumentsButton").addEventListener("click", uploadFilesReq);
    document.getElementById("uploadCodeButton").addEventListener("click", uploadFilesCode);
    document.getElementById("embedding_mode").addEventListener("change", () => {state.embedding_mode = document.getElementById("embedding_mode").value; state.embedding_mode_changed = true});
});

