const state = {
    requirements: [],
    code_functions: [],
};

async function sendPrompt() {
    const input = document.getElementById('promptInput');
    const message = input.value.trim();
    if (message == "") return;


    const messages = document.getElementById('messages');
    messages.innerHTML += `
    <div style="display: flex; justify-content: flex-end;">
        <div class="message user">${message}</div>
    </div>`;

    try {
        const response = await fetch('http://127.0.0.1:8000/chat/ask/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
                { 
                    prompt: message, 
                    requirements: state.requirements, 
                    code_functions: state.code_functions
                })
        });

        const data = await response.json();
        const markdownHtml = marked.parse(data.reply);

        messages.innerHTML += `
            <div style="display: flex; justify-content: flex-start;">
                <div class="message bot">${markdownHtml}</div>
            </div>`; 
    } catch (error) {
        messages.innerHTML += `<div><strong>Error:</strong> Could not reach server.</div>`;
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

    const messages = document.getElementById('messages');
    messages.innerHTML += `<div><strong>You:</strong> Uploaded ${files.length} file(s)</div>`;

    loadingIndicator.style.display = 'flex';

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
        messages.innerHTML += `<div><strong>Error:</strong> Upload failed.</div>`;
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
        formData.append('files', files[i]);
    }

    const messages = document.getElementById('messages');
    messages.innerHTML += `<div><strong>You:</strong> Uploaded ${files.length} code file(s)</div>`;

    loadingIndicator.style.display = 'flex';

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
        messages.innerHTML += `<div><strong>Error:</strong> Code upload failed.</div>`;
        console.error(error);
    } finally {
        loadingIndicator.style.display = 'none';
    }

    input.value = '';
}