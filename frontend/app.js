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

    document.getElementById("editor").classList.remove("hidden");
    document.getElementById("docTitle").innerText = "Editando: " + doc;

    loadLogos();
}

function loadLogos() {
    const container = document.getElementById("logos");
    container.innerHTML = "";

    logos.forEach(logo => {
        const img = document.createElement("img");
        img.src = `http://127.0.0.1:8000/logos/${logo}`;

        img.onclick = () => selectLogo(img, logo);
        container.appendChild(img);
    });
}

function selectLogo(img, logo) {
    selectedLogo = logo;

    document.querySelectorAll(".logos img").forEach(i =>
        i.classList.remove("selected")
    );

    img.classList.add("selected");

    document.getElementById("previewLogo").src =
        `http://127.0.0.1:8000/logos/${logo}`;
}

document.getElementById("footer").addEventListener("input", e => {
    document.getElementById("previewFooter").innerText =
        e.target.value || "Texto del pie";
});

function processDoc() {
    if (!selectedLogo) {
        alert("Selecciona un logo primero");
        return;
    }

    const footer = document.getElementById("footer").value;

    fetch(
        `http://127.0.0.1:8000/process` +
        `?filename=${encodeURIComponent(selectedDoc)}` +
        `&logo=${encodeURIComponent(selectedLogo)}` +
        `&footer_text=${encodeURIComponent(footer)}` +
        `&link=https://example.com`,
        { method: "POST" }
    )
    .then(r => {
        if (!r.ok) throw new Error("Error backend");
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

const positionSelect = document.getElementById("logoPosition");
const sizeInput = document.getElementById("logoSize");

positionSelect.addEventListener("change", updatePreview);
sizeInput.addEventListener("input", updatePreview);

function updatePreview() {
    const header = document.querySelector(".page-header");
    header.className = "page-header " + positionSelect.value;

    const img = document.getElementById("previewLogo");
    img.style.width = `${sizeInput.value * 40}px`;
}
