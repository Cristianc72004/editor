let selectedDoc = null;
let selectedLogoLeft = null;
let selectedLogoRight = null;

const logos = [
    "logo1.png",
    "logo2.png",
    "sherpa.png",
    "latindex.png"
];

// ================= DOCUMENTOS =================

function loadDocs() {
    fetch("http://127.0.0.1:8000/documents")
        .then(r => r.json())
        .then(data => {
            const ul = document.getElementById("docs");
            ul.innerHTML = "";

            data.forEach(doc => {
                const li = document.createElement("li");
                li.innerHTML = `
                    ${doc}
                    <button onclick="editDoc('${doc}')">Editar</button>
                `;
                ul.appendChild(li);
            });
        });
}

function editDoc(doc) {
    selectedDoc = doc;
    document.getElementById("editor").classList.remove("hidden");
    document.getElementById("docTitle").innerText = "Editando: " + doc;
    loadLogos();
}

// ================= LOGOS =================

function loadLogos() {
    loadLogoGroup("logosLeft", selectLogoLeft);
    loadLogoGroup("logosRight", selectLogoRight);
}

function loadLogoGroup(containerId, handler) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    logos.forEach(logo => {
        const img = document.createElement("img");
        img.src = `http://127.0.0.1:8000/logos/${logo}`;
        img.onclick = () => handler(img, logo, containerId);
        container.appendChild(img);
    });
}

function selectLogoLeft(img, logo, containerId) {
    selectLogoGeneric(img, containerId);
    selectedLogoLeft = logo;

    document.getElementById("previewLogoLeft").src =
        `http://127.0.0.1:8000/logos/${logo}`;
}

function selectLogoRight(img, logo, containerId) {
    selectLogoGeneric(img, containerId);
    selectedLogoRight = logo;

    document.getElementById("previewLogoRight").src =
        `http://127.0.0.1:8000/logos/${logo}`;
}

function selectLogoGeneric(img, containerId) {
    document
        .querySelectorAll(`#${containerId} img`)
        .forEach(i => i.classList.remove("selected"));

    img.classList.add("selected");
}

// ================= TEXTOS DINÁMICOS =================

document.getElementById("runningAuthor").addEventListener("input", e => {
    document.getElementById("previewRunningAuthor").innerText =
        e.target.value || "Autor";
});

document.getElementById("footer").addEventListener("input", e => {
    document.getElementById("previewFooterLeft").innerText =
        e.target.value || "Texto del pie";
});

// ================= PROCESAR =================

function processDoc() {
    if (!selectedDoc || !selectedLogoLeft) {
        alert("Selecciona un documento y el logo principal");
        return;
    }

    const titleField = document.getElementById("articleTitle");
    const authorsField = document.getElementById("articleAuthors");

    if (!titleField.value || !authorsField.value) {
        alert("El título y los autores son obligatorios");
        return;
    }

    const params = new URLSearchParams({
        filename: selectedDoc,
        logo_left: selectedLogoLeft,
        title: titleField.value,
        authors: authorsField.value,
        running_author: document.getElementById("runningAuthor").value || "",
        footer_text: document.getElementById("footer").value || ""
    });

    if (selectedLogoRight) {
        params.append("logo_right", selectedLogoRight);
    }

    fetch(`http://127.0.0.1:8000/process?${params.toString()}`, {
        method: "POST"
    })
    .then(r => {
        if (!r.ok) throw new Error("Error backend");
        return r.json();
    })
    .then(data => {
        alert("Documento guardado correctamente ✅\n\n" + data.file);
    })
    .catch(err => {
        console.error(err);
        alert("Error procesando el documento ❌");
    });
}
