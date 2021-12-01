from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

doc = DocxTemplate("../documents/HLM-jinja.docx")

context = {
    "nom_bailleur": "3F Construction SA",
    "nom_programme": "Les alouettes",
    "type": "PLAI",
    "nb_logements": "21",
    "financement": "CAF+",
    "adresse": "Avenue du général Toto",
    "code_postal": "13001",
    "ville": "Marseille",
    "image": InlineImage(
        doc, image_descriptor="../documents/Screenshot.png", width=Inches(5)
    ),
    "logements": [
        {"des": "1487 521", "s": 15, "su": 12.45, "p": 1200.0},
        {"des": "1487 522", "s": 15, "su": "13.00", "p": 1200.0},
        {"des": "1487 523", "s": 18, "su": 12.45, "p": 1500.0},
    ],
    "signataire_nom": "Sabine Marini",
    "affiche_tableau": True,
}

doc.render(context)
doc.save("../documents/generated_with_jinja.docx")
