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

    const prev = document.getElementById("previewLogoLeft");
    if (prev) prev.src = `http://127.0.0.1:8000/logos/${logo}`;
}

function selectLogoRight(img, logo, containerId) {
    selectLogoGeneric(img, containerId);
    selectedLogoRight = logo;

    const prev = document.getElementById("previewLogoRight");
    if (prev) prev.src = `http://127.0.0.1:8000/logos/${logo}`;
}

function selectLogoGeneric(img, containerId) {
    document
        .querySelectorAll(`#${containerId} img`)
        .forEach(i => i.classList.remove("selected"));

    img.classList.add("selected");
}

// ================= TEXTOS DINÁMICOS =================

document.getElementById("runningAuthor")?.addEventListener("input", e => {
    const el = document.getElementById("previewRunningAuthor");
    if (el) el.innerText = e.target.value || "Autor";
});

document.getElementById("footer")?.addEventListener("input", e => {
    const el = document.getElementById("previewFooterLeft");
    if (el) el.innerText = e.target.value || "Texto del pie";
});

document.getElementById("journalName")?.addEventListener("input", e => {
    const el = document.getElementById("previewJournalName");
    if (el) el.innerText = e.target.value || "Green World Journal";
});

document.getElementById("journalISSN")?.addEventListener("input", e => {
    const el = document.getElementById("previewISSN");
    if (el) el.innerText = e.target.value || "ISSN: 2737-6109";
});

// ================= PROCESAR =================

function valNum(id, defVal) {
    const el = document.getElementById(id);
    if (!el) return defVal;
    const v = parseFloat(el.value);
    return Number.isFinite(v) ? v : defVal;
}

function valStr(id, defVal) {
    const el = document.getElementById(id);
    return (el && el.value !== undefined) ? el.value : defVal;
}

function processDoc() {
    if (!selectedDoc || !selectedLogoLeft) {
        alert("Selecciona un documento y el logo principal");
        return;
    }

    const titleField = document.getElementById("articleTitle");
    const authorsField = document.getElementById("articleAuthors");
    const journalName = valStr("journalName", "Green World Journal");
    const issn = valStr("journalISSN", "ISSN: 2737-6109");

    if (!titleField.value || !authorsField.value) {
        alert("El título y los autores son obligatorios");
        return;
    }

    // ===== Lee controles numéricos si los agregaste al HTML =====
    const logo_left_x = valNum("inp_logo_left_x", 0.60);
    const logo_left_y = valNum("inp_logo_left_y", 0.38);
    const logo_left_w = valNum("inp_logo_left_w", 1.20);
    const logo_left_h = document.getElementById("inp_logo_left_h")?.value || "";

    const logo_right_y = valNum("inp_logo_right_y", 0.38);
    const logo_right_w = valNum("inp_logo_right_w", 1.40);
    const logo_right_x = document.getElementById("inp_logo_right_x")?.value || "";
    const logo_right_h = document.getElementById("inp_logo_right_h")?.value || "";

    const title_x = valNum("inp_title_x", 1.35);
    const title_y = valNum("inp_title_y", 0.45);
    const title_w = valNum("inp_title_w", 5.10);
    const title_h = valNum("inp_title_h", 0.70);

    const bar_x = valNum("inp_bar_x", 0.00);
    const bar_y = valNum("inp_bar_y", 1.10);
    const bar_w = valNum("inp_bar_w", 2.3622);
    const bar_h = valNum("inp_bar_h", 0.24);

    const params = new URLSearchParams({
        filename: selectedDoc,
        logo_left: selectedLogoLeft,
        title: titleField.value,
        authors: authorsField.value,
        running_author: valStr("runningAuthor", ""),
        footer_text: valStr("footer", ""),
        journal_name: journalName,
        issn: issn,

        // posiciones
        logo_left_x: String(logo_left_x),
        logo_left_y: String(logo_left_y),
        logo_left_w: String(logo_left_w),

        logo_right_y: String(logo_right_y),
        logo_right_w: String(logo_right_w),

        title_x: String(title_x),
        title_y: String(title_y),
        title_w: String(title_w),
        title_h: String(title_h),

        bar_x: String(bar_x),
        bar_y: String(bar_y),
        bar_w: String(bar_w),
        bar_h: String(bar_h),
    });

    // Opcionales (solo se envían si el input existe y no está vacío)
    if (selectedLogoRight) {
        params.append("logo_right", selectedLogoRight);
    }
    if (logo_right_x !== "") params.append("logo_right_x", logo_right_x);
    if (logo_left_h !== "")  params.append("logo_left_h", logo_left_h);
    if (logo_right_h !== "") params.append("logo_right_h", logo_right_h);

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