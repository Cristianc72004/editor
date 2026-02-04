let selectedDoc = null;
let selectedLogo = null;

const logos = [
    "logo1.png",
    "logo2.png"
];

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
    document.getElementById("editor").style.display = "block";
    document.getElementById("docTitle").innerText = "Editando: " + doc;
    loadLogos();
}

function loadLogos() {
    const container = document.getElementById("logos");
    container.innerHTML = "";

    logos.forEach(logo => {
        const img = document.createElement("img");
        img.src = `http://127.0.0.1:8000/logos/${logo}`;
        img.style.height = "60px";
        img.style.cursor = "pointer";
        img.style.border = "2px solid transparent";

        img.onclick = () => selectLogo(img, logo);
        container.appendChild(img);
    });
}

function selectLogo(img, logo) {
    selectedLogo = logo;

    document.querySelectorAll("#logos img").forEach(i => {
        i.style.border = "2px solid transparent";
    });

    img.style.border = "2px solid blue";

    document.getElementById("previewLogo").src =
        `http://127.0.0.1:8000/logos/${logo}`;
}

document.getElementById("footer").addEventListener("input", e => {
    document.getElementById("previewFooter").innerText = e.target.value;
});

function processDoc() {
    if (!selectedLogo) {
        alert("Selecciona un logo antes de procesar ❗");
        return;
    }

    const footer = document.getElementById("footer").value;

    fetch(
        `http://127.0.0.1:8000/process?filename=${encodeURIComponent(selectedDoc)}&logo=${encodeURIComponent(selectedLogo)}&footer_text=${encodeURIComponent(footer)}&link=https://example.com`,
        { method: "POST" }
    )
    .then(r => {
        if (!r.ok) throw new Error("Error en backend");
        return r.json();
    })
    .then(() => {
        alert("Documento procesado correctamente ✅");
    })
    .catch(err => {
        console.error(err);
        alert("Error procesando el documento ❌");
    });
}

function previewDoc() {
    const footer = document.getElementById("footer").value;

    const url =
        `http://127.0.0.1:8000/preview` +
        `?filename=${selectedDoc}` +
        `&logo=${selectedLogo}` +
        `&footer_text=${footer}` +
        `&link=https://example.com`;

    document.getElementById("pdfPreview").src = url;
}
