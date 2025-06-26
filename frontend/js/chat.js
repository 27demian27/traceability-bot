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
    embedding_mode: "default",
    embedding_mode_changed: false,
};

async function sendPrompt() {
    const input = document.getElementById('promptInput');
    const message = input.value.trim();
    if (message === "") return;

    if (state.embedding_mode_changed) {
        await getSimilarities();
    }


    const messages = document.getElementById('messages');
    messages.innerHTML += `
    <div style="display: flex; justify-content: flex-end;">
        <div class="message user">${message}</div>
    </div>`;

    const botMessageContainer = document.createElement('div');
    botMessageContainer.style.display = 'flex';
    botMessageContainer.style.justifyContent = 'flex-start';

    const botMessageDiv = document.createElement('div');
    botMessageDiv.className = 'message bot normal markdown-body';
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
            })
        });

        if (!response.ok || !response.body) {
            throw new Error("Stream connection failed");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let raw_read = "";
        let markdownBuffer = "";
        
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
                    const markdownChunk = part.slice(6);
                    markdownBuffer += markdownChunk;

                    botMessageDiv.textContent = markdownBuffer;

                    if(markdownChunk.includes("<think>")) {
                        botMessageDiv.className = 'message bot thinking';
                    }
                    if(markdownChunk.includes("</think>")) {
                        botMessageDiv.className = 'message bot normal';
                        markdownBuffer = '';
                    }
                } else {
                    markdownBuffer += "\n";
                }
                messages.scrollTop = messages.scrollHeight;
            }
            buffer = parts[parts.length - 1];
        }
        botMessageDiv.innerHTML = marked.parse(markdownBuffer);
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
                embedding_mode: state.embedding_mode
            })
        });
        const data = await response.json();
        console.log(data);
    } catch(error) {
        messages.innerHTML =
            "<strong>Error:</strong> <i>Error getting similarities.</i>";
        console.error(error);
    } finally {
        state.embedding_mode_changed = false;
    }
}

async function uploadDocuments() {
    console.log(document.getElementById('uploadInputDocuments'));
    console.log("uploadDocuments")
    const input = document.getElementById('uploadInputDocuments');
    const files = input.files;
    console.log(input.files);
    if (files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (file.type == "") { continue }

        let type = 'unknown';
        if (file.name.toLowerCase().includes('testing')) {
            type = 'test';
        } else if (file.name.toLowerCase().includes('requirement')) {
            type = 'req';
        }
        formData.append(`files[${i}]`, file);
        formData.append(`types[${i}]`, type);
    }

    const errorMessages = document.getElementById('docUploadErrors');
    errorMessages.innerHTML = ""
    errorMessages.innerHTML += `<div>Uploading ${files.length} file(s)...</div>`;

    loadingIndicator.style.display = 'flex';
    const messages = document.getElementById('messages');
    try {
        for (let pair of formData.entries()) {
            console.log(pair[0], pair[1]);
        }
        const response = await fetch('http://localhost:8000/chat/upload/docs/', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        const data = await response.json();
        console.log(data.files_uploaded.length);
        if (data.files_uploaded.length > 0) {
            messages.innerHTML += `
            <div style="display: flex; justify-content: flex-start;">
                <div class="message bot">Thanks for providing your requirements documents.</div>
            </div>`;  
            errorMessages.innerHTML += `<div>Successfully uploaded ${files.length} file(s).</div>`;
        } else {
            messages.innerHTML += `
            <div style="display: flex; justify-content: flex-start;">
                <div class="message bot">Please make sure you are uploading PDF documents.</div>
            </div>`;
            errorMessages.innerHTML = ""
        }  
        console.log(data);
    } catch (error) {
        errorMessages.innerHTML = ""
        errorMessages.innerHTML += `<div><strong>Error:</strong> <i>Document upload failed.</i></div>`;
        console.error(error);
    } finally {
        loadingIndicator.style.display = 'none';
    }

    input.value = '';
}

async function uploadCode() {
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
        const response = await fetch("http://localhost:8000/chat/upload/code/", {
            method: "POST",
            credentials: 'include',
            body: formData
        });

        const data = await response.json();
        console.log(data);
        if (data.status == "success") {
            document.getElementById("messages").innerHTML += `
                <div style="display:flex;justify-content:flex-start">
                    <div class="message bot">Code files received and analyzed.</div>
                </div>`;
        } else {
            errorMessages.innerHTML =
            "<strong>Error:</strong> <i>Code upload failed.</i>";
        }
        
    } catch (error) {
        errorMessages.innerHTML =
            "<strong>Error:</strong> <i>Code upload failed.</i>";
        console.error(error);
    } finally {
        errorMessages.textContent = `Succesfully uploaded ${files.length} code file(s).`;
        input.value = '';
    }
}

async function drawGraph() {
    const url = `http://localhost:8000/chat/graph/?mode=${state.embedding_mode}`;
    try {
        await fetch(url, {
            method: "GET",
            credentials: "include",
        });
    } catch(error) {
        console.error(error);
    }
}

async function clearSession() {
    state.embedding_mode_changed = true;
    try {
        await fetch("http://localhost:8000/chat/clear_session/", {
            method: "POST",
            headers: {
            'Content-Type': 'application/json',
            },
            credentials: "include",
            body: JSON.stringify({
                clear_chat_only: false
            })
        });
    } catch(error) {
        console.error(error);
    }
}

async function clearChatSession() {
    const messages = document.getElementById('messages');
    console.log("clearChatSession")
    try {
        await fetch("http://localhost:8000/chat/clear_session/", {
            method: "POST",
            headers: {
            'Content-Type': 'application/json',
            },
            credentials: "include",
            body: JSON.stringify({
                clear_chat_only: true
            })
        });
        messages.innerHTML = "";
    } catch(error) {
        console.error(error);
    }
}

window.addEventListener("unload", clearSession);

document.addEventListener("DOMContentLoaded", () => {
    state.embedding_mode_changed = true;
    document.getElementById("sendPromptButton").addEventListener("click", sendPrompt);
    document.getElementById("chatbox").addEventListener("click", (e) => {
        if (e.target.closest("#refreshChatButton")) {
            clearChatSession();
        }
    });    
    document.getElementById("promptInput").addEventListener("keydown", async function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        await sendPrompt();
    }
    });
    document.getElementById("drawGraphButton").addEventListener("click", drawGraph);
    document.getElementById("uploadDocumentsButton").addEventListener("click", uploadDocuments);
    document.getElementById("uploadCodeButton").addEventListener("click", uploadCode);
    document.getElementById("embedding_mode").addEventListener("change", () => {state.embedding_mode = document.getElementById("embedding_mode").value; state.embedding_mode_changed = true});
});

