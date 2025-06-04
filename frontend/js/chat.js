const state = {
    requirements: [],
    code_functions: [],
};

async function sendPrompt() {
    const input = document.getElementById('promptInput');
    const message = input.value.trim();
    if (message === "") return;

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
        const response = await fetch('http://127.0.0.1:8000/chat/ask/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: message,
                requirements: state.requirements,
                code_functions: state.code_functions
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
        messages.innerHTML += `<strong>Error:</strong> Could not reach server.`;
        console.error(error);
    }

    input.value = '';
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
        const response = await fetch('http://127.0.0.1:8000/chat/upload/', {
            method: 'POST',
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
        errorMessagesessages.innerHTML += `<div><strong>Error:</strong> Upload failed.</div>`;
        console.error(error);
    } finally {
        loadingIndicator.style.display = 'none';
    }

    input.value = '';
}

async function uploadFilesCode() {
    console.log("uploadFilesCode");

    const input = document.getElementById('uploadInputCode');
    const files = input.files;
    if (files.length === 0) return;

    const formData = new FormData();
    formData.append('type', 'code');

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        formData.append('files', file, file.webkitRelativePath || file.name);
    }

    const errorMessages = document.getElementById('codeUploadErrors');
    errorMessages.innerHTML = ""
    errorMessages.innerHTML += `<div>Uploaded ${files.length} code file(s)</div>`;

    loadingIndicator.style.display = 'flex';
    const messages = document.getElementById('messages');
    try {
        const response = await fetch('http://127.0.0.1:8000/chat/upload/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        messages.innerHTML += `
        <div style="display: flex; justify-content: flex-start;">
            <div class="message bot">Code files received and analyzed.</div>
        </div>`;
        console.log(data);

        state.code_functions = data.code_functions;

    } catch (error) {
        errorMessages.innerHTML += `<div><strong>Error:</strong> Code upload failed.</div>`;
        console.error(error);
    } finally {
        loadingIndicator.style.display = 'none';
    }

    input.value = '';
}